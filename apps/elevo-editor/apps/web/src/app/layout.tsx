import Script from "next/script";
import "./globals.css";
import "./host-theme.css";
import { Toaster } from "../components/ui/sonner";
import { TooltipProvider } from "../components/ui/tooltip";
import { ThemeController } from "../components/theme/theme-controller";
import { baseMetaData } from "./metadata";
import { BotIdClient } from "botid/client";
import { webEnv } from "@elevo-editor/env/web";
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

/**
 * Inline script to hydrate auth session from URL params before React renders.
 * In local dev, the Nuxt host app passes access_token/refresh_token as query params
 * because the editor runs on a different port (origin) and can't share localStorage.
 */
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const authHydrateScript = `(function(){try{var p=new URLSearchParams(location.search);var a=p.get('access_token');if(!a)return;var u=${JSON.stringify(supabaseUrl)};if(!u)return;var ref=(new URL(u)).hostname.split('.')[0];var key='sb-'+ref+'-auth-token';var cur={};try{var raw=localStorage.getItem(key);if(raw)cur=JSON.parse(raw)||{};}catch(e){}var s={access_token:a,refresh_token:p.get('refresh_token')||undefined};var next=Object.assign({},cur,s);next.currentSession=Object.assign({},cur.currentSession||{},s);localStorage.setItem(key,JSON.stringify(next));p.delete('access_token');p.delete('refresh_token');var clean=location.pathname+(p.toString()?'?'+p.toString():'');history.replaceState({},'',clean);}catch(e){}})();`;

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
				{/* Auth hydration: store tokens passed via URL from host app (cross-origin dev) */}
				{/* biome-ignore lint/security/noDangerouslySetInnerHtml: required for pre-hydration auth */}
				<script dangerouslySetInnerHTML={{ __html: authHydrateScript }} />
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
