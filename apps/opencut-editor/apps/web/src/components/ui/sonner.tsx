"use client";

import { useEffect, useState } from "react";
import { Toaster as Sonner } from "sonner";
import { ELEVO_THEME_KEY } from "@/components/theme/theme-controller";

type ToasterProps = React.ComponentProps<typeof Sonner>;

const Toaster = ({ ...props }: ToasterProps) => {
	const [theme, setTheme] = useState<"light" | "dark">("dark");

	useEffect(() => {
		// Resolve initial theme from the html element class
		const isDark = document.documentElement.classList.contains("dark");
		setTheme(isDark ? "dark" : "light");

		// Watch for class changes (ThemeController updates the html element)
		const observer = new MutationObserver(() => {
			setTheme(
				document.documentElement.classList.contains("dark") ? "dark" : "light",
			);
		});
		observer.observe(document.documentElement, {
			attributes: true,
			attributeFilter: ["class"],
		});

		// Also sync on cross-tab storage changes
		const handleStorage = (e: StorageEvent) => {
			if (e.key === ELEVO_THEME_KEY) {
				setTheme(e.newValue === "light" ? "light" : "dark");
			}
		};
		window.addEventListener("storage", handleStorage);

		return () => {
			observer.disconnect();
			window.removeEventListener("storage", handleStorage);
		};
	}, []);

	return (
		<Sonner
			theme={theme}
			className="toaster group"
			position="top-center"
			offset={20}
			toastOptions={{
				classNames: {
					toast: "group toast group-[.toaster]:bg-background group-[.toaster]:text-foreground group-[.toaster]:border-border group-[.toaster]:shadow-lg",
					description: "group-[.toast]:text-muted-foreground",
					actionButton:
						"group-[.toast]:bg-primary group-[.toast]:text-primary-foreground",
					cancelButton:
						"group-[.toast]:bg-muted group-[.toast]:text-muted-foreground",
				},
			}}
			expand={false}
			richColors
			{...props}
		/>
	);
};

export { Toaster };
