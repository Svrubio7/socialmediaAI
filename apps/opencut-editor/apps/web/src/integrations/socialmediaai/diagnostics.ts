export type SaveState = "idle" | "saving" | "saved" | "error";

export interface ConnectivityEvent {
	at: number;
	method: string;
	path: string;
	status: number;
	requestId?: string;
	error?: string;
}

export interface TimingEvent {
	at: number;
	name: string;
	durationMs: number;
	details?: Record<string, unknown>;
}

export interface SocialMediaAiDiagnosticsState {
	projectId?: string;
	userId?: string;
	saveState: SaveState;
	lastSaveAt?: number;
	urlMode: "signed" | "public" | "proxy" | "unknown";
	recentEvents: ConnectivityEvent[];
	recentTimings: TimingEvent[];
}

const MAX_EVENTS = 20;
const MAX_TIMINGS = 20;
const CLIENT_METRICS_ENDPOINT = `${(process.env.NEXT_PUBLIC_FASTAPI_URL || "/api/v1").replace(/\/$/, "")}/metrics-lite/client`;

const state: SocialMediaAiDiagnosticsState = {
	saveState: "idle",
	urlMode: "unknown",
	recentEvents: [],
	recentTimings: [],
};

const listeners = new Set<() => void>();

function notify() {
	for (const listener of listeners) {
		listener();
	}
}

export function subscribeDiagnostics(listener: () => void): () => void {
	listeners.add(listener);
	return () => listeners.delete(listener);
}

export function getDiagnosticsState(): SocialMediaAiDiagnosticsState {
	return state;
}

export function setProjectContext(projectId: string) {
	state.projectId = projectId;
	notify();
}

export function setUserContext(userId: string) {
	state.userId = userId;
	notify();
}

export function setSaveState(next: SaveState) {
	state.saveState = next;
	if (next === "saved") {
		state.lastSaveAt = Date.now();
	}
	notify();
}

export function setUrlMode(mode: SocialMediaAiDiagnosticsState["urlMode"]) {
	state.urlMode = mode;
	notify();
}

export function recordApiEvent(event: ConnectivityEvent) {
	state.recentEvents = [event, ...state.recentEvents].slice(0, MAX_EVENTS);
	notify();
}

function emitTimingToBackend(event: TimingEvent) {
	if (typeof window === "undefined") return;
	const payload = JSON.stringify({
		name: event.name,
		duration_ms: event.durationMs,
		metadata: event.details || {},
	});

	try {
		if (typeof navigator.sendBeacon === "function") {
			const blob = new Blob([payload], { type: "application/json" });
			navigator.sendBeacon(CLIENT_METRICS_ENDPOINT, blob);
			return;
		}
	} catch {
		// Fallback to fetch if sendBeacon is unavailable or fails.
	}

	fetch(CLIENT_METRICS_ENDPOINT, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: payload,
		cache: "no-store",
		credentials: "include",
		keepalive: true,
	}).catch(() => {});
}

export function recordTiming(
	name: string,
	durationMs: number,
	details: Record<string, unknown> = {},
) {
	if (!Number.isFinite(durationMs) || durationMs < 0) return;
	const event: TimingEvent = {
		at: Date.now(),
		name,
		durationMs: Number(durationMs.toFixed(2)),
		details,
	};
	state.recentTimings = [event, ...state.recentTimings].slice(0, MAX_TIMINGS);
	notify();
	emitTimingToBackend(event);
}

export function isDiagnosticsEnabled(): boolean {
	if (typeof window === "undefined") return false;
	const flag = String(process.env.NEXT_PUBLIC_EDITOR_DIAGNOSTICS || "").toLowerCase() === "true";
	const queryEnabled = new URLSearchParams(window.location.search).get("diag") === "1";
	return flag || queryEnabled;
}
