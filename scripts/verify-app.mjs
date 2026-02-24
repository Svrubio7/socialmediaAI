#!/usr/bin/env node

const appBaseUrl = (process.env.VERIFY_APP_BASE_URL || "http://127.0.0.1:3000").replace(/\/$/, "");
const apiBaseUrl = `${appBaseUrl}/api/v1`;

/** @type {Array<{name: string, ok: boolean, detail: string}>} */
const results = [];

const print = (line = "") => process.stdout.write(`${line}\n`);

const randomId = () => `${Date.now()}_${Math.random().toString(16).slice(2)}`;

async function readJson(response) {
	const text = await response.text();
	if (!text) return {};
	try {
		return JSON.parse(text);
	} catch {
		return { raw: text };
	}
}

function ensureStatus(response, allowed, label) {
	if (!allowed.includes(response.status)) {
		throw new Error(`${label} expected [${allowed.join(", ")}], got ${response.status}`);
	}
}

async function runCheck(name, fn) {
	try {
		const detail = await fn();
		results.push({ name, ok: true, detail: detail || "ok" });
		print(`PASS  ${name}  ${detail || ""}`.trimEnd());
	} catch (error) {
		const detail = error instanceof Error ? error.message : String(error);
		results.push({ name, ok: false, detail });
		print(`FAIL  ${name}  ${detail}`);
	}
}

