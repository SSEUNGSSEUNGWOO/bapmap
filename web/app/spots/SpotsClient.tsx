"use client";

import { useState, useMemo, useRef } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import type { Spot } from "@/lib/supabase";
import { useLang } from "@/lib/LanguageContext";

const T = {
  en: {
    eyebrow: "The list",
    title: "Where Koreans Eat",
    subtitle: "No tourist traps. No sponsored picks. Just the real thing.",
    allCities: "All cities",
    searchPlaceholder: "Search spots, neighborhoods...",
    newest: "Newest",
    topRated: "Top Rated",
    az: "A–Z",
    allCategories: "All Categories",
    allAreas: "All Areas",
    spot: "spot",
    spots: "spots",
    inArea: "in",
    forQuery: "for",
    noSpotsTitle: "No spots found",
    noSpotsDesc: "Try a different search or filter",
  },
  ja: {
    eyebrow: "リスト",
    title: "韓国人が食べに行く店",
    subtitle: "観光客向けの店はなし。広告もなし。本物だけ。",
    allCities: "全都市",
    searchPlaceholder: "スポット・エリアを検索...",
    newest: "新着順",
    topRated: "評価順",
    az: "A–Z",
    allCategories: "全カテゴリー",
    allAreas: "全エリア",
    spot: "件",
    spots: "件",
    inArea: "",
    forQuery: "「",
    noSpotsTitle: "スポットが見つかりません",
    noSpotsDesc: "検索条件を変えてみてください",
  },
};

const CATEGORY_JA: Record<string, string> = {
  "Asian": "アジア料理",
  "Bakery & Cafe": "ベーカリー＆カフェ",
  "Bar": "バー",
  "Chinese": "中華料理",
  "Gopchang": "コプチャン",
  "Italian": "イタリア料理",
  "Japanese": "日本料理",
  "Korean": "韓国料理",
  "Korean BBQ": "韓国式焼肉",
  "Korean Soup": "韓国スープ",
  "Noodles": "麺料理",
  "Pizza": "ピザ",
  "Seafood": "海鮮",
  "Street Food": "屋台・ストリートフード",
  "Tteokbokki": "トッポッキ",
  "Western": "洋食",
};

const REGION_JA: Record<string, string> = {
  "Dongdaemun District": "東大門区", "Dongdaemun-gu": "東大門区",
  "Dongjak District": "銅雀区", "Dongjak-gu": "銅雀区",
  "Gangnam District": "江南区", "Gangnam-gu": "江南区",
  "Guro District": "九老区", "Guro-gu": "九老区",
  "Gwanak District": "冠岳区", "Gwanak-gu": "冠岳区",
  "Gwangjin District": "広津区", "Gwangjin-gu": "広津区",
  "Jongno District": "鍾路区", "Jongno-gu": "鍾路区",
  "Jung District": "中区", "Jung-gu": "中区",
  "Mapo District": "麻浦区", "Mapo-gu": "麻浦区",
  "Seocho District": "瑞草区", "Seocho-gu": "瑞草区",
  "Seodaemun District": "西大門区", "Seodaemun-gu": "西大門区",
  "Seongdong District": "城東区", "Seongdong-gu": "城東区",
  "Songpa District": "松坡区", "Songpa-gu": "松坡区",
  "Yeongdeungpo": "永登浦", "Yeongdeungpo District": "永登浦区", "Yeongdeungpo-gu": "永登浦区",
  "Yongsan District": "龍山区", "Yongsan-gu": "龍山区",
};

const CITY_TABS = [
  { label: "All", labelJa: "すべて", href: "/spots", image: null },
  { label: "Seoul", labelJa: "ソウル", href: "/cities/seoul", image: "https://images.unsplash.com/photo-1748273945548-6ef8d73b9325?w=800&q=80" },
  { label: "Gangwon", labelJa: "江原道", href: "/cities/gangwon", image: "https://images.unsplash.com/photo-1721999591032-a8b3845c9564?w=800&q=80" },
  { label: "Gyeonggi", labelJa: "京畿道", href: "/cities/gyeonggi", image: "https://images.unsplash.com/photo-1619341663312-0b8cde878b2f?w=800&q=80" },
  { label: "Jeju", labelJa: "済州島", href: "/cities/jeju", image: "https://images.unsplash.com/photo-1613186448181-7ba25cc0ff2a?w=800&q=80" },
  { label: "Incheon", labelJa: "仁川", href: "/cities/incheon", image: "https://images.unsplash.com/photo-1592205838971-5d7c8b9de850?w=800&q=80" },
];

