import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import SpotsClient from "@/app/spots/SpotsClient";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

const CITY_TABS = [
  { label: "All", href: "/spots", image: null },
  { label: "Seoul", href: "/cities/seoul", image: "https://images.unsplash.com/photo-1748273945548-6ef8d73b9325?w=800&q=80" },
  { label: "Gangwon", href: "/cities/gangwon", image: "https://images.unsplash.com/photo-1721999591032-a8b3845c9564?w=800&q=80" },
  { label: "Gyeonggi", href: "/cities/gyeonggi", image: "https://images.unsplash.com/photo-1619341663312-0b8cde878b2f?w=800&q=80" },
  { label: "Jeju", href: "/cities/jeju", image: "https://images.unsplash.com/photo-1613186448181-7ba25cc0ff2a?w=800&q=80" },
  { label: "Incheon", href: "/cities/incheon", image: "https://images.unsplash.com/photo-1592205838971-5d7c8b9de850?w=800&q=80" },
];

export const revalidate = 300;

const CITY_DISPLAY: Record<string, { label: string; description: string }> = {
  seoul: { label: "Seoul", description: "25 million people, one obsession: eating well. From 3am pojangmacha to Michelin-starred tasting menus — Seoul does it all, and somehow makes it look effortless." },
  gangwon: { label: "Gangwon", description: "The mountains meet the sea here. Dakgalbi in Chuncheon, freshly caught seafood in Sokcho, and air so clean it makes the food taste better. Worth every hour of the drive." },
  gyeonggi: { label: "Gyeonggi", description: "Seoul's quieter neighbor, but don't sleep on it. Budae jjigae in Uijeongbu, galbi in Suwon — some of Korea's most iconic dishes were born just outside the capital." },
  jeju: { label: "Jeju Island", description: "Black pork grilled over lava rock. Abalone porridge made by actual haenyeo divers. Hallabong tangerines everywhere. Jeju eats like nowhere else in Korea — because it is nowhere else." },
  incheon: { label: "Incheon", description: "Korea's gateway city has more going on than just the airport. The original Chinatown, fried rice worth missing your flight for, and raw seafood so fresh it's still moving." },
  gyeongsangbuk: { label: "Gyeongsangbuk", description: "Old Korea, preserved. The food here is bold, fermented, and uncompromising — the way it's been for centuries. Andong jjimdak, Yeongju hanwoo, makgeolli that actually tastes like something." },
};

export async function generateStaticParams() {
  const { data } = await supabase
    .from("spots")
    .select("city")
    .eq("status", "업로드완료");

  const cities = [...new Set((data ?? []).map((r) => r.city).filter(Boolean))];
  return cities.map((city) => ({ city: city.toLowerCase() }));
}

export async function generateMetadata({ params }: { params: Promise<{ city: string }> }): Promise<Metadata> {
  const { city } = await params;
  const meta = CITY_DISPLAY[city];
  const label = meta?.label || city.charAt(0).toUpperCase() + city.slice(1);
  return {
    title: `Best Local Restaurants in ${label} | Bapmap`,
    description: meta?.description || `Curated local food spots in ${label}, Korea.`,
  };
}

export default async function CityPage({ params }: { params: Promise<{ city: string }> }) {
  const { city } = await params;
  const meta = CITY_DISPLAY[city];
  const label = meta?.label || city.charAt(0).toUpperCase() + city.slice(1);

  const { data: spots } = await supabase
    .from("spots")
    .select("id, name, english_name, city, region, image_url, image_urls, rating, category, price_level, subway, tagline")
    .eq("status", "업로드완료")
    .ilike("city", city)
    .order("created_at", { ascending: false });

  if (!spots || spots.length === 0) notFound();

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <p className="text-xs font-bold tracking-[0.2em] uppercase mb-2" style={{ color: "var(--orange)" }}>
        <a href="/cities" style={{ color: "var(--orange)", textDecoration: "none" }}>Cities</a> / {label}
      </p>
      <h1 className="font-display mb-3" style={{ fontSize: "clamp(2rem,5vw,3.5rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
        Where Locals Eat in {label}
      </h1>
      <p className="mb-6" style={{ color: "var(--muted)" }}>
        {meta?.description || `${spots.length} curated spots in ${label}.`}
      </p>

      {/* 도시 탭 */}
      <div className="flex gap-3 overflow-x-auto pb-2 mb-8 -mx-1 px-1" style={{ scrollbarWidth: "none" }}>
        {CITY_TABS.map(({ label: tabLabel, href, image }) => {
          const isActive = href === `/cities/${city}`;
          return (
            <Link key={tabLabel} href={href} className="no-underline flex-shrink-0">
              <div className="relative rounded-2xl overflow-hidden transition-all duration-200 hover:-translate-y-1 hover:shadow-lg"
                style={{ width: 110, height: 70 }}>
                {image ? (
                  <img src={image} alt={tabLabel} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full" style={{ background: "var(--orange)" }} />
                )}
                <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.55) 60%, transparent)" }} />
                <div className="absolute bottom-0 left-0 right-0 px-3 pb-2">
                  <span className="text-xs font-bold text-white">{tabLabel}</span>
                </div>
                {isActive && (
                  <div className="absolute inset-0 ring-2 ring-inset rounded-2xl" style={{ borderColor: "var(--orange)" }} />
                )}
              </div>
            </Link>
          );
        })}
      </div>

      <Suspense>
        <SpotsClient spots={spots as Spot[]} />
      </Suspense>
    </div>
  );
}
