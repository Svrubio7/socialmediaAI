import Script from "next/script";
import "./globals.css";
import "./host-theme.css";
import { Toaster } from "../components/ui/sonner";
import { TooltipProvider } from "../components/ui/tooltip";
import { ThemeController } from "../components/theme/theme-controller";
import { baseMetaData } from "./metadata";
import { BotIdClient } from "botid/client";
import { webEnv } from "@opencut/env/web";
import { Inter } from "next/font/google";

const siteFont = Inter({ subsets: ["latin"] });

export const metadata = baseMetaData;

const protectedRoutes = [
	{
		path: "/none",
		method: "GET",
	},
];

/**
 * Inline script injected before React hydration to prevent FOUC.
 * Reads 'elevo-theme' from localStorage (shared key with the Nuxt app) and
 * applies the 'dark' class before first paint so the theme matches preference.
 */
const themeInitScript = `(function(){try{var t=localStorage.getItem('elevo-theme');if(t==='light'){document.documentElement.classList.remove('dark')}else if(t==='system'||!t){if(window.matchMedia('(prefers-color-scheme: dark)').matches){document.documentElement.classList.add('dark')}else{document.documentElement.classList.remove('dark')}}else{document.documentElement.classList.add('dark')}}catch(e){}})();`;

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en" suppressHydrationWarning>
			<head>
				{/* FOUC prevention: must run before first paint */}
				{/* biome-ignore lint/security/noDangerouslySetInnerHtml: required for theme FOUC prevention */}
				<script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
				<BotIdClient protect={protectedRoutes} />
			</head>
			<body className={`${siteFont.className} font-sans antialiased`}>
				{/* Mounts cross-tab storage listener and syncs theme state */}
				<ThemeController />
				<TooltipProvider>
					<Toaster />
					<Script
						src="https://cdn.databuddy.cc/databuddy.js"
						strategy="afterInteractive"
						async
						data-client-id="UP-Wcoy5arxFeK7oyjMMZ"
						data-disabled={webEnv.NODE_ENV === "development"}
						data-track-attributes={false}
						data-track-errors={true}
						data-track-outgoing-links={false}
						data-track-web-vitals={false}
						data-track-sessions={false}
					/>
					{children}
				</TooltipProvider>
			</body>
		</html>
	);
}