function SpotCardImage({ images, name }: { images: string[]; name: string }) {
  const [idx, setIdx] = useState(0);
  const [hovering, setHovering] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const handleMouseEnter = () => {
    if (images.length <= 1) return;
    setHovering(true);
    intervalRef.current = setInterval(() => {
      setIdx((prev) => (prev + 1) % images.length);
    }, 700);
  };

  const handleMouseLeave = () => {
    setHovering(false);
    if (intervalRef.current) clearInterval(intervalRef.current);
    setIdx(0);
  };

  return (
    <div
      className="h-48 overflow-hidden bg-gray-100 relative"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {images.map((url, i) => (
        <img
          key={i}
          src={url}
          alt={`${name} ${i + 1}`}
          className="absolute inset-0 w-full h-full object-cover transition-opacity duration-300"
          style={{ opacity: idx === i ? 1 : 0 }}
        />
      ))}
      {images.length > 1 && hovering && (
        <div className="absolute bottom-2 left-0 right-0 flex justify-center gap-1 z-10">
          {images.map((_, i) => (
            <div key={i} className="w-1.5 h-1.5 rounded-full transition-all" style={{ background: idx === i ? "#fff" : "rgba(255,255,255,0.5)" }} />
          ))}
        </div>
      )}
    </div>
  );
}

type SortOption = "newest" | "rating" | "name";
const PAGE_SIZE = 9;

