"use client";

import { useEffect, useState } from "react";
import {
	getDiagnosticsState,
	isDiagnosticsEnabled,
	subscribeDiagnostics,
} from "@/integrations/socialmediaai/diagnostics";

export function SocialMediaAiDiagnosticsPanel() {
	const [enabled, setEnabled] = useState(false);
	const [state, setState] = useState(() => ({ ...getDiagnosticsState() }));

	useEffect(() => {
		setEnabled(isDiagnosticsEnabled());
	}, []);

	useEffect(() => {
		if (!enabled) return;
		return subscribeDiagnostics(() => {
			const next = getDiagnosticsState();
			setState({
				...next,
				recentEvents: [...next.recentEvents],
				recentTimings: [...next.recentTimings],
			});
		});
	}, [enabled]);

	if (!enabled) return null;

	return (
		<div className="fixed bottom-3 right-3 z-[999] w-[min(92vw,420px)] rounded-md border border-primary/40 bg-background/95 p-3 text-xs shadow-lg backdrop-blur">
			<p className="mb-2 text-[11px] uppercase tracking-[0.14em] text-muted-foreground">
				Editor connectivity
			</p>
			<div className="grid grid-cols-2 gap-2">
				<span className="text-muted-foreground">projectId</span>
				<span className="truncate">{state.projectId || "-"}</span>
				<span className="text-muted-foreground">userId</span>
				<span className="truncate">{state.userId || "-"}</span>
				<span className="text-muted-foreground">save</span>
				<span>{state.saveState}</span>
				<span className="text-muted-foreground">url mode</span>
				<span>{state.urlMode}</span>
			</div>
			{state.lastSaveAt ? (
				<p className="mt-2 text-[11px] text-muted-foreground">
					last save: {new Date(state.lastSaveAt).toLocaleTimeString()}
				</p>
			) : null}
			<div className="mt-2 max-h-28 space-y-1 overflow-auto border-t pt-2">
				{state.recentEvents.length === 0 ? (
					<p className="text-[11px] text-muted-foreground">No recent API calls</p>
				) : (
					state.recentEvents.map((event) => (
						<div key={`${event.at}-${event.requestId || event.path}`} className="flex items-center justify-between gap-2 text-[11px]">
							<span className="truncate text-muted-foreground">
								{event.method} {event.path}
							</span>
							<span className={event.status >= 400 ? "text-destructive" : "text-foreground"}>
								{event.status}
							</span>
						</div>
					))
				)}
			</div>
			<div className="mt-2 max-h-28 space-y-1 overflow-auto border-t pt-2">
				{state.recentTimings.length === 0 ? (
					<p className="text-[11px] text-muted-foreground">No timing samples</p>
				) : (
					state.recentTimings.map((event) => (
						<div key={`${event.at}-${event.name}`} className="flex items-center justify-between gap-2 text-[11px]">
							<span className="truncate text-muted-foreground">{event.name}</span>
							<span className="text-foreground">{event.durationMs.toFixed(1)}ms</span>
						</div>
					))
				)}
			</div>
		</div>
	);
}
