import type { MediaAsset, MediaType } from "@/types/assets";
import type { TProject, TProjectMetadata } from "@/types/project";
import type { TScene } from "@/types/timeline";
import {
	socialMediaAiApi,
	type ApiError,
	type ApiProjectAsset,
	type ApiProjectAssetSignedUploadResponse,
} from "./api-client";
import {
	getAccessToken,
	getSessionUserId,
	getSupabaseAnonKey,
	getSupabaseUrl,
	isSupabaseConfigured,
} from "./auth";
import {
	recordTiming,
	setProjectContext,
	setSaveState,
	setUrlMode,
	setUserContext,
} from "./diagnostics";

const EDITOR_ENGINE = "opencut" as const;
const SIGNED_URL_TTL_SECONDS = 3600;
const DEFAULT_BUCKET = "videos";
const SUPABASE_FETCH_TIMEOUT_MS = 15000;
const SIGNED_URL_CACHE_TTL_MS = 60000;
const SIGNED_UPLOAD_CACHE_TTL_MS = 45000;
const ASSET_LOAD_CONCURRENCY = 6;

let didPrimeUser = false;
const projectRevisionMap = new Map<string, number>();
const projectAssetMap = new Map<string, Map<string, ApiProjectAsset>>();
const signedUrlCache = new Map<string, { url: string; expiresAt: number }>();
const signedUploadCache = new Map<string, { value: ApiProjectAssetSignedUploadResponse; expiresAt: number }>();

const getBucketName = () =>
	process.env.NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET || DEFAULT_BUCKET;

const encodeStoragePath = (path: string) =>
	path
		.split("/")
		.filter(Boolean)
		.map((segment) => encodeURIComponent(segment))
		.join("/");

const withTimeout = <T>(promise: Promise<T>, timeoutMs: number): Promise<T> =>
	new Promise<T>((resolve, reject) => {
		const timer = setTimeout(() => reject(new Error(`Timed out after ${timeoutMs}ms`)), timeoutMs);
		promise
			.then((value) => {
				clearTimeout(timer);
				resolve(value);
			})
			.catch((error) => {
				clearTimeout(timer);
				reject(error);
			});
	});

async function fetchWithRetry(url: string, init: RequestInit, retries = 1): Promise<Response> {
	let lastError: Error | null = null;
	for (let attempt = 0; attempt <= retries; attempt += 1) {
		try {
			const response = await withTimeout(fetch(url, init), SUPABASE_FETCH_TIMEOUT_MS);
			if (response.ok) {
				return response;
			}
			if (response.status >= 500 && response.status <= 599 && attempt < retries) {
				continue;
			}
			return response;
		} catch (error) {
			lastError = error instanceof Error ? error : new Error("Network request failed");
			if (attempt >= retries) {
				throw lastError;
			}
		}
	}
	throw lastError || new Error("Network request failed");
}

async function mapWithConcurrency<T, R>(
	items: T[],
	limit: number,
	mapper: (item: T) => Promise<R>,
): Promise<R[]> {
	if (!items.length) return [];
	const workerLimit = Math.max(1, Math.min(limit, items.length));
	const results = new Array<R>(items.length);
	let cursor = 0;

	const workers = Array.from({ length: workerLimit }, async () => {
		while (true) {
			const index = cursor;
			cursor += 1;
			if (index >= items.length) return;
			results[index] = await mapper(items[index] as T);
		}
	});

	await Promise.all(workers);
	return results;
}

async function buildStorageAuthHeaders(contentType?: string): Promise<HeadersInit> {
	const token = await getAccessToken();
	if (!token) {
		throw new Error("Missing Supabase access token");
	}
	const headers: HeadersInit = {
		Authorization: `Bearer ${token}`,
		apikey: getSupabaseAnonKey(),
		"x-upsert": "true",
	};
	if (contentType) {
		headers["Content-Type"] = contentType;
	}
	return headers;
}

const toIso = (value: Date | string | undefined) => {
	if (!value) return new Date().toISOString();
	if (value instanceof Date) return value.toISOString();
	const parsed = new Date(value);
	if (Number.isNaN(parsed.getTime())) return new Date().toISOString();
	return parsed.toISOString();
};

const toDate = (value: unknown): Date => {
	if (value instanceof Date) return value;
	if (typeof value === "string" || typeof value === "number") {
		const parsed = new Date(value);
		if (!Number.isNaN(parsed.getTime())) return parsed;
	}
	return new Date();
};

