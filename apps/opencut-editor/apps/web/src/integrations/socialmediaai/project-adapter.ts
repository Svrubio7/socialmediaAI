const DEFAULT_BASE_PATH = "/editor";
const DEFAULT_RETURN_TO = "/editor";

export const editorBasePath = (process.env.NEXT_PUBLIC_EDITOR_BASE_PATH || DEFAULT_BASE_PATH).replace(/\/$/, "");

export function buildEditorProjectPath(projectId: string): string {
	const encoded = encodeURIComponent(projectId);
	return `/${encoded}`;
}

export function getReturnToPath(): string {
	if (typeof window === "undefined") {
		return process.env.NEXT_PUBLIC_EDITOR_RETURN_TO || DEFAULT_RETURN_TO;
	}
	const value = new URLSearchParams(window.location.search).get("returnTo");
	if (!value) {
		return process.env.NEXT_PUBLIC_EDITOR_RETURN_TO || DEFAULT_RETURN_TO;
	}
	if (!value.startsWith("/")) {
		return process.env.NEXT_PUBLIC_EDITOR_RETURN_TO || DEFAULT_RETURN_TO;
	}
	return value;
}
