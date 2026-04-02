import { supabase } from "@/lib/supabase";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Link from "next/link";

async function getSpot(slug: string) {
  const { data: spots } = await supabase
    .from("spots")
    .select("*")
    .eq("status", "업로드완료");
  return spots?.find((s) => {
    const s_slug = (s.english_name || s.name).toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
    return s_slug === slug;
  }) ?? null;
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const spot = await getSpot(slug);
  if (!spot) return {};

  const title = `${spot.english_name || spot.name} — Bapmap`;
  const description = `${spot.english_name || spot.name} in ${spot.region || spot.city}, Korea. ★${spot.rating} · ${spot.price_level || "Local pick"} · ${spot.subway || ""}`.trim();

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `https://bapmap.com/spots/${slug}`,
      images: spot.image_url ? [{ url: spot.image_url, width: 800, height: 600, alt: spot.english_name }] : [],
      type: "article",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: spot.image_url ? [spot.image_url] : [],
    },
  };
}

export default async function SpotPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const spot = await getSpot(slug);
  if (!spot) notFound();

  const images: string[] = Array.isArray(spot.image_urls) && spot.image_urls.length > 0
    ? spot.image_urls
    : spot.image_url ? [spot.image_url] : [];

  return (
    <div>
      {/* ── 이미지 갤러리 ── */}
      {images.length > 0 && (
        <div className={`grid gap-2 ${images.length >= 3 ? "grid-cols-3" : images.length === 2 ? "grid-cols-2" : "grid-cols-1"}`} style={{ maxHeight: "480px" }}>
          {images.slice(0, 3).map((url, i) => (
            <div key={i} className={`overflow-hidden bg-gray-100 ${images.length === 1 ? "col-span-1" : ""}`} style={{ height: "480px" }}>
              <img
                src={url}
                alt={`${spot.english_name || spot.name} ${i + 1}`}
                className="w-full h-full object-cover"
              />
            </div>
          ))}
        </div>
      )}

      {/* ── 본문 ── */}
      <div className="max-w-2xl mx-auto px-6 py-12">

        {/* 브레드크럼 */}
        <div className="flex items-center gap-2 text-xs mb-6" style={{ color: "var(--muted)" }}>
          <Link href="/spots" className="no-underline hover:opacity-70" style={{ color: "var(--muted)" }}>Spots</Link>
          <span>›</span>
          <span style={{ color: "var(--orange)" }}>{spot.region || spot.city}</span>
        </div>

        {/* 헤더 */}
        <div className="mb-8">
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-2" style={{ color: "var(--orange)" }}>
            {spot.region || spot.city}
          </p>
          <h1 className="font-display mb-4" style={{ fontSize: "clamp(2rem,5vw,3rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
            {spot.english_name || spot.name}
          </h1>

          {/* 배지들 */}
          <div className="flex flex-wrap gap-2">
            <span className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
              ★ {spot.rating} · {spot.rating_count?.toLocaleString()} reviews
            </span>
            {spot.price_level && (
              <span className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
                {spot.price_level}
              </span>
            )}
            {spot.subway && (
              <span className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
                🚇 {spot.subway}
              </span>
            )}
            {spot.category && (
              <span className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
                {spot.category}
              </span>
            )}
          </div>
        </div>

        <div className="border-t border-[var(--border)] mb-8" />

        {/* 본문 글 */}
        {spot.content ? (
          <div className="mb-10">
            {spot.content.split("\n\n").map((block: string, i: number) => {
              const lines = block.split("\n").filter((l: string) => l.trim());
              // 소제목 감지: 한 줄이고 30자 이하이며 문장이 아닌 경우
              const isHeading = lines.length === 1 && lines[0].length <= 40 && !lines[0].endsWith(".");
              if (isHeading) {
                return (
                  <h2 key={i} className="font-bold mt-10 mb-3" style={{ fontSize: "1.1rem", color: "var(--ink)" }}>
                    {lines[0]}
                  </h2>
                );
              }
              return (
                <p key={i} className="mb-6" style={{
                  fontSize: i === 0 ? "1.15rem" : "1rem",
                  lineHeight: "1.9",
                  color: i === 0 ? "var(--ink)" : "var(--muted)",
                  fontWeight: i === 0 ? 400 : 400,
                }}>
                  {lines.map((line: string, j: number) => (
                    <span key={j}>{line}{j < lines.length - 1 && <br />}</span>
                  ))}
                </p>
              );
            })}
          </div>
        ) : (
          <p className="mb-10" style={{ color: "var(--muted)" }}>Content coming soon.</p>
        )}

        <div className="border-t border-[var(--border)] mb-8" />

        {/* 영업시간 */}
        {spot.hours && (
          <div className="mb-8">
            <p className="text-xs font-bold tracking-[0.2em] uppercase mb-3" style={{ color: "var(--orange)" }}>Hours</p>
            <div className="text-sm leading-relaxed" style={{ color: "var(--muted)" }}>
              {spot.hours.split("\n").map((line: string, i: number) => (
                <div key={i}>{line}</div>
              ))}
            </div>
          </div>
        )}

        {/* 구글맵 버튼 */}
        {spot.google_maps_url && (
          <a
            href={spot.google_maps_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 font-bold text-sm px-6 py-3 rounded-full text-white no-underline transition-opacity hover:opacity-80"
            style={{ background: "var(--orange)" }}
          >
            Open in Google Maps →
          </a>
        )}
      </div>
    </div>
  );
}