function normalizeScene(raw: unknown, index: number): TScene {
	const scene = (raw || {}) as Record<string, unknown>;
	return {
		id: String(scene.id || `scene_${index + 1}`),
		name: String(scene.name || `Scene ${index + 1}`),
		isMain: Boolean(scene.isMain),
		tracks: (Array.isArray(scene.tracks) ? scene.tracks : []) as TScene["tracks"],
		bookmarks: (Array.isArray(scene.bookmarks) ? scene.bookmarks : []) as TScene["bookmarks"],
		createdAt: toDate(scene.createdAt),
		updatedAt: toDate(scene.updatedAt),
	};
}

function toSerializableProject(project: TProject): Record<string, unknown> {
	return {
		metadata: {
			...project.metadata,
			createdAt: toIso(project.metadata.createdAt),
			updatedAt: toIso(project.metadata.updatedAt),
		},
		scenes: project.scenes.map((scene) => ({
			...scene,
			createdAt: toIso(scene.createdAt),
			updatedAt: toIso(scene.updatedAt),
		})),
		currentSceneId: project.currentSceneId,
		settings: project.settings,
		version: project.version,
		timelineViewState: project.timelineViewState,
	};
}

function fromSerializableProject({
	state,
	fallbackId,
	fallbackName,
}: {
	state: Record<string, unknown>;
	fallbackId: string;
	fallbackName: string;
}): TProject {
	const metadataRaw = (state.metadata || {}) as Record<string, unknown>;
	const scenesRaw = Array.isArray(state.scenes) ? state.scenes : [];

	const scenes = scenesRaw.map((scene, index) => normalizeScene(scene, index));
	const activeSceneId = String(
		state.currentSceneId || scenes[0]?.id || "scene_main",
	);

	return {
		metadata: {
			id: String(metadataRaw.id || fallbackId),
			name: String(metadataRaw.name || fallbackName),
			thumbnail:
				typeof metadataRaw.thumbnail === "string"
					? metadataRaw.thumbnail
					: undefined,
			duration: Number(metadataRaw.duration || 0),
			createdAt: toDate(metadataRaw.createdAt),
			updatedAt: toDate(metadataRaw.updatedAt),
		},
		scenes,
		currentSceneId: activeSceneId,
		settings: (state.settings || {
			fps: 30,
			canvasSize: { width: 1080, height: 1920 },
			background: { type: "color", color: "#000000" },
		}) as TProject["settings"],
		version: Number(state.version || 6),
		timelineViewState: state.timelineViewState as TProject["timelineViewState"],
	};
}

async function ensureUserContext(): Promise<void> {
	if (didPrimeUser) return;
	const me = await socialMediaAiApi.getMe();
	setUserContext(me.id);
	didPrimeUser = true;
}

async function ensureProjectRevision(projectId: string): Promise<number> {
	const cached = projectRevisionMap.get(projectId);
	if (typeof cached === "number") return cached;
	const project = await socialMediaAiApi.getProject(projectId);
	projectRevisionMap.set(projectId, Number(project.revision || 0));
	return Number(project.revision || 0);
}

function inferMediaKind(type: MediaType): "video" | "image" | "audio" {
	if (type === "video") return "video";
	if (type === "audio") return "audio";
	return "image";
}

function inferUrlMode(url?: string): "signed" | "public" | "proxy" | "unknown" {
	if (!url) return "unknown";
	if (url.includes("/stream") || url.includes("/thumbnail")) return "proxy";
	if (url.includes("token=") || url.includes("signature") || url.includes("expires")) return "signed";
	return "public";
}

async function toFile({
	url,
	filename,
	mimeType,
}: {
	url: string;
	filename: string;
	mimeType?: string;
}): Promise<File> {
	const response = await fetch(url, { cache: "no-store" });
	if (!response.ok) {
		throw new Error(`Failed to fetch asset (${response.status})`);
	}
	const blob = await response.blob();
	const type = blob.type || mimeType || "application/octet-stream";
	return new File([blob], filename, { type, lastModified: Date.now() });
}

