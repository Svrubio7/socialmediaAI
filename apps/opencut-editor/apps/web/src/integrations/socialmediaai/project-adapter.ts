const DEFAULT_BASE_PATH = "/editor";
const DEFAULT_RETURN_TO = "/videos";

export const editorBasePath = (process.env.NEXT_PUBLIC_EDITOR_BASE_PATH || DEFAULT_BASE_PATH).replace(/\/$/, "");

export function buildEditorProjectPath(projectId: string): string {
	const encoded = encodeURIComponent(projectId);
	return `/${encoded}`;
}

function getHostAppOrigin(): string {
	if (typeof window === "undefined") {
		return process.env.NEXT_PUBLIC_HOST_APP_URL || "";
	}
	const hostUrl = process.env.NEXT_PUBLIC_HOST_APP_URL;
	if (hostUrl) {
		return hostUrl;
	}
	const currentPort = window.location.port;
	if (currentPort === "3002") {
		return `${window.location.protocol}//${window.location.hostname}:3000`;
	}
	return "";
}

export function getReturnToPath(): string {
	const hostOrigin = getHostAppOrigin();
	
	if (typeof window === "undefined") {
		const returnPath = process.env.NEXT_PUBLIC_EDITOR_RETURN_TO || DEFAULT_RETURN_TO;
		return hostOrigin ? `${hostOrigin}${returnPath}` : returnPath;
	}
	const value = new URLSearchParams(window.location.search).get("returnTo");
	let returnPath: string;
	if (!value || !value.startsWith("/")) {
		returnPath = process.env.NEXT_PUBLIC_EDITOR_RETURN_TO || DEFAULT_RETURN_TO;
	} else {
		returnPath = value;
	}
	return hostOrigin ? `${hostOrigin}${returnPath}` : returnPath;
}

/** Path to the editor's projects list (used when exiting a project). */
export function getEditorProjectsPath(): string {
	return `${editorBasePath}/projects`;
}
