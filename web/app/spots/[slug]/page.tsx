import { supabase } from "@/lib/supabase";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

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

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "name": spot.english_name || spot.name,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": spot.english_address || spot.address,
      "addressLocality": spot.city,
      "addressRegion": spot.region,
      "addressCountry": "KR",
    },
    "geo": spot.lat && spot.lng ? {
      "@type": "GeoCoordinates",
      "latitude": spot.lat,
      "longitude": spot.lng,
    } : undefined,
    "aggregateRating": spot.rating ? {
      "@type": "AggregateRating",
      "ratingValue": spot.rating,
      "reviewCount": spot.rating_count || 1,
      "bestRating": 5,
    } : undefined,
    "priceRange": spot.price_level || undefined,
    "servesCuisine": spot.category || undefined,
    "image": images[0] || undefined,
    "url": `https://bapmap.com/spots/${slug}`,
  };

  return (
    <div>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
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
          <div className="mb-10 prose-content">
            <ReactMarkdown
              components={{
                h1: ({ children }) => (
                  <h1 className="font-display mb-4" style={{ fontSize: "1.5rem", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.2 }}>{children}</h1>
                ),
                h2: ({ children }) => (
                  <h2 className="font-bold mt-10 mb-4 pl-4" style={{ fontSize: "1.05rem", color: "var(--ink)", borderLeft: "3px solid var(--orange)", letterSpacing: "-0.01em" }}>{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="font-bold mt-6 mb-2" style={{ fontSize: "0.95rem", color: "var(--ink)" }}>{children}</h3>
                ),
                p: ({ children }) => (
                  <p className="mb-6" style={{ fontSize: "1rem", lineHeight: "1.9", color: "var(--muted)" }}>{children}</p>
                ),
                strong: ({ children }) => (
                  <strong style={{ color: "var(--ink)", fontWeight: 600 }}>{children}</strong>
                ),
                ul: ({ children }) => (
                  <ul className="mb-6 space-y-1 pl-4" style={{ color: "var(--muted)", listStyleType: "disc" }}>{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="mb-6 space-y-1 pl-4" style={{ color: "var(--muted)", listStyleType: "decimal" }}>{children}</ol>
                ),
                li: ({ children }) => (
                  <li style={{ fontSize: "1rem", lineHeight: "1.9" }}>{children}</li>
                ),
                hr: () => (
                  <div className="border-t border-[var(--border)] my-8" />
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto mb-6">
                    <table className="w-full text-sm" style={{ borderCollapse: "collapse" }}>{children}</table>
                  </div>
                ),
                td: ({ children }) => (
                  <td className="py-2 pr-4" style={{ borderBottom: "1px solid var(--border)", color: "var(--muted)" }}>{children}</td>
                ),
                a: ({ href, children }) => (
                  <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: "var(--orange)", textDecoration: "underline" }}>{children}</a>
                ),
              }}
            >
              {spot.content}
            </ReactMarkdown>
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

        {/* 구글 리뷰 */}
        {Array.isArray(spot.google_reviews) && spot.google_reviews.length > 0 && (
          <div className="mb-8">
            <div className="border-t border-[var(--border)] mb-8" />
            <p className="text-xs font-bold tracking-[0.2em] uppercase mb-4" style={{ color: "var(--orange)" }}>What People Are Saying</p>
            <div className="space-y-4">
              {spot.google_reviews.slice(0, 3).map((review: string, i: number) => (
                <div key={i} className="p-4 rounded-xl" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
                  <p className="text-sm leading-relaxed" style={{ color: "var(--muted)" }}>"{review}"</p>
                </div>
              ))}
            </div>
            <p className="text-xs mt-3" style={{ color: "var(--border)" }}>— Google Reviews</p>
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
