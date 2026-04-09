import { supabase } from "@/lib/supabase";
import MapClient from "../../map/MapClient";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "マップ — Bapmap",
  description: "韓国のローカルグルメスポットをマップで探す。",
  alternates: {
    canonical: "https://bapmap.com/ja/map",
    languages: {
      "en": "https://bapmap.com/map",
      "ja": "https://bapmap.com/ja/map",
    },
  },
};

export default async function JaMapPage() {
  const { data: spots } = await supabase
    .from("spots")
    .select("id, name, english_name, lat, lng, category, region, city, rating, image_url")
    .eq("status", "업로드완료");

  return <MapClient spots={spots ?? []} />;
}
