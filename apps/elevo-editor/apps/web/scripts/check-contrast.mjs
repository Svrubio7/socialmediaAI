#!/usr/bin/env node
/*
 * WCAG contrast checker for Elevo theme tokens (light + dark).
 * Fails when any text pair is < 4.5:1 or any UI boundary/icon pair is < 3:1.
 */

function hexToRgb(hex) {
	const value = hex.replace("#", "");
	if (!/^[0-9a-fA-F]{6}$/.test(value)) {
		throw new Error(`Invalid hex color: ${hex}`);
	}

	return {
		r: Number.parseInt(value.slice(0, 2), 16),
		g: Number.parseInt(value.slice(2, 4), 16),
		b: Number.parseInt(value.slice(4, 6), 16),
	};
}

function srgbToLinear(channel) {
	const normalized = channel / 255;
	if (normalized <= 0.03928) {
		return normalized / 12.92;
	}
	return ((normalized + 0.055) / 1.055) ** 2.4;
}

function getLuminance(hex) {
	const { r, g, b } = hexToRgb(hex);
	const rl = srgbToLinear(r);
	const gl = srgbToLinear(g);
	const bl = srgbToLinear(b);
	return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl;
}

function getContrastRatio(foreground, background) {
	const fgLum = getLuminance(foreground);
	const bgLum = getLuminance(background);
	const lighter = Math.max(fgLum, bgLum);
	const darker = Math.min(fgLum, bgLum);
	return (lighter + 0.05) / (darker + 0.05);
}

const checks = [
	// ---- LIGHT MODE ----
	{
		type: "text",
		mode: "light",
		name: "foreground on background",
		foreground: "#0A0A09",
		background: "#FFFFFF",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "light",
		name: "card-foreground on card",
		foreground: "#0A0A09",
		background: "#FFF0D9",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "light",
		name: "popover-foreground on popover",
		foreground: "#0A0A09",
		background: "#FFFFFF",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "light",
		name: "primary-foreground on primary",
		foreground: "#0A0A09",
		background: "#E1F690",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "light",
		name: "secondary-foreground on secondary",
		foreground: "#0A0A09",
		background: "#E9FEFF",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "light",
		name: "accent-foreground on accent",
		foreground: "#0A0A09",
		background: "#FFF0D9",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "light",
		name: "muted-foreground on muted",
		foreground: "#5B5B58",
		background: "#F5F4EF",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "light",
		name: "destructive-foreground on destructive",
		foreground: "#FFFFFF",
		background: "#B42318",
		minRatio: 4.5,
	},
	{
		type: "ui",
		mode: "light",
		name: "border on background",
		foreground: "#8C8A82",
		background: "#FFFFFF",
		minRatio: 3,
	},
	{
		type: "ui",
		mode: "light",
		name: "panel border on panel background",
		foreground: "#9A8A70",
		background: "#FFF7E8",
		minRatio: 3,
	},
	{
		type: "ui",
		mode: "light",
		name: "secondary-border on secondary",
		foreground: "#287F81",
		background: "#E9FEFF",
		minRatio: 3,
	},
	{
		type: "ui",
		mode: "light",
		name: "ring on background",
		foreground: "#0A0A09",
		background: "#FFFFFF",
		minRatio: 3,
	},

	// ---- DARK MODE ----
	{
		type: "text",
		mode: "dark",
		name: "[dark] foreground on background",
		foreground: "#F0F0EE",
		background: "#0A0A09",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "dark",
		name: "[dark] card-foreground on card",
		foreground: "#F0F0EE",
		background: "#141412",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "dark",
		name: "[dark] popover-foreground on popover",
		foreground: "#F0F0EE",
		background: "#111110",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "dark",
		name: "[dark] primary-foreground on primary",
		foreground: "#0A0A09",
		background: "#E1F690",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "dark",
		name: "[dark] secondary-foreground on secondary",
		foreground: "#7CFBFD",
		background: "#0D4A4B",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "dark",
		name: "[dark] accent-foreground on accent",
		foreground: "#F0F0EE",
		background: "#1A1A18",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "dark",
		name: "[dark] muted-foreground on muted",
		foreground: "#A8A8A4",
		background: "#1F1F1D",
		minRatio: 4.5,
	},
	{
		type: "text",
		mode: "dark",
		name: "[dark] destructive-foreground on destructive",
		foreground: "#FFFFFF",
		background: "#B91C1C",
		minRatio: 4.5,
	},
	{
		type: "ui",
		mode: "dark",
		name: "[dark] border on background",
		foreground: "#636360",
		background: "#0A0A09",
		minRatio: 3,
	},
	{
		type: "ui",
		mode: "dark",
		name: "[dark] ring (Lime Cream) on background",
		foreground: "#E1F690",
		background: "#0A0A09",
		minRatio: 3,
	},
	{
		type: "ui",
		mode: "dark",
		name: "[dark] sidebar border on sidebar background",
		foreground: "#636360",
		background: "#0D0D0C",
		minRatio: 3,
	},
];

console.log("Elevo contrast check — light + dark (WCAG)");
console.log("-------------------------------------------");

let hasFailure = false;
let lastMode = "";
for (const check of checks) {
	const mode = check.mode ?? "light";
	if (mode !== lastMode) {
		console.log(`\n  [${mode.toUpperCase()} MODE]`);
		lastMode = mode;
	}
	const ratio = getContrastRatio(check.foreground, check.background);
	const pass = ratio >= check.minRatio;
	if (!pass) {
		hasFailure = true;
	}

	const status = pass ? "✓ PASS" : "✗ FAIL";
	console.log(
		`  ${status} [${check.type}] ${check.name}: ${ratio.toFixed(2)}:1 (min ${check.minRatio}:1)`,
	);
}

console.log("");
if (hasFailure) {
	console.error("One or more contrast checks FAILED.");
	process.exit(1);
}

console.log("All contrast checks passed.");
