import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import SpotsClient from "./SpotsClient";
import Link from "next/link";
import { Suspense } from "react";

export const revalidate = 300;

const CITY_TABS = [
  { label: "All", href: "/spots", image: null },
  { label: "Seoul", href: "/cities/seoul", image: "https://images.unsplash.com/photo-1748273945548-6ef8d73b9325?w=800&q=80" },
  { label: "Gangwon", href: "/cities/gangwon", image: "https://images.unsplash.com/photo-1721999591032-a8b3845c9564?w=800&q=80" },
  { label: "Gyeonggi", href: "/cities/gyeonggi", image: "https://images.unsplash.com/photo-1619341663312-0b8cde878b2f?w=800&q=80" },
  { label: "Jeju", href: "/cities/jeju", image: "https://images.unsplash.com/photo-1613186448181-7ba25cc0ff2a?w=800&q=80" },
  { label: "Incheon", href: "/cities/incheon", image: "https://images.unsplash.com/photo-1592205838971-5d7c8b9de850?w=800&q=80" },
];

export default async function SpotsPage() {
  const { data: spots } = await supabase
    .from("spots")
    .select("id, name, english_name, city, region, image_url, image_urls, rating, category, price_level, subway, tagline")
    .eq("status", "업로드완료")
    .order("created_at", { ascending: false });

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <p className="text-xs font-bold tracking-[0.2em] uppercase mb-2" style={{ color: "var(--orange)" }}>The list</p>
      <h1 className="font-display mb-3" style={{ fontSize: "clamp(2.5rem,6vw,4rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
        Where Koreans Eat
      </h1>
      <p className="mb-6" style={{ color: "var(--muted)" }}>No tourist traps. No sponsored picks. Just the real thing.</p>

      {/* 도시 탭 */}
      <div className="flex gap-3 overflow-x-auto pb-2 mb-8 -mx-1 px-1" style={{ scrollbarWidth: "none" }}>
        {CITY_TABS.map(({ label, href, image }) => (
          <Link key={label} href={href} className="no-underline flex-shrink-0">
            <div className="relative rounded-2xl overflow-hidden transition-all duration-200 hover:-translate-y-1 hover:shadow-lg"
              style={{ width: 110, height: 70 }}>
              {image ? (
                <img src={image} alt={label} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full" style={{ background: "var(--orange)" }} />
              )}
              <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.55) 60%, transparent)" }} />
              <div className="absolute bottom-0 left-0 right-0 px-3 pb-2">
                <span className="text-xs font-bold text-white">{label}</span>
                {label === "All" && <span className="block text-[10px] text-white/70">All cities</span>}
              </div>
              {label === "All" && (
                <div className="absolute inset-0 ring-2 ring-inset ring-white/40 rounded-2xl" />
              )}
            </div>
          </Link>
        ))}
      </div>

      <Suspense>
        <SpotsClient spots={(spots ?? []) as Spot[]} />
      </Suspense>
    </div>
  );
}
