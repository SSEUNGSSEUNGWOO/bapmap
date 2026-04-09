import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import SpotsClient from "../../spots/SpotsClient";
import { Suspense } from "react";
import type { Metadata } from "next";

export const revalidate = 300;

export const metadata: Metadata = {
  title: "スポット一覧 | Bapmap",
  description: "韓国のローカルグルメスポット。地元の人が実際に通うお店を厳選。",
  alternates: {
    canonical: "https://bapmap.com/ja/spots",
    languages: {
      "en": "https://bapmap.com/spots",
      "ja": "https://bapmap.com/ja/spots",
    },
  },
};

export default async function JaSpotsPage() {
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