async function run() {
	print(`Verifying unified app at ${appBaseUrl}`);

	/** @type {string | undefined} */
	let token;
	/** @type {string | undefined} */
	let projectId;
	/** @type {number} */
	let projectRevision = 0;

	await runCheck("route./", async () => {
		const response = await fetch(`${appBaseUrl}/`, { redirect: "manual" });
		ensureStatus(response, [200], "GET /");
		return `status=${response.status}`;
	});

	await runCheck("route./editor", async () => {
		const response = await fetch(`${appBaseUrl}/editor`, { redirect: "manual" });
		ensureStatus(response, [200, 301, 302, 303, 307, 308], "GET /editor");
		return `status=${response.status}`;
	});

	await runCheck("route./api/health", async () => {
		const response = await fetch(`${appBaseUrl}/api/health`, { redirect: "manual" });
		ensureStatus(response, [200], "GET /api/health");
		return `status=${response.status}`;
	});

	await runCheck("auth.register+whoami", async () => {
		const email = `verify_${randomId()}@example.com`;
		const registerResponse = await fetch(`${apiBaseUrl}/auth/register`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				email,
				password: "verify-password-123",
				name: "Verify User",
			}),
			redirect: "manual",
		});
		ensureStatus(registerResponse, [200], "POST /auth/register");
		const registerPayload = await readJson(registerResponse);
		token = registerPayload.access_token;
		if (!token) {
			throw new Error("register response missing access_token");
		}

		const meResponse = await fetch(`${apiBaseUrl}/auth/me`, {
			headers: { Authorization: `Bearer ${token}` },
			redirect: "manual",
		});
		ensureStatus(meResponse, [200], "GET /auth/me");
		const mePayload = await readJson(meResponse);
		if (!mePayload.id || !mePayload.email) {
			throw new Error("auth/me response missing id/email");
		}
		return `user=${mePayload.id}`;
	});

	await runCheck("auth.unauthorized-negative", async () => {
		const response = await fetch(`${apiBaseUrl}/projects`, { redirect: "manual" });
		ensureStatus(response, [401, 403], "GET /projects without auth");
		return `status=${response.status}`;
	});

	await runCheck("project.create-save-load", async () => {
		if (!token) throw new Error("missing auth token");
		const createResponse = await fetch(`${apiBaseUrl}/projects`, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				name: `verify-opencut-${randomId()}`,
				editor_engine: "opencut",
			}),
			redirect: "manual",
		});
		ensureStatus(createResponse, [201], "POST /projects");
		const created = await readJson(createResponse);
		projectId = created.id;
		projectRevision = Number(created.revision || 0);
		if (!projectId) {
			throw new Error("project create response missing id");
		}

		const marker = randomId();
		const patchResponse = await fetch(`${apiBaseUrl}/projects/${projectId}`, {
			method: "PATCH",
			headers: {
				Authorization: `Bearer ${token}`,
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				revision: projectRevision,
				editor_engine: "opencut",
				schema_version: 6,
				state: {
					version: 6,
					metadata: {
						id: projectId,
						name: "verify-project",
						duration: 0,
						createdAt: new Date().toISOString(),
						updatedAt: new Date().toISOString(),
					},
					scenes: [],
					currentSceneId: "scene_main",
					settings: {
						fps: 30,
						canvasSize: { width: 1080, height: 1920 },
						background: { type: "color", color: "#000000" },
					},
					timelineViewState: { zoomLevel: 1, scrollLeft: 0, playheadTime: 0 },
					verification: { marker },
				},
			}),
			redirect: "manual",
		});
		ensureStatus(patchResponse, [200], "PATCH /projects/{id}");
		const patched = await readJson(patchResponse);
		projectRevision = Number(patched.revision || projectRevision);

		const loadResponse = await fetch(`${apiBaseUrl}/projects/${projectId}`, {
			headers: { Authorization: `Bearer ${token}` },
			redirect: "manual",
		});
		ensureStatus(loadResponse, [200], "GET /projects/{id}");
		const loaded = await readJson(loadResponse);
		if (loaded?.state?.verification?.marker !== marker) {
			throw new Error("loaded project state does not match saved marker");
		}
		return `project=${projectId}`;
	});

	await runCheck("route./editor/{projectId}", async () => {
		if (!projectId) throw new Error("missing project id");
		const response = await fetch(`${appBaseUrl}/editor/${projectId}`, { redirect: "manual" });
		ensureStatus(response, [200, 301, 302, 303, 307, 308], "GET /editor/{projectId}");
		return `status=${response.status}`;
	});

	await runCheck("signed-upload.create-upload-playable-url", async () => {
		if (!token || !projectId) throw new Error("missing auth context");
		const assetId = `verify_asset_${randomId()}`;

		const signedResponse = await fetch(`${apiBaseUrl}/projects/${projectId}/assets/signed-upload-url`, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				kind: "video",
				filename: "verify-upload.mp4",
				content_type: "video/mp4",
				asset_id: assetId,
				upsert: true,
			}),
			redirect: "manual",
		});
		ensureStatus(signedResponse, [201], "POST /assets/signed-upload-url");
		const signedPayload = await readJson(signedResponse);
		if (!signedPayload.signed_url || !signedPayload.storage_path) {
			throw new Error("signed upload response missing signed_url/storage_path");
		}

		const minimalMp4 = new Uint8Array([
			0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,
			0x69, 0x73, 0x6f, 0x6d, 0x00, 0x00, 0x02, 0x00,
		]);

		const uploadResponse = await fetch(signedPayload.signed_url, {
			method: "PUT",
			headers: {
				"Content-Type": signedPayload.content_type || "video/mp4",
			},
			body: minimalMp4,
			redirect: "manual",
		});
		ensureStatus(uploadResponse, [200, 201, 204], "PUT signed upload URL");

		const registerResponse = await fetch(`${apiBaseUrl}/projects/${projectId}/assets/register`, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				kind: "video",
				storage_path: signedPayload.storage_path,
				filename: "verify-upload.mp4",
				metadata: {
					project_id: projectId,
					opencut_media_id: assetId,
				},
			}),
			redirect: "manual",
		});
		ensureStatus(registerResponse, [201], "POST /assets/register");
		const registerPayload = await readJson(registerResponse);
		if (!registerPayload.id) {
			throw new Error("register response missing video id");
		}

		const mediaResponse = await fetch(`${apiBaseUrl}/videos/media-urls`, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				video_ids: [registerPayload.id],
				include_video: true,
				include_thumbnail: false,
			}),
			redirect: "manual",
		});
		ensureStatus(mediaResponse, [200], "POST /videos/media-urls");
		const mediaPayload = await readJson(mediaResponse);
		const videoUrl = mediaPayload?.items?.[0]?.video_url;
		if (!videoUrl) {
			throw new Error("media-urls response missing playable video_url");
		}

		const playableResponse = await fetch(videoUrl, {
			method: "HEAD",
			headers: { Authorization: `Bearer ${token}` },
			redirect: "manual",
		});
		ensureStatus(playableResponse, [200, 206, 302, 303, 307, 308], "HEAD playable URL");
		return `status=${playableResponse.status}`;
	});

	await runCheck("route./api/metrics-lite", async () => {
		const response = await fetch(`${appBaseUrl}/api/metrics-lite`, { redirect: "manual" });
		ensureStatus(response, [200], "GET /api/metrics-lite");
		const payload = await readJson(response);
		if (!payload || typeof payload !== "object" || !("metrics" in payload)) {
			throw new Error("metrics-lite response missing metrics payload");
		}
		return "metrics payload present";
	});

	print("");
	const passed = results.filter((item) => item.ok).length;
	const failed = results.length - passed;
	print(`Summary: ${passed} passed, ${failed} failed`);

	if (failed > 0) {
		process.exitCode = 1;
	}
}

run().catch((error) => {
	print(`Fatal verify failure: ${error instanceof Error ? error.message : String(error)}`);
	process.exitCode = 1;
});
