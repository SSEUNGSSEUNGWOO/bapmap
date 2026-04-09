import { supabase } from "@/lib/supabase";
import type { MetadataRoute } from "next";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const { data: spots } = await supabase
    .from("spots")
    .select("english_name, name, city, category, created_at")
    .eq("status", "업로드완료");

  const spotUrls = (spots ?? []).flatMap((spot) => {
    const slug = (spot.english_name || spot.name)
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^\w-]/g, "");
    return [
      {
        url: `https://bapmap.com/spots/${slug}`,
        lastModified: new Date(spot.created_at),
        changeFrequency: "monthly" as const,
        priority: 0.8,
      },
      {
        url: `https://bapmap.com/ja/spots/${slug}`,
        lastModified: new Date(spot.created_at),
        changeFrequency: "monthly" as const,
        priority: 0.8,
      },
    ];
  });

  const cities = [...new Set((spots ?? []).map((s) => s.city).filter(Boolean))];
  const cityUrls = cities.map((city) => ({
    url: `https://bapmap.com/cities/${city.toLowerCase()}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.85,
  }));

  const cityCatPairs = new Set(
    (spots ?? [])
      .filter((s) => s.city && s.category)
      .map((s) => `${s.city.toLowerCase()}|${s.category.toLowerCase().replace(/\s+&\s+/g, "-").replace(/\s+/g, "-").replace(/[^\w-]/g, "")}`)
  );
  const cityCatUrls = Array.from(cityCatPairs).map((pair) => {
    const [city, cat] = pair.split("|");
    return {
      url: `https://bapmap.com/cities/${city}/${cat}`,
      lastModified: new Date(),
      changeFrequency: "weekly" as const,
      priority: 0.8,
    };
  });

  const { data: guides } = await supabase
    .from("guides")
    .select("slug, created_at")
    .eq("status", "published");

  const guideUrls = (guides ?? []).flatMap((g) => [
    {
      url: `https://bapmap.com/guides/${g.slug}`,
      lastModified: new Date(g.created_at),
      changeFrequency: "monthly" as const,
      priority: 0.85,
    },
    {
      url: `https://bapmap.com/ja/guides/${g.slug}`,
      lastModified: new Date(g.created_at),
      changeFrequency: "monthly" as const,
      priority: 0.85,
    },
  ]);

  return [
    { url: "https://bapmap.com", lastModified: new Date(), changeFrequency: "weekly", priority: 1 },
    { url: "https://bapmap.com/ja", lastModified: new Date(), changeFrequency: "weekly", priority: 0.95 },
    { url: "https://bapmap.com/spots", lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: "https://bapmap.com/ja/spots", lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: "https://bapmap.com/guides", lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: "https://bapmap.com/ja/guides", lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: "https://bapmap.com/map", lastModified: new Date(), changeFrequency: "weekly", priority: 0.85 },
    { url: "https://bapmap.com/ja/map", lastModified: new Date(), changeFrequency: "weekly", priority: 0.85 },
    { url: "https://bapmap.com/cities", lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: "https://bapmap.com/about", lastModified: new Date(), changeFrequency: "monthly", priority: 0.5 },
    ...cityUrls,
    ...cityCatUrls,
    ...guideUrls,
    ...spotUrls,
  ];
}