export default function SpotsClient({ spots, hideHeader }: { spots: Spot[]; hideHeader?: boolean }) {
  const { lang } = useLang();
  const t = T[lang];
  const isJa = lang === "ja";
  const searchParams = useSearchParams();
  const [query, setQuery] = useState("");
  const [activeRegion, setActiveRegion] = useState("All");
  const [activeCategory, setActiveCategory] = useState(searchParams.get("category") || "All");
  const [sort, setSort] = useState<SortOption>("newest");
  const [page, setPage] = useState(1);

  const regions = useMemo(() => {
    const set = new Set(spots.map((s) => s.region || s.city).filter(Boolean));
    return ["All", ...Array.from(set).sort()];
  }, [spots]);

  const categories = useMemo(() => {
    const set = new Set(spots.map((s) => s.category).filter(Boolean));
    return ["All", ...Array.from(set).sort()];
  }, [spots]);

  const filtered = useMemo(() => {
    const result = spots.filter((s) => {
      const matchRegion = activeRegion === "All" || (s.region || s.city) === activeRegion;
      const matchCategory = activeCategory === "All" || s.category === activeCategory;
      const q = query.toLowerCase();
      const matchQuery = !q ||
        (s.english_name || s.name).toLowerCase().includes(q) ||
        (s.region || s.city || "").toLowerCase().includes(q) ||
        (s.category || "").toLowerCase().includes(q);
      return matchRegion && matchCategory && matchQuery;
    });

    if (sort === "rating") return [...result].sort((a, b) => (b.rating || 0) - (a.rating || 0));
    if (sort === "name") return [...result].sort((a, b) => (a.english_name || a.name).localeCompare(b.english_name || b.name));
    return result;
  }, [spots, query, activeRegion, activeCategory, sort]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const handleFilterChange = (fn: () => void) => {
    fn();
    setPage(1);
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      {!hideHeader && (
        <>
          {/* 헤더 */}
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-2" style={{ color: "var(--orange)" }}>{t.eyebrow}</p>
          <h1 className="font-display mb-3" style={{ fontSize: "clamp(2.5rem,6vw,4rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
            {t.title}
          </h1>
          <p className="mb-6" style={{ color: "var(--muted)" }}>{t.subtitle}</p>

          {/* 도시 탭 */}
          <div className="flex gap-3 overflow-x-auto pb-2 mb-8 -mx-1 px-1" style={{ scrollbarWidth: "none" }}>
            {CITY_TABS.map(({ label, labelJa, href, image }) => (
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
                    <span className="text-xs font-bold text-white">{isJa ? labelJa : label}</span>
                    {label === "All" && <span className="block text-[10px] text-white/70">{t.allCities}</span>}
                  </div>
                  {label === "All" && (
                    <div className="absolute inset-0 ring-2 ring-inset ring-white/40 rounded-2xl" />
                  )}
                </div>
              </Link>
            ))}
          </div>
        </>
      )}

      {/* 검색 + 필터 */}
      <div className="mb-10 space-y-3">
        {/* 검색창 */}
        <div className="relative">
          <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" style={{ color: "var(--muted)" }}>
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            placeholder={t.searchPlaceholder}
            value={query}
            onChange={(e) => handleFilterChange(() => setQuery(e.target.value))}
            className="w-full pl-11 pr-4 py-3 rounded-xl text-sm outline-none"
            style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--ink)" }}
          />
          {query && (
            <button onClick={() => handleFilterChange(() => setQuery(""))} className="absolute right-4 top-1/2 -translate-y-1/2 text-xs" style={{ color: "var(--muted)" }}>✕</button>
          )}
        </div>

        {/* 드롭다운 필터 한 줄 */}
        <div className="flex gap-2">
          {/* 정렬 */}
          <select
            value={sort}
            onChange={(e) => handleFilterChange(() => setSort(e.target.value as SortOption))}
            className="text-xs font-semibold px-3 py-2 rounded-xl outline-none cursor-pointer"
            style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--ink)" }}
          >
            <option value="newest">{t.newest}</option>
            <option value="rating">{t.topRated}</option>
            <option value="name">{t.az}</option>
          </select>

          {/* 카테고리 */}
          <select
            value={activeCategory}
            onChange={(e) => handleFilterChange(() => setActiveCategory(e.target.value))}
            className="text-xs font-semibold px-3 py-2 rounded-xl outline-none cursor-pointer flex-1"
            style={{ background: "var(--surface)", border: "1px solid var(--border)", color: activeCategory !== "All" ? "var(--orange)" : "var(--ink)" }}
          >
            {categories.map((c) => <option key={c} value={c}>{c === "All" ? t.allCategories : (isJa && CATEGORY_JA[c]) ? CATEGORY_JA[c] : c}</option>)}
          </select>

          {/* 지역 */}
          <select
            value={activeRegion}
            onChange={(e) => handleFilterChange(() => setActiveRegion(e.target.value))}
            className="text-xs font-semibold px-3 py-2 rounded-xl outline-none cursor-pointer flex-1"
            style={{ background: "var(--surface)", border: "1px solid var(--border)", color: activeRegion !== "All" ? "var(--orange)" : "var(--ink)" }}
          >
            {regions.map((r) => <option key={r} value={r}>{r === "All" ? t.allAreas : (isJa && REGION_JA[r]) ? REGION_JA[r] : r}</option>)}
          </select>
        </div>
      </div>

      {/* 결과 수 */}
      <p className="text-xs font-semibold mb-6 tracking-wide" style={{ color: "var(--muted)" }}>
        {filtered.length} {filtered.length === 1 ? t.spot : t.spots}
        {activeCategory !== "All" && ` · ${activeCategory}`}
        {activeRegion !== "All" && ` ${t.inArea} ${isJa ? (REGION_JA[activeRegion] || activeRegion) : activeRegion}`}
        {query && isJa ? `「${query}」` : query ? ` for "${query}"` : ""}
      </p>

      {/* 카드 그리드 */}
      {filtered.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {paginated.map((spot) => {
            const slug = (spot.english_name || spot.name).toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
            return (
              <Link key={spot.id} href={`/spots/${slug}`} className="group block no-underline h-full">
                <div className="bg-white rounded-2xl overflow-hidden border border-[var(--border)] group-hover:shadow-xl group-hover:-translate-y-1 transition-all duration-200 h-full flex flex-col">
                  {spot.image_url ? (
                    <SpotCardImage
                      images={Array.isArray(spot.image_urls) && spot.image_urls.length > 0 ? spot.image_urls.slice(0, 3) : [spot.image_url]}
                      name={spot.english_name || spot.name}
                    />
                  ) : (
                    <div className="h-48 flex items-center justify-center" style={{ background: "var(--surface)" }}>
                      <span style={{ fontSize: "2.5rem" }}>🍜</span>
                    </div>
                  )}
                  <div className="p-4 flex flex-col flex-1">
                    <div className="text-[10px] font-bold tracking-widest uppercase mb-1" style={{ color: "var(--orange)" }}>
                      {isJa ? (REGION_JA[spot.region || spot.city || ""] || spot.region || spot.city) : (spot.region || spot.city)}
                    </div>
                    <div className="font-semibold text-sm mb-auto line-clamp-2" style={{ color: "var(--ink)" }}>
                      {spot.english_name || spot.name}
                    </div>
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center gap-2">
                        <span className="text-xs" style={{ color: "var(--muted)" }}>★ {spot.rating}</span>
                        {spot.price_level && <span className="text-xs" style={{ color: "var(--muted)" }}>{spot.price_level}</span>}
                      </div>
                      {spot.category && (
                        <div className="text-[10px] font-medium px-2 py-0.5 rounded-full" style={{ background: "var(--surface)", color: "var(--muted)", border: "1px solid var(--border)" }}>
                          {isJa ? (CATEGORY_JA[spot.category!] || spot.category) : spot.category}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-20">
          <div className="text-4xl mb-4">🍽️</div>
          <p className="font-semibold mb-1" style={{ color: "var(--ink)" }}>{t.noSpotsTitle}</p>
          <p className="text-sm" style={{ color: "var(--muted)" }}>{t.noSpotsDesc}</p>
        </div>
      )}

      {/* 페이지네이션 */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-2 mt-10">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 rounded-full text-sm font-semibold transition-all disabled:opacity-30"
            style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--ink)" }}
          >
            ←
          </button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className="w-9 h-9 rounded-full text-sm font-semibold transition-all"
              style={{
                background: page === p ? "var(--orange)" : "var(--surface)",
                color: page === p ? "#fff" : "var(--muted)",
                border: `1px solid ${page === p ? "var(--orange)" : "var(--border)"}`,
              }}
            >
              {p}
            </button>
          ))}
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 rounded-full text-sm font-semibold transition-all disabled:opacity-30"
            style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--ink)" }}
          >
            →
          </button>
        </div>
      )}
    </div>
  );
}