async function resolveSignedUrl(storagePath: string): Promise<string | undefined> {
	if (!isSupabaseConfigured()) return undefined;
	const cached = signedUrlCache.get(storagePath);
	const now = Date.now();
	if (cached && cached.expiresAt > now) {
		return cached.url;
	}

	const supabaseUrl = getSupabaseUrl();
	const bucket = getBucketName();
	const encodedPath = encodeStoragePath(storagePath);
	const headers = await buildStorageAuthHeaders("application/json");
	const startedAt = typeof performance !== "undefined" ? performance.now() : Date.now();
	const response = await fetchWithRetry(
		`${supabaseUrl}/storage/v1/object/sign/${bucket}/${encodedPath}`,
		{
			method: "POST",
			headers,
			body: JSON.stringify({ expiresIn: SIGNED_URL_TTL_SECONDS }),
			credentials: "include",
			cache: "no-store",
		},
		1,
	);
	const endedAt = typeof performance !== "undefined" ? performance.now() : Date.now();
	recordTiming("signed_url_generation_duration_ms", endedAt - startedAt, {
		source: "storage-adapter",
		storagePath,
	});
	if (!response.ok) return undefined;
	const payload = (await response.json()) as { signedURL?: string; signedUrl?: string; signed_url?: string };
	const relative =
		payload.signedURL || payload.signedUrl || payload.signed_url || "";
	if (!relative) return undefined;
	if (relative.startsWith("http://") || relative.startsWith("https://")) {
		signedUrlCache.set(storagePath, {
			url: relative,
			expiresAt: now + SIGNED_URL_CACHE_TTL_MS,
		});
		return relative;
	}
	const absolute = `${supabaseUrl}${relative.startsWith("/") ? "" : "/"}${relative}`;
	signedUrlCache.set(storagePath, {
		url: absolute,
		expiresAt: now + SIGNED_URL_CACHE_TTL_MS,
	});
	return absolute;
}

function getAssetLookup(projectId: string): Map<string, ApiProjectAsset> {
	if (!projectAssetMap.has(projectId)) {
		projectAssetMap.set(projectId, new Map());
	}
	return projectAssetMap.get(projectId)!;
}

function isApiConflict(error: unknown): error is ApiError {
	return Boolean(error && typeof error === "object" && "status" in error && (error as ApiError).status === 409);
}

async function saveProject(project: TProject): Promise<void> {
	setProjectContext(project.metadata.id);
	setSaveState("saving");
	await ensureUserContext();

	const requestState = toSerializableProject(project);
	const attemptSave = async (revision: number) =>
		socialMediaAiApi.updateProject(project.metadata.id, {
			state: requestState,
			revision,
			schema_version: Number(project.version || 6),
			editor_engine: EDITOR_ENGINE,
		});

	let revision = await ensureProjectRevision(project.metadata.id);
	try {
		const saved = await attemptSave(revision);
		projectRevisionMap.set(project.metadata.id, Number(saved.revision || revision));
		setSaveState("saved");
		return;
	} catch (error) {
		if (!isApiConflict(error)) {
			setSaveState("error");
			throw error;
		}

		const detail = (error.payload?.detail || {}) as Record<string, unknown>;
		const serverRevision = Number(detail.server_revision);
		if (!Number.isFinite(serverRevision)) {
			setSaveState("error");
			throw error;
		}

		revision = serverRevision;
		try {
			const saved = await attemptSave(revision);
			projectRevisionMap.set(project.metadata.id, Number(saved.revision || revision));
			setSaveState("saved");
		} catch (retryError) {
			setSaveState("error");
			throw retryError;
		}
	}
}

async function loadProject(projectId: string): Promise<{ project: TProject } | null> {
	setProjectContext(projectId);
	await ensureUserContext();
	const payload = await socialMediaAiApi.getProject(projectId);
	projectRevisionMap.set(projectId, Number(payload.revision || 0));
	return {
		project: fromSerializableProject({
			state: payload.state || {},
			fallbackId: payload.id,
			fallbackName: payload.name,
		}),
	};
}

async function loadAllProjectsMetadata(): Promise<TProjectMetadata[]> {
	await ensureUserContext();
	const payload = await socialMediaAiApi.listProjects({ limit: 100, editorEngine: EDITOR_ENGINE });
	return payload.items.map((item) => ({
		id: item.id,
		name: item.name,
		duration: Number(item.duration || 0),
		thumbnail: typeof item.thumbnail === "string" ? item.thumbnail : undefined,
		createdAt: new Date(item.created_at),
		updatedAt: new Date(item.updated_at),
	}));
}

