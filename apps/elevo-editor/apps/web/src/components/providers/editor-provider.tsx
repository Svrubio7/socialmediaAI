"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import Image from "next/image";
import { useEditor } from "@/hooks/use-editor";
import {
	useKeybindingsListener,
	useKeybindingDisabler,
} from "@/hooks/use-keybindings";
import { useEditorActions } from "@/hooks/actions/use-editor-actions";
import { prefetchFontAtlas } from "@/lib/fonts/google-fonts";
import { getReturnToPath, getHostLoginUrl } from "@/integrations/socialmediaai/project-adapter";
import { hydrateSessionFromUrl } from "@/integrations/socialmediaai/auth";
import { recordTiming } from "@/integrations/socialmediaai/diagnostics";
import { DEFAULT_LOGO_URL } from "@/constants/site-constants";

interface EditorProviderProps {
	projectId: string;
	children: React.ReactNode;
}

function isAuthError(err: unknown): boolean {
	if (!err || typeof err !== "object") return false;
	if ("status" in err && Number((err as { status?: unknown }).status) === 401) {
		return true;
	}
	if ("message" in err) {
		const message = String((err as { message?: unknown }).message || "").toLowerCase();
		return (
			message.includes("not authenticated") ||
			message.includes("unauthorized") ||
			message.includes("forbidden")
		);
	}
	return false;
}

function navigateToLogin(_router: ReturnType<typeof useRouter>) {
	const loginUrl = getHostLoginUrl();
	if (typeof window !== "undefined") {
		window.location.assign(loginUrl);
		return;
	}
}

export function EditorProvider({ projectId, children }: EditorProviderProps) {
	const editor = useEditor();
	const router = useRouter();
	const [isLoading, setIsLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const { disableKeybindings, enableKeybindings } = useKeybindingDisabler();
	const activeProject = editor.project.getActiveOrNull();

	useEffect(() => {
		if (isLoading) {
			disableKeybindings();
		} else {
			enableKeybindings();
		}
	}, [isLoading, disableKeybindings, enableKeybindings]);

	useEffect(() => {
		let cancelled = false;
		const bootStartedAt =
			typeof performance !== "undefined" ? performance.now() : Date.now();

		const loadProject = async () => {
			try {
				setIsLoading(true);
				// In dev, tokens are passed via URL from the Nuxt host app (cross-origin)
				hydrateSessionFromUrl();
				await editor.project.loadProject({ id: projectId });

				if (cancelled) return;

				setIsLoading(false);
				prefetchFontAtlas();
				const endedAt =
					typeof performance !== "undefined" ? performance.now() : Date.now();
				const durationMs = endedAt - bootStartedAt;
				recordTiming("project_load_duration_ms", durationMs, { projectId, source: "editor-provider" });
				recordTiming("editor_boot_to_interactive_ms", durationMs, {
					projectId,
					source: "editor-provider",
				});
			} catch (err) {
				if (cancelled) return;
				if (isAuthError(err)) {
					navigateToLogin(router);
					return;
				}

				const isNotFound =
					err instanceof Error &&
					(err.message.includes("not found") ||
						err.message.includes("does not exist"));

				if (isNotFound) {
					if (typeof window !== "undefined") {
						window.location.assign(getReturnToPath());
					} else {
						router.replace(getReturnToPath());
					}
					return;
				} else {
					setError(
						err instanceof Error ? err.message : "Failed to load project",
					);
					setIsLoading(false);
				}
			}
		};

		loadProject();

		return () => {
			cancelled = true;
		};
	}, [projectId, editor, router]);

	if (error) {
		return (
			<div className="bg-background flex h-screen w-screen items-center justify-center">
				<div className="flex flex-col items-center gap-4">
					<Image
						src={DEFAULT_LOGO_URL}
						alt="Elevo logo"
						width={56}
						height={56}
						className="size-14"
						priority
					/>
					<p className="text-destructive text-sm">{error}</p>
				</div>
			</div>
		);
	}

	if (isLoading) {
		return (
			<div className="bg-background flex h-screen w-screen items-center justify-center">
				<div className="flex flex-col items-center gap-4">
					<Image
						src={DEFAULT_LOGO_URL}
						alt="Elevo logo"
						width={56}
						height={56}
						className="size-14"
						priority
					/>
					<Loader2 className="text-muted-foreground size-8 animate-spin" />
					<p className="text-muted-foreground text-sm">Loading project...</p>
				</div>
			</div>
		);
	}

	if (!activeProject) {
		return (
			<div className="bg-background flex h-screen w-screen items-center justify-center">
				<div className="flex flex-col items-center gap-4">
					<Image
						src={DEFAULT_LOGO_URL}
						alt="Elevo logo"
						width={56}
						height={56}
						className="size-14"
						priority
					/>
					<Loader2 className="text-muted-foreground size-8 animate-spin" />
					<p className="text-muted-foreground text-sm">Exiting project...</p>
				</div>
			</div>
		);
	}

	return (
		<>
			<EditorRuntimeBindings />
			{children}
		</>
	);
}

function EditorRuntimeBindings() {
	const editor = useEditor();

	useEffect(() => {
		const handleBeforeUnload = (event: BeforeUnloadEvent) => {
			if (!editor.save.getIsDirty()) return;
			event.preventDefault();
			(event as unknown as { returnValue: string }).returnValue = "";
		};

		window.addEventListener("beforeunload", handleBeforeUnload);
		return () => window.removeEventListener("beforeunload", handleBeforeUnload);
	}, [editor]);

	useEditorActions();
	useKeybindingsListener();
	return null;
}
