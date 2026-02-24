import { Hero } from "@/components/landing/hero";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import type { Metadata } from "next";
import { SITE_URL } from "@/constants/site-constants";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
	alternates: {
		canonical: SITE_URL,
	},
};

export default async function Home() {
	if (process.env.NEXT_PUBLIC_FASTAPI_URL) {
		redirect("/projects");
	}

	return (
		<div>
			<Header />
			<Hero />
			<Footer />
		</div>
	);
}
