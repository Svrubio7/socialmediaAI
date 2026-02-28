import { getAccessToken } from "./auth";
import { recordApiEvent, recordTiming } from "./diagnostics";

export interface ApiErrorPayload {
	detail?: unknown;
	message?: string;
}

export class ApiError extends Error {
	status: number;
	payload: ApiErrorPayload | null;

	constructor({ message, status, payload }: { message: string; status: number; payload: ApiErrorPayload | null }) {
		super(message);
		this.status = status;
		this.payload = payload;
	}
}

const API_BASE_URL = (process.env.NEXT_PUBLIC_FASTAPI_URL || "/api/v1").replace(/\/$/, "");
const REQUEST_TIMEOUT_MS = 20000;
const MAX_RETRIES = 2;
const RETRYABLE_STATUS = new Set([408, 425, 429, 500, 502, 503, 504]);

function buildRequestId() {
	return `oc_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

function ensureBaseUrl() {
	if (!API_BASE_URL) {
		throw new Error("NEXT_PUBLIC_FASTAPI_URL is empty; expected a same-origin path like /api/v1");
	}
}

function wait(ms: number) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchWithTimeout(
	url: string,
	init: RequestInit,
	timeoutMs: number,
): Promise<Response> {
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), timeoutMs);
	try {
		return await fetch(url, { ...init, signal: controller.signal });
	} finally {
		clearTimeout(timer);
	}
}

async function requestJson<T>(
	path: string,
	options: {
		method?: "GET" | "POST" | "PATCH" | "DELETE";
		body?: unknown;
	} = {},
): Promise<T> {
	ensureBaseUrl();
	const method = options.method || "GET";
	let attempt = 0;
	let authRefreshAttempted = false;
	let lastError: ApiError | null = null;

	while (attempt <= MAX_RETRIES) {
		let token = await getAccessToken();
		if (!token && !authRefreshAttempted) {
			token = await getAccessToken(true);
			authRefreshAttempted = true;
		}
		if (!token) {
			throw new ApiError({ message: "Not authenticated", status: 401, payload: null });
		}

		const requestId = buildRequestId();
		const requestStartedAt = Date.now();
		let response: Response | null = null;
		try {
			response = await fetchWithTimeout(
				`${API_BASE_URL}${path}`,
				{
					method,
					headers: {
						Authorization: `Bearer ${token}`,
						"Content-Type": "application/json",
						"X-Request-ID": requestId,
					},
					body: options.body === undefined ? undefined : JSON.stringify(options.body),
					cache: "no-store",
					credentials: "include",
				},
				REQUEST_TIMEOUT_MS,
			);
		} catch (error) {
			const message =
				error instanceof Error ? error.message : "Network error while requesting API";
			lastError = new ApiError({
				message,
				status: 0,
				payload: { message },
			});

			recordApiEvent({
				at: Date.now(),
				method,
				path,
				status: 0,
				requestId,
				error: message,
			});

			if (attempt < MAX_RETRIES) {
				await wait(250 * (attempt + 1));
				attempt += 1;
				continue;
			}
			break;
		}

		let payload: ApiErrorPayload | null = null;
		try {
			payload = (await response.json()) as ApiErrorPayload;
		} catch {
			payload = null;
		}

		const elapsedMs = Date.now() - requestStartedAt;
		recordApiEvent({
			at: Date.now(),
			method,
			path,
			status: response.status,
			requestId,
			error: response.ok ? undefined : String(payload?.detail || payload?.message || "Request failed"),
		});
		if (response.ok) {
			const cleanPath = path.split("?")[0] || path;
			if (/^\/projects\/[^/]+$/.test(cleanPath) && method === "GET") {
				recordTiming("project_load_duration_ms", elapsedMs, { source: "api-client", path: cleanPath });
			}
			if (cleanPath.endsWith("/assets") && method === "GET") {
				recordTiming("asset_list_fetch_duration_ms", elapsedMs, { source: "api-client", path: cleanPath });
			}
			if (cleanPath.endsWith("/assets/signed-upload-url") && method === "POST") {
				recordTiming("signed_url_generation_duration_ms", elapsedMs, {
					source: "api-client",
					path: cleanPath,
				});
			}
		}

		if (response.ok) {
			return (payload || {}) as T;
		}

		if (response.status === 401 && !authRefreshAttempted) {
			const refreshed = await getAccessToken(true);
			authRefreshAttempted = true;
			if (refreshed) {
				attempt += 1;
				continue;
			}
		}

		lastError = new ApiError({
			message: String(payload?.detail || payload?.message || `Request failed with ${response.status}`),
			status: response.status,
			payload,
		});

		if (RETRYABLE_STATUS.has(response.status) && attempt < MAX_RETRIES) {
			await wait(250 * (attempt + 1));
			attempt += 1;
			continue;
		}
		break;
	}

	if (lastError) throw lastError;
	throw new ApiError({
		message: "Request failed with unknown error",
		status: 0,
		payload: null,
	});
}

const toQuery = (params: Record<string, string | number | boolean | undefined>) => {
	const search = new URLSearchParams();
	for (const [key, value] of Object.entries(params)) {
		if (value === undefined || value === null || value === "") continue;
		search.set(key, String(value));
	}
	const encoded = search.toString();
	return encoded ? `?${encoded}` : "";
};

export interface ApiProjectListItem {
	id: string;
	name: string;
	description?: string;
	editor_engine: "legacy" | "elevo-editor";
	schema_version: number;
	revision: number;
	duration?: number;
	thumbnail?: string;
	created_at: string;
	updated_at: string;
}

export interface ApiProjectResponse extends ApiProjectListItem {
	state: Record<string, unknown>;
}

export interface ApiProjectAsset {
	id: string;
	kind: "video" | "image" | "audio";
	filename: string;
	storage_path: string;
	url?: string;
	duration?: number;
	width?: number;
	height?: number;
	metadata?: Record<string, unknown>;
}

export interface ApiProjectAssetSignedUploadResponse {
	bucket: string;
	storage_path: string;
	signed_url: string;
	token?: string;
	content_type: string;
	expires_in: number;
}

export const socialMediaAiApi = {
	getMe: () =>
		requestJson<{ id: string; email: string }>("/auth/me"),

	listProjects: (params: {
		page?: number;
		limit?: number;
		editorEngine?: "legacy" | "elevo-editor";
		sourceVideoId?: string;
	} = {}) =>
		requestJson<{ items: ApiProjectListItem[]; total: number; page: number; limit: number }>(
			`/projects${toQuery({
				page: params.page,
				limit: params.limit,
				editor_engine: params.editorEngine,
				source_video_id: params.sourceVideoId,
			})}`,
		),

	getProject: (projectId: string) =>
		requestJson<ApiProjectResponse>(`/projects/${projectId}`),

	createProject: (payload: {
		name?: string;
		description?: string;
		editor_engine?: "legacy" | "elevo-editor";
	}) => requestJson<ApiProjectResponse>("/projects", { method: "POST", body: payload }),

	updateProject: (
		projectId: string,
		payload: {
			name?: string;
			description?: string;
			state?: Record<string, unknown>;
			schema_version?: number;
			revision?: number;
			editor_engine?: "legacy" | "elevo-editor";
		},
	) => requestJson<ApiProjectResponse>(`/projects/${projectId}`, { method: "PATCH", body: payload }),

	deleteProject: (projectId: string) =>
		requestJson<{ ok: true }>(`/projects/${projectId}`, { method: "DELETE" }),

	listProjectAssets: (projectId: string) =>
		requestJson<{ items: ApiProjectAsset[]; total: number }>(
			`/projects/${projectId}/assets${toQuery({ project_only: true })}`,
		),

	registerProjectAsset: (
		projectId: string,
		payload: {
			kind: "video" | "image" | "audio";
			storage_path: string;
			filename?: string;
			original_filename?: string;
			metadata?: Record<string, unknown>;
			file_size?: number;
			duration?: number;
			width?: number;
			height?: number;
			fps?: number;
			codec?: string;
			bitrate?: number;
		},
	) =>
		requestJson<ApiProjectAsset>(`/projects/${projectId}/assets/register`, {
			method: "POST",
			body: payload,
		}),

	createProjectAssetSignedUploadUrl: (
		projectId: string,
		payload: {
			kind: "video" | "image" | "audio";
			filename: string;
			content_type?: string;
			asset_id?: string;
			upsert?: boolean;
		},
	) =>
		requestJson<ApiProjectAssetSignedUploadResponse>(
			`/projects/${projectId}/assets/signed-upload-url`,
			{
				method: "POST",
				body: payload,
			},
		),

	resolveVideoMediaUrls: (videoIds: string[]) =>
		requestJson<{ items: Array<{ id: string; video_url?: string; thumbnail_url?: string }>; expires_in?: number }>(
			"/videos/media-urls",
			{
				method: "POST",
				body: {
					video_ids: videoIds,
					include_video: true,
					include_thumbnail: true,
				},
			},
		),

	deleteVideo: (videoId: string) =>
		requestJson<{ message?: string }>(`/videos/${videoId}`, { method: "DELETE" }),
};
