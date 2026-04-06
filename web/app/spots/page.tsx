import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import SpotsClient from "./SpotsClient";
import { Suspense } from "react";

export const revalidate = 300;

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
