import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import type { Metadata } from "next";
import SpotsClient from "./SpotsClient";
import { Suspense } from "react";

export const revalidate = 300;

export const metadata: Metadata = {
  title: "All Spots | Bapmap",
  description: "Every Korean restaurant on Bapmap. Real local picks — no tourist traps.",
  alternates: {
    canonical: "https://bapmap.com/spots",
    languages: {
      "en": "https://bapmap.com/spots",
      "ja": "https://bapmap.com/ja/spots",
    },
  },
};

export default async function SpotsPage() {
  const { data: spots } = await supabase
    .from("spots")
    .select("id, name, english_name, city, region, image_url, image_urls, rating, category, price_level, subway, tagline")
    .eq("status", "업로드완료")
    .order("created_at", { ascending: false });

  return (
    <Suspense>
      <SpotsClient spots={(spots ?? []) as Spot[]} />
    </Suspense>
  );
}
