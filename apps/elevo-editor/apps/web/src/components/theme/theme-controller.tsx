"use client";

import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * Shared storage key — identical to the Nuxt app's key so both apps stay in sync.
 */
export const ELEVO_THEME_KEY = "elevo-theme";

type ThemePreference = "light" | "dark" | "system";

function resolveTheme(preference: ThemePreference): "light" | "dark" {
	if (preference === "system") {
		return typeof window !== "undefined" &&
			window.matchMedia("(prefers-color-scheme: dark)").matches
			? "dark"
			: "light";
	}
	return preference;
}

function applyTheme(theme: "light" | "dark") {
	if (typeof document === "undefined") return;
	if (theme === "dark") {
		document.documentElement.classList.add("dark");
	} else {
		document.documentElement.classList.remove("dark");
	}
}

function readPreference(): ThemePreference {
	try {
		const stored = localStorage.getItem(ELEVO_THEME_KEY);
		if (stored === "light" || stored === "dark" || stored === "system") {
			return stored;
		}
	} catch {
		/* ignore */
	}
	// Default: follow system preference
	return "system";
}

/**
 * ThemeController — mounts invisibly in the root layout.
 *
 * Responsibilities:
 * - Re-applies the persisted theme on client mount (covers SSR hydration).
 * - Listens for the 'storage' event so theme changes in the Nuxt app (or any
 *   other tab) are reflected immediately without a reload.
 * - Listens for OS-level prefers-color-scheme changes when preference is 'system'.
 */
export function ThemeController() {
	useEffect(() => {
		// Apply on mount (handles any hydration delta)
		applyTheme(resolveTheme(readPreference()));

		// Cross-tab / cross-app sync
		const handleStorage = (e: StorageEvent) => {
			if (e.key !== ELEVO_THEME_KEY) return;
			const pref = (e.newValue ?? "system") as ThemePreference;
			applyTheme(resolveTheme(pref));
		};
		window.addEventListener("storage", handleStorage);

		// OS preference change listener (active when user selected "system")
		const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
		const handleMedia = () => {
			if (readPreference() === "system") {
				applyTheme(resolveTheme("system"));
			}
		};
		mediaQuery.addEventListener("change", handleMedia);

		return () => {
			window.removeEventListener("storage", handleStorage);
			mediaQuery.removeEventListener("change", handleMedia);
		};
	}, []);

	return null;
}

/**
 * ThemeToggleButton — a standalone icon button that cycles light ↔ dark.
 * Writes to localStorage using the shared key so both apps stay in sync.
 * Accepts an optional className for positioning in various headers.
 */
export function ThemeToggleButton({ className }: { className?: string }) {
	const [isDark, setIsDark] = useState(true);

	useEffect(() => {
		const pref = readPreference();
		setIsDark(resolveTheme(pref) === "dark");

		// Keep button state in sync with cross-tab changes
		const handleStorage = (e: StorageEvent) => {
			if (e.key !== ELEVO_THEME_KEY) return;
			const pref = (e.newValue ?? "system") as ThemePreference;
			setIsDark(resolveTheme(pref) === "dark");
		};
		window.addEventListener("storage", handleStorage);
		return () => window.removeEventListener("storage", handleStorage);
	}, []);

	const toggle = () => {
		const next: ThemePreference = isDark ? "light" : "dark";
		try {
			localStorage.setItem(ELEVO_THEME_KEY, next);
		} catch {
			/* ignore */
		}
		applyTheme(next);
		setIsDark(next === "dark");

		// Notify other tabs/windows
		window.dispatchEvent(
			new StorageEvent("storage", {
				key: ELEVO_THEME_KEY,
				newValue: next,
				storageArea: localStorage,
			}),
		);
	};

	return (
		<Button
			variant="ghost"
			size="icon"
			onClick={toggle}
			className={className}
			aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
		>
			{isDark ? <Sun className="size-4" /> : <Moon className="size-4" />}
		</Button>
	);
}
