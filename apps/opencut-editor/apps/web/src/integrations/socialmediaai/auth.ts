interface StoredSession {
	access_token?: string;
	refresh_token?: string;
	expires_at?: number;
	expires_in?: number;
	user?: {
		id?: string;
	};
	currentSession?: {
		access_token?: string;
		refresh_token?: string;
		expires_at?: number;
		expires_in?: number;
		user?: {
			id?: string;
		};
	};
	expiresAt?: number;
	currentSessionExpiresAt?: number;
	session?: {
		access_token?: string;
		refresh_token?: string;
		expires_at?: number;
		expires_in?: number;
		user?: {
			id?: string;
		};
	};
}

export const getSupabaseUrl = () => process.env.NEXT_PUBLIC_SUPABASE_URL || "";
export const getSupabaseAnonKey = () => process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

const getAuthStorageKey = () => {
	try {
		const url = new URL(getSupabaseUrl());
		const projectRef = url.hostname.split(".")[0];
		return projectRef ? `sb-${projectRef}-auth-token` : "";
	} catch {
		return "";
	}
};

function readStoredSession(): StoredSession | null {
	if (typeof window === "undefined") return null;
	const key = getAuthStorageKey();
	if (!key) return null;

	const raw = window.localStorage.getItem(key);
	if (!raw) return null;

	try {
		const parsed = JSON.parse(raw) as unknown;
		if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
			return parsed as StoredSession;
		}
		if (Array.isArray(parsed) && parsed.length > 0) {
			const first = parsed[0];
			if (first && typeof first === "object") {
				return { currentSession: first as StoredSession["currentSession"] };
			}
			if (typeof parsed[0] === "string" && typeof parsed[1] === "string") {
				return {
					currentSession: {
						access_token: parsed[0],
						refresh_token: parsed[1],
						user:
							parsed.length > 4 && parsed[4] && typeof parsed[4] === "object"
								? ((parsed[4] as { user?: { id?: string } }).user || (parsed[4] as { id?: string }))
								: undefined,
					},
				};
			}
		}
	} catch {
		return null;
	}
	return null;
}

function resolveActiveSession(stored: StoredSession): StoredSession["currentSession"] {
	if (stored.currentSession && typeof stored.currentSession === "object") {
		return stored.currentSession;
	}
	if (stored.session && typeof stored.session === "object") {
		return stored.session;
	}
	return {
		access_token: stored.access_token,
		refresh_token: stored.refresh_token,
		expires_at: stored.expires_at,
		expires_in: stored.expires_in,
		user: stored.user,
	};
}

function shouldRefreshToken(session: StoredSession["currentSession"] | undefined): boolean {
	if (!session?.access_token) return true;
	const now = Math.floor(Date.now() / 1000);
	const expiresAt = Number(session.expires_at || 0);
	if (Number.isFinite(expiresAt) && expiresAt > 0) {
		return now >= expiresAt - 30;
	}
	return false;
}

function writeUpdatedSession(updatedSession: {
	access_token?: string;
	refresh_token?: string;
	expires_at?: number;
	expires_in?: number;
	user?: { id?: string };
}): void {
	if (typeof window === "undefined") return;
	const key = getAuthStorageKey();
	if (!key) return;

	const current = readStoredSession() || {};
	const next: StoredSession = {
		...current,
		access_token: updatedSession.access_token || current.access_token,
		refresh_token: updatedSession.refresh_token || current.refresh_token,
		expires_at:
			typeof updatedSession.expires_at === "number"
				? updatedSession.expires_at
				: current.expires_at,
		expires_in:
			typeof updatedSession.expires_in === "number"
				? updatedSession.expires_in
				: current.expires_in,
		user: updatedSession.user || current.user,
		currentSession: {
			...(current.currentSession || {}),
			access_token: updatedSession.access_token || current.currentSession?.access_token,
			refresh_token: updatedSession.refresh_token || current.currentSession?.refresh_token,
			expires_at:
				typeof updatedSession.expires_at === "number"
					? updatedSession.expires_at
					: current.currentSession?.expires_at,
			expires_in:
				typeof updatedSession.expires_in === "number"
					? updatedSession.expires_in
					: current.currentSession?.expires_in,
			user: updatedSession.user || current.currentSession?.user,
		},
	};

	try {
		window.localStorage.setItem(key, JSON.stringify(next));
	} catch {
		// Ignore storage write errors; existing session remains usable.
	}
}

async function refreshAccessToken(
	session: StoredSession["currentSession"],
): Promise<string | null> {
	const refreshToken = session?.refresh_token;
	if (!refreshToken || !isSupabaseConfigured()) return null;

	try {
		const response = await fetch(
			`${getSupabaseUrl().replace(/\/$/, "")}/auth/v1/token?grant_type=refresh_token`,
			{
				method: "POST",
				headers: {
					apikey: getSupabaseAnonKey(),
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ refresh_token: refreshToken }),
				cache: "no-store",
			},
		);
		if (!response.ok) return null;
		const payload = (await response.json()) as {
			access_token?: string;
			refresh_token?: string;
			expires_at?: number;
			expires_in?: number;
			user?: { id?: string };
		};
		if (!payload.access_token) return null;
		writeUpdatedSession(payload);
		return payload.access_token;
	} catch {
		return null;
	}
}

export function isSupabaseConfigured(): boolean {
	return Boolean(getSupabaseUrl() && getSupabaseAnonKey());
}

export async function getAccessToken(forceRefresh = false): Promise<string | null> {
	const stored = readStoredSession();
	if (!stored) return null;
	const session = resolveActiveSession(stored);
	if (!session) return null;

	if (forceRefresh || shouldRefreshToken(session)) {
		const refreshed = await refreshAccessToken(session);
		if (refreshed) return refreshed;
	}

	return session.access_token || null;
}

export async function getSessionUserId(): Promise<string | null> {
	const stored = readStoredSession();
	if (!stored) return null;
	const session = resolveActiveSession(stored);
	return session?.user?.id || stored.user?.id || null;
}
