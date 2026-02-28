import { NextResponse } from "next/server";

const hostMode = Boolean(process.env.NEXT_PUBLIC_FASTAPI_URL);

const hostModeResponse = () =>
	NextResponse.json(
		{
			detail: "BetterAuth routes are disabled in SocialMediaAI host mode",
		},
		{ status: 404 },
	);

async function getHandlers() {
	const [{ auth }, { toNextJsHandler }] = await Promise.all([
		import("@/lib/auth/server"),
		import("better-auth/next-js"),
	]);
	return toNextJsHandler(auth);
}

export async function GET(request: Request) {
	if (hostMode) {
		return hostModeResponse();
	}
	const handlers = await getHandlers();
	return handlers.GET(request);
}

export async function POST(request: Request) {
	if (hostMode) {
		return hostModeResponse();
	}
	const handlers = await getHandlers();
	return handlers.POST(request);
}
