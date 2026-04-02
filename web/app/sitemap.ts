import { supabase } from "@/lib/supabase";
import type { MetadataRoute } from "next";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const { data: spots } = await supabase
    .from("spots")
    .select("english_name, name, created_at")
    .eq("status", "업로드완료");

  const spotUrls = (spots ?? []).map((spot) => {
    const slug = (spot.english_name || spot.name)
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^\w-]/g, "");
    return {
      url: `https://bapmap.com/spots/${slug}`,
      lastModified: new Date(spot.created_at),
      changeFrequency: "monthly" as const,
      priority: 0.8,
    };
  });

  return [
    { url: "https://bapmap.com", lastModified: new Date(), changeFrequency: "weekly", priority: 1 },
    { url: "https://bapmap.com/spots", lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: "https://bapmap.com/about", lastModified: new Date(), changeFrequency: "monthly", priority: 0.5 },
    ...spotUrls,
  ];
}