async function createProject(name: string): Promise<string> {
	await ensureUserContext();
	const created = await socialMediaAiApi.createProject({
		name,
		editor_engine: EDITOR_ENGINE,
	});
	projectRevisionMap.set(created.id, Number(created.revision || 0));
	setProjectContext(created.id);
	return created.id;
}

async function deleteProject(projectId: string): Promise<void> {
	await socialMediaAiApi.deleteProject(projectId);
	projectRevisionMap.delete(projectId);
	projectAssetMap.delete(projectId);
}

async function saveMediaAsset({
	projectId,
	mediaAsset,
}: {
	projectId: string;
	mediaAsset: MediaAsset;
}): Promise<void> {
	await ensureUserContext();
	if (!isSupabaseConfigured()) {
		throw new Error("Supabase is not configured for host mode");
	}

	const filename = mediaAsset.file.name || `${mediaAsset.id}`;
	let storagePath = "";
	try {
		const cacheKey = `${projectId}:${mediaAsset.id}:${filename}:${mediaAsset.file.type || "application/octet-stream"}`;
		let signedUpload = signedUploadCache.get(cacheKey)?.value;
		const now = Date.now();
		if (!signedUpload || (signedUploadCache.get(cacheKey)?.expiresAt || 0) <= now) {
			const signedUploadStarted = typeof performance !== "undefined" ? performance.now() : Date.now();
			signedUpload = await socialMediaAiApi.createProjectAssetSignedUploadUrl(
				projectId,
				{
					kind: inferMediaKind(mediaAsset.type),
					filename,
					content_type: mediaAsset.file.type || "application/octet-stream",
					asset_id: mediaAsset.id,
					upsert: true,
				},
			);
			const signedUploadEnded = typeof performance !== "undefined" ? performance.now() : Date.now();
			recordTiming("signed_url_generation_duration_ms", signedUploadEnded - signedUploadStarted, {
				source: "save-media-asset",
				projectId,
			});
			const ttlMs = Math.min(
				Math.max(5000, Number(signedUpload.expires_in || 0) * 1000),
				SIGNED_UPLOAD_CACHE_TTL_MS,
			);
			signedUploadCache.set(cacheKey, { value: signedUpload, expiresAt: now + ttlMs });
		}

		storagePath = signedUpload.storage_path;
		const uploadResponse = await fetchWithRetry(
			signedUpload.signed_url,
			{
				method: "PUT",
				headers: {
					"Content-Type":
						mediaAsset.file.type ||
						signedUpload.content_type ||
						"application/octet-stream",
				},
				body: mediaAsset.file,
				cache: "no-store",
			},
			1,
		);
		if (!uploadResponse.ok) {
			throw new Error(`Failed to upload media asset (${uploadResponse.status})`);
		}
	} catch {
		// Fallback for environments where signed upload issuance is unavailable.
		const userId = await getSessionUserId();
		if (!userId) {
			throw new Error("Not authenticated");
		}
		storagePath = `editor/assets/${userId}/${projectId}/${mediaAsset.id}/${filename}`;
		const bucket = getBucketName();
		const supabaseUrl = getSupabaseUrl();
		const encodedPath = encodeStoragePath(storagePath);
		const uploadHeaders = await buildStorageAuthHeaders(
			mediaAsset.file.type || undefined,
		);
		const uploadResponse = await fetchWithRetry(
			`${supabaseUrl}/storage/v1/object/${bucket}/${encodedPath}`,
			{
				method: "POST",
				headers: uploadHeaders,
				body: mediaAsset.file,
				cache: "no-store",
			},
			1,
		);
		if (!uploadResponse.ok) {
			throw new Error(`Failed to upload media asset (${uploadResponse.status})`);
		}
	}

	const registered = await socialMediaAiApi.registerProjectAsset(projectId, {
		kind: inferMediaKind(mediaAsset.type),
		storage_path: storagePath,
		filename: mediaAsset.name,
		original_filename: filename,
		file_size: mediaAsset.file.size,
		duration: mediaAsset.duration,
		width: mediaAsset.width,
		height: mediaAsset.height,
		metadata: {
			project_id: projectId,
			opencut_media_id: mediaAsset.id,
			mime_type: mediaAsset.file.type,
		},
	});

	getAssetLookup(projectId).set(mediaAsset.id, registered);
}

