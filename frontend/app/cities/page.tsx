import { supabase } from "@/lib/supabase";
import Link from "next/link";
import type { Metadata } from "next";

export const revalidate = 3600;

export const metadata: Metadata = {
  title: "Explore by City | Bapmap",
  description: "Find the best local restaurants and food spots in Seoul, Gangwon, Gyeonggi, Jeju and more — curated by locals.",
  alternates: {
    canonical: "https://bapmap.com/cities",
  },
};

const CITY_META: Record<string, { label: string; description: string; emoji: string }> = {
  Seoul: { label: "Seoul", description: "The best local eats in Korea's capital — from Hongdae to Gangnam.", emoji: "🏙️" },
  Gangwon: { label: "Gangwon", description: "Fresh seafood, dakgalbi, and mountain food in Korea's nature province.", emoji: "🏔️" },
  Gyeonggi: { label: "Gyeonggi", description: "Day-trip worthy spots just outside Seoul.", emoji: "🌿" },
  Jeju: { label: "Jeju", description: "Black pork, haenyeo seafood, and island specialties.", emoji: "🍊" },
  Incheon: { label: "Incheon", description: "Chinatown jjajangmyeon, fresh seafood, and more.", emoji: "🚢" },
  Gyeongsangbuk: { label: "Gyeongsangbuk", description: "Traditional flavors from Korea's southeastern heartland.", emoji: "🏯" },
};

export default async function CitiesPage() {
  const { data } = await supabase
    .from("spots")
    .select("city")
    .eq("status", "업로드완료");

  const cityCounts = (data ?? []).reduce<Record<string, number>>((acc, r) => {
    const c = r.city;
    if (c) acc[c] = (acc[c] || 0) + 1;
    return acc;
  }, {});

  const cities = Object.entries(cityCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([city, count]) => ({ city, count, slug: city.toLowerCase(), ...CITY_META[city] }));

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <p className="text-xs font-bold tracking-[0.2em] uppercase mb-2" style={{ color: "var(--orange)" }}>Explore</p>
      <h1 className="font-display mb-3" style={{ fontSize: "clamp(2rem,5vw,3.5rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
        Pick a City
      </h1>
      <p className="mb-10" style={{ color: "var(--muted)" }}>Local food picks, organized by where you're headed.</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {cities.map(({ city, count, slug, label, description, emoji }) => (
          <Link key={city} href={`/cities/${slug}`} className="group block no-underline">
            <div className="rounded-2xl p-6 border transition-all duration-200 group-hover:shadow-lg group-hover:-translate-y-0.5"
              style={{ background: "var(--surface)", borderColor: "var(--border)" }}>
              <div className="text-3xl mb-3">{emoji || "🍽️"}</div>
              <div className="font-semibold text-lg mb-1" style={{ color: "var(--ink)" }}>{label || city}</div>
              <div className="text-sm mb-3" style={{ color: "var(--muted)" }}>{description || `${count} curated spots`}</div>
              <div className="text-xs font-bold" style={{ color: "var(--orange)" }}>{count} spots →</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
