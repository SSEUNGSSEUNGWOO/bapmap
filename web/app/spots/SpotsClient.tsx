"use client";

import { useState, useMemo, useEffect, useRef } from "react";
import Link from "next/link";
import type { Spot } from "@/lib/supabase";

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

export default function SpotsClient({ spots }: { spots: Spot[] }) {
  const [query, setQuery] = useState("");
  const [activeRegion, setActiveRegion] = useState("All");
  const [sort, setSort] = useState<SortOption>("newest");
  const [page, setPage] = useState(1);

  const regions = useMemo(() => {
    const set = new Set(spots.map((s) => s.region || s.city).filter(Boolean));
    return ["All", ...Array.from(set).sort()];
  }, [spots]);

  const filtered = useMemo(() => {
    const result = spots.filter((s) => {
      const matchRegion = activeRegion === "All" || (s.region || s.city) === activeRegion;
      const q = query.toLowerCase();
      const matchQuery = !q ||
        (s.english_name || s.name).toLowerCase().includes(q) ||
        (s.region || s.city || "").toLowerCase().includes(q) ||
        (s.category || "").toLowerCase().includes(q);
      return matchRegion && matchQuery;
    });

    if (sort === "rating") return [...result].sort((a, b) => (b.rating || 0) - (a.rating || 0));
    if (sort === "name") return [...result].sort((a, b) => (a.english_name || a.name).localeCompare(b.english_name || b.name));
    return result;
  }, [spots, query, activeRegion, sort]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const handleFilterChange = (fn: () => void) => {
    fn();
    setPage(1);
  };

  return (
    <div>
      {/* 검색 + 필터 */}
      <div className="mb-10 space-y-4">
        {/* 검색창 */}
        <div className="relative">
          <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" style={{ color: "var(--muted)" }}>
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            placeholder="Search spots, neighborhoods..."
            value={query}
            onChange={(e) => handleFilterChange(() => setQuery(e.target.value))}
            className="w-full pl-11 pr-4 py-3 rounded-xl text-sm outline-none"
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              color: "var(--ink)",
            }}
          />
          {query && (
            <button onClick={() => handleFilterChange(() => setQuery(""))} className="absolute right-4 top-1/2 -translate-y-1/2 text-xs" style={{ color: "var(--muted)" }}>✕</button>
          )}
        </div>

        {/* 정렬 */}
        <div className="flex gap-2">
          {(["newest", "rating", "name"] as SortOption[]).map((s) => (
            <button
              key={s}
              onClick={() => handleFilterChange(() => setSort(s))}
              className="text-xs font-semibold px-4 py-2 rounded-full transition-all"
              style={{
                background: sort === s ? "var(--ink)" : "var(--surface)",
                color: sort === s ? "#fff" : "var(--muted)",
                border: `1px solid ${sort === s ? "var(--ink)" : "var(--border)"}`,
              }}
            >
              {s === "newest" ? "Newest" : s === "rating" ? "Top Rated" : "A–Z"}
            </button>
          ))}
        </div>

        {/* 지역 필터 */}
        <div className="flex gap-2 flex-wrap">
          {regions.map((r) => (
            <button
              key={r}
              onClick={() => handleFilterChange(() => setActiveRegion(r))}
              className="text-xs font-semibold px-4 py-2 rounded-full transition-all"
              style={{
                background: activeRegion === r ? "var(--orange)" : "var(--surface)",
                color: activeRegion === r ? "#fff" : "var(--muted)",
                border: `1px solid ${activeRegion === r ? "var(--orange)" : "var(--border)"}`,
              }}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* 결과 수 */}
      <p className="text-xs font-semibold mb-6 tracking-wide" style={{ color: "var(--muted)" }}>
        {filtered.length} {filtered.length === 1 ? "spot" : "spots"}
        {activeRegion !== "All" && ` in ${activeRegion}`}
        {query && ` for "${query}"`}
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
                      {spot.region || spot.city}
                    </div>
                    <div className="font-semibold text-sm mb-auto" style={{ color: "var(--ink)" }}>
                      {spot.english_name || spot.name}
                    </div>
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center gap-2">
                        <span className="text-xs" style={{ color: "var(--muted)" }}>★ {spot.rating}</span>
                        {spot.price_level && <span className="text-xs" style={{ color: "var(--muted)" }}>{spot.price_level}</span>}
                      </div>
                      {spot.category && (
                        <div className="text-[10px] font-medium px-2 py-0.5 rounded-full" style={{ background: "var(--surface)", color: "var(--muted)", border: "1px solid var(--border)" }}>
                          {spot.category}
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
          <p className="font-semibold mb-1" style={{ color: "var(--ink)" }}>No spots found</p>
          <p className="text-sm" style={{ color: "var(--muted)" }}>Try a different search or filter</p>
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