async function loadAllMediaAssets({ projectId }: { projectId: string }): Promise<MediaAsset[]> {
	const startedAt = typeof performance !== "undefined" ? performance.now() : Date.now();
	await ensureUserContext();
	const payload = await socialMediaAiApi.listProjectAssets(projectId);
	const scopedItems = payload.items.filter((item) => {
		const metadata = (item.metadata || {}) as Record<string, unknown>;
		return String(metadata.project_id || "") === projectId;
	});

	const remoteByMediaId = getAssetLookup(projectId);
	remoteByMediaId.clear();

	const videoItems = scopedItems.filter((item) => item.kind === "video");
	const videoIds = videoItems.map((item) => item.id);
	const videoUrlMap = new Map<string, { video_url?: string; thumbnail_url?: string }>();
	if (videoIds.length > 0) {
		const resolved = await socialMediaAiApi.resolveVideoMediaUrls(videoIds);
		for (const item of resolved.items) {
			videoUrlMap.set(item.id, {
				video_url: item.video_url,
				thumbnail_url: item.thumbnail_url,
			});
		}
	}

	const loaded = await mapWithConcurrency(scopedItems, ASSET_LOAD_CONCURRENCY, async (item) => {
		const metadata = (item.metadata || {}) as Record<string, unknown>;
		const mediaId = String(metadata.opencut_media_id || item.id);
		remoteByMediaId.set(mediaId, item);

		let sourceUrl: string | undefined;
		let thumbnailUrl: string | undefined;
		if (item.kind === "video") {
			const media = videoUrlMap.get(item.id);
			sourceUrl = media?.video_url || item.url;
			thumbnailUrl = media?.thumbnail_url;
		} else {
			sourceUrl = item.url || (await resolveSignedUrl(item.storage_path));
		}

		if (!sourceUrl) {
			return null;
		}

		setUrlMode(inferUrlMode(sourceUrl));

		let file: File;
		try {
			file = await toFile({
				url: sourceUrl,
				filename: item.filename,
				mimeType: typeof metadata.mime_type === "string" ? metadata.mime_type : undefined,
			});
		} catch {
			file = new File([new Blob()], item.filename, {
				type:
					typeof metadata.mime_type === "string"
						? metadata.mime_type
						: "application/octet-stream",
				lastModified: Date.now(),
			});
		}

		return {
			id: mediaId,
			name: item.filename,
			type: item.kind as MediaType,
			file,
			url: URL.createObjectURL(file),
			thumbnailUrl,
			width: item.width,
			height: item.height,
			duration: item.duration,
		};
	});

	const endedAt = typeof performance !== "undefined" ? performance.now() : Date.now();
	recordTiming("asset_list_fetch_duration_ms", endedAt - startedAt, {
		source: "storage-adapter",
		projectId,
		assets: scopedItems.length,
	});
	return loaded.filter((item) => item !== null) as MediaAsset[];
}

async function deleteMediaAsset({ projectId, id }: { projectId: string; id: string }): Promise<void> {
	const lookup = getAssetLookup(projectId);
	const record = lookup.get(id);
	if (!record) {
		return;
	}

	if (record.kind === "video") {
		await socialMediaAiApi.deleteVideo(record.id);
		lookup.delete(id);
		return;
	}

	if (isSupabaseConfigured()) {
		const token = await getAccessToken();
		if (token) {
			const supabaseUrl = getSupabaseUrl();
			const bucket = getBucketName();
			const encodedPath = encodeStoragePath(record.storage_path);
			await fetch(`${supabaseUrl}/storage/v1/object/${bucket}/${encodedPath}`, {
				method: "DELETE",
				headers: {
					Authorization: `Bearer ${token}`,
					apikey: getSupabaseAnonKey(),
				},
			});
		}
	}
	lookup.delete(id);
}

async function deleteProjectMedia({ projectId }: { projectId: string }): Promise<void> {
	const lookup = getAssetLookup(projectId);
	const ids = Array.from(lookup.keys());
	for (const mediaId of ids) {
		await deleteMediaAsset({ projectId, id: mediaId });
	}
	lookup.clear();
}

export const socialMediaAiStorageAdapter = {
	isEnabled: () => Boolean(process.env.NEXT_PUBLIC_FASTAPI_URL),
	createProject,
	saveProject,
	loadProject,
	loadAllProjectsMetadata,
	deleteProject,
	saveMediaAsset,
	loadAllMediaAssets,
	deleteMediaAsset,
	deleteProjectMedia,
};
