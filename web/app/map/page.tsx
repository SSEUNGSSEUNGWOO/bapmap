import { supabase } from "@/lib/supabase";
import MapClient from "./MapClient";

export const metadata = {
  title: "Map — Bapmap",
  description: "Explore local Korean spots on the map.",
};

export default async function MapPage() {
  const { data: spots } = await supabase
    .from("spots")
    .select("id, name, english_name, lat, lng, category, region, city, rating, image_url")
    .eq("status", "업로드완료");

  return <MapClient spots={spots ?? []} />;
}
