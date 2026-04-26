import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import SpotsClient from "@/app/spots/SpotsClient";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

const CITY_DISPLAY: Record<string, string> = {
  seoul: "Seoul", gangwon: "Gangwon", gyeonggi: "Gyeonggi",
  jeju: "Jeju Island", incheon: "Incheon", gyeongsangbuk: "Gyeongsangbuk",
};

const CATEGORY_DISPLAY: Record<string, { label: string; description: string; keywords: string }> = {
  "korean-bbq": {
    label: "Korean BBQ",
    description: "Samgyeopsal, galbi, dak galbi — grilled right at your table.",
    keywords: "samgyeopsal, galbi, Korean BBQ restaurants",
  },
  "noodles": {
    label: "Noodles",
    description: "Ramen, buckwheat noodles, cold noodles — slurp-worthy picks.",
    keywords: "ramen, naengmyeon, kalguksu, Korean noodles",
  },
  "korean-soup": {
    label: "Korean Soup",
    description: "Haejangguk, sundubu, doenjang — the real Korean comfort food.",
    keywords: "haejangguk, sundubu jjigae, Korean soup",
  },
  "seafood": {
    label: "Seafood",
    description: "Raw fish, mulhoe, grilled catch — fresh from Korean waters.",
    keywords: "hoe, sashimi, seafood, Korean raw fish",
  },
  "gopchang": {
    label: "Gopchang",
    description: "Gopchang, makchang, chicken feet — the offal spots locals love.",
    keywords: "gopchang, makchang, Korean offal BBQ",
  },
  "tteokbokki": {
    label: "Tteokbokki",
    description: "Spicy rice cakes, street style and sit-down.",
    keywords: "tteokbokki, spicy rice cakes, Korean street food",
  },
  "bakery-cafe": {
    label: "Bakery & Cafe",
    description: "Artisan bread, specialty coffee, and Korean-style cafes.",
    keywords: "Korean bakery, cafe, bread, specialty coffee",
  },
  "bar": {
    label: "Bar",
    description: "Makgeolli bars, soju spots, wine — where locals drink.",
    keywords: "makgeolli bar, soju, Korean drinking",
  },
  "japanese": {
    label: "Japanese",
    description: "Ramen, tonkatsu, and Japanese food done right in Korea.",
    keywords: "tonkatsu, Japanese food Korea, ramen",
  },
  "chinese": {
    label: "Chinese",
    description: "Jjajangmyeon, jjamppong — Korean-Chinese classics.",
    keywords: "jjajangmyeon, jjamppong, Korean Chinese food",
  },
  "italian": {
    label: "Italian",
    description: "Pizza and pasta — Italian food the Korean way.",
    keywords: "Italian restaurant Korea, pizza Seoul",
  },
  "western": {
    label: "Western",
    description: "Burgers, steaks, and Western food worth seeking out.",
    keywords: "burger Seoul, Western restaurant Korea",
  },
};

// DB 카테고리명 → URL slug
function categoryToSlug(cat: string) {
  return cat.toLowerCase().replace(/\s+&\s+/g, "-").replace(/\s+/g, "-").replace(/[^\w-]/g, "");
}

// URL slug → DB 카테고리명
function slugToCategory(slug: string) {
  const map: Record<string, string> = {
    "korean-bbq": "Korean BBQ",
    "noodles": "Noodles",
    "korean-soup": "Korean Soup",
    "seafood": "Seafood",
    "gopchang": "Gopchang",
    "tteokbokki": "Tteokbokki",
    "bakery-cafe": "Bakery & Cafe",
    "bar": "Bar",
    "japanese": "Japanese",
    "chinese": "Chinese",
    "italian": "Italian",
    "western": "Western",
    "chicken": "Chicken",
    "asian": "Asian",
    "street-food": "Street Food",
  };
  return map[slug] || slug;
}

export async function generateStaticParams() {
  const { data } = await supabase
    .from("spots")
    .select("city, category")
    .eq("status", "업로드완료");

  const params = new Set<string>();
  (data ?? []).forEach((r) => {
    if (r.city && r.category) {
      params.add(`${r.city.toLowerCase()}|${categoryToSlug(r.category)}`);
    }
  });

  return Array.from(params).map((p) => {
    const [city, category] = p.split("|");
    return { city, category };
  });
}

export async function generateMetadata({ params }: { params: Promise<{ city: string; category: string }> }): Promise<Metadata> {
  const { city, category } = await params;
  const cityLabel = CITY_DISPLAY[city] || city.charAt(0).toUpperCase() + city.slice(1);
  const catMeta = CATEGORY_DISPLAY[category];
  const catLabel = catMeta?.label || slugToCategory(category);

  return {
    title: `Best ${catLabel} in ${cityLabel} | Bapmap`,
    description: `The best ${catLabel.toLowerCase()} spots in ${cityLabel}, Korea — personally curated. ${catMeta?.keywords || ""}`,
    alternates: {
      canonical: `https://bapmap.com/cities/${city}/${category}`,
    },
  };
}

export default async function CityCategory({ params }: { params: Promise<{ city: string; category: string }> }) {
  const { city, category } = await params;
  const cityLabel = CITY_DISPLAY[city] || city.charAt(0).toUpperCase() + city.slice(1);
  const catMeta = CATEGORY_DISPLAY[category];
  const catLabel = catMeta?.label || slugToCategory(category);
  const dbCategory = slugToCategory(category);

  const { data: spots } = await supabase
    .from("spots")
    .select("id, name, english_name, city, region, image_url, image_urls, rating, category, price_level, subway, tagline")
    .eq("status", "업로드완료")
    .ilike("city", city)
    .eq("category", dbCategory)
    .order("rating", { ascending: false });

  if (!spots || spots.length === 0) notFound();

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <p className="text-xs font-bold tracking-[0.2em] uppercase mb-2" style={{ color: "var(--orange)" }}>
        <Link href="/cities" style={{ color: "var(--orange)", textDecoration: "none" }}>Cities</Link>
        {" / "}
        <Link href={`/cities/${city}`} style={{ color: "var(--orange)", textDecoration: "none" }}>{cityLabel}</Link>
        {" / "}{catLabel}
      </p>
      <h1 className="font-display mb-3" style={{ fontSize: "clamp(2rem,5vw,3.5rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
        Best {catLabel} in {cityLabel}
      </h1>
      <p className="mb-10" style={{ color: "var(--muted)" }}>
        {catMeta?.description || `${spots.length} curated ${catLabel.toLowerCase()} spots in ${cityLabel}.`}
        {" "}Personally visited. No tourist traps.
      </p>

      <Suspense>
        <SpotsClient spots={spots as Spot[]} />
      </Suspense>
    </div>
  );
}
