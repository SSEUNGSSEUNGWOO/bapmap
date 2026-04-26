"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useLang } from "@/lib/LanguageContext";
import { translateSubway } from "@/lib/translateSubway";
import type { Spot } from "@/lib/supabase";

const T = {
  en: {
    guidesLink: "Guides",
    viewBtn: "View →",
    backLink: "← All Guides",
  },
  ja: {
    guidesLink: "ガイド",
    viewBtn: "見る →",
    backLink: "← ガイド一覧",
  },
};

const markdownComponents = {
  h2: ({ children }: { children?: React.ReactNode }) => (
    <h2 className="font-display mt-10 mb-4" style={{ fontSize: "1.6rem", color: "var(--ink)", letterSpacing: "-0.02em" }}>{children}</h2>
  ),
  h3: ({ children }: { children?: React.ReactNode }) => (
    <h3 className="font-semibold mt-8 mb-3" style={{ fontSize: "1.1rem", color: "var(--ink)" }}>{children}</h3>
  ),
  p: ({ children }: { children?: React.ReactNode }) => (
    <p className="mb-5 leading-relaxed" style={{ color: "var(--ink)" }}>{children}</p>
  ),
  strong: ({ children }: { children?: React.ReactNode }) => (
    <strong style={{ color: "var(--ink)", fontWeight: 700 }}>{children}</strong>
  ),
  ul: ({ children }: { children?: React.ReactNode }) => (
    <ul className="mb-5 pl-5 space-y-1" style={{ color: "var(--muted)" }}>{children}</ul>
  ),
  li: ({ children }: { children?: React.ReactNode }) => (
    <li className="leading-relaxed">{children}</li>
  ),
  hr: () => (
    <hr className="my-10" style={{ borderColor: "var(--border)" }} />
  ),
};

type Segment =
  | { type: "text"; content: string }
  | { type: "spot"; name: string };

function SpotFeature({ spot, index, viewLabel, isJa }: { spot: Spot; index: number; viewLabel: string; isJa: boolean }) {
  const { p } = useLang();
  const slug = (spot.english_name || spot.name)
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^\w-]/g, "");

  const image = Array.isArray(spot.image_urls) && spot.image_urls.length > 0
    ? spot.image_urls[0]
    : spot.image_url;

  return (
    <div className="my-12 -mx-6" style={{ borderTop: "1px solid var(--border)", borderBottom: "1px solid var(--border)" }}>
      {image && (
        <div className="overflow-hidden" style={{ height: "340px" }}>
          <img src={image} alt={spot.english_name || spot.name} className="w-full h-full object-cover" />
        </div>
      )}
      <div className="px-6 py-7">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-[9px] font-bold tracking-[0.25em] uppercase mb-2" style={{ color: "var(--orange)" }}>
              {String(index + 1).padStart(2, "0")} · {spot.region || spot.city}
            </p>
            <h3
              className="font-display m-0 leading-tight"
              style={{ fontSize: "clamp(1.6rem, 4vw, 2.2rem)", color: "var(--ink)", letterSpacing: "-0.02em" }}
            >
              {spot.english_name || spot.name}
            </h3>
            {spot.tagline && (
              <p className="mt-2 text-sm italic" style={{ color: "var(--muted)" }}>
                "{spot.tagline}"
              </p>
            )}
          </div>
          <Link
            href={p(`/spots/${slug}`)}
            className="shrink-0 text-xs font-bold no-underline px-4 py-2 rounded-full transition-opacity hover:opacity-70"
            style={{ background: "var(--orange)", color: "#fff", marginTop: "4px" }}
          >
            {viewLabel}
          </Link>
        </div>
        <div className="flex flex-wrap gap-2 mt-4">
          {spot.category && (
            <span className="text-[10px] font-medium px-2.5 py-1 rounded-full" style={{ background: "var(--surface)", color: "var(--muted)", border: "1px solid var(--border)" }}>
              {spot.category}
            </span>
          )}
          {spot.price_level && (
            <span className="text-[10px] font-medium px-2.5 py-1 rounded-full" style={{ background: "var(--surface)", color: "var(--muted)", border: "1px solid var(--border)" }}>
              {spot.price_level}
            </span>
          )}
          {spot.subway && (
            <span className="text-[10px] font-medium px-2.5 py-1 rounded-full" style={{ background: "var(--surface)", color: "var(--muted)", border: "1px solid var(--border)" }}>
              🚇 {isJa ? translateSubway(spot.subway) : spot.subway}
            </span>
          )}
          {spot.rating && (
            <span className="text-[10px] font-medium px-2.5 py-1 rounded-full" style={{ background: "var(--surface)", color: "var(--muted)", border: "1px solid var(--border)" }}>
              ★ {spot.rating}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

type GuideData = {
  title: string;
  subtitle?: string;
  cover_image?: string;
  category_tag?: string;
  intro?: string;
  body?: string;
  title_ja?: string;
  subtitle_ja?: string;
  intro_ja?: string;
  body_ja?: string;
};

type Props = {
  guide: GuideData;
  spots: Spot[];
  segments: Segment[];
  segmentsJa: Segment[];
  spotMap: Record<string, Spot>;
  hasInlineSpots: boolean;
};

export default function GuideContent({ guide: g, spots, segments, segmentsJa, spotMap, hasInlineSpots }: Props) {
  const { lang, p } = useLang();
  const t = T[lang];
  const isJa = lang === "ja";

  const title = isJa && g.title_ja ? g.title_ja : g.title;
  const subtitle = isJa && g.subtitle_ja ? g.subtitle_ja : g.subtitle;
  const intro = isJa && g.intro_ja ? g.intro_ja : g.intro;
  const activeSegments = isJa && segmentsJa.length > 0 ? segmentsJa : segments;

  let spotIndex = 0;

  return (
    <div>
      {/* ── HERO ── */}
      <div className="relative overflow-hidden" style={{ height: "70vh", minHeight: "480px" }}>
        {g.cover_image ? (
          <img src={g.cover_image} alt={title} className="absolute inset-0 w-full h-full object-cover" />
        ) : (
          <div className="absolute inset-0" style={{ background: "var(--ink)" }} />
        )}
        <div
          className="absolute inset-0"
          style={{ background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 60%)" }}
        />
        <div className="absolute bottom-0 left-0 right-0 px-8 pb-12 max-w-4xl mx-auto">
          <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-4" style={{ color: "var(--orange)" }}>
            <Link href={p("/guides")} style={{ color: "var(--orange)", textDecoration: "none" }}>{t.guidesLink}</Link>
            {g.category_tag && <> / {g.category_tag}</>}
          </p>
          <h1
            className="font-display text-white m-0 leading-tight"
            style={{ fontSize: "clamp(2.2rem,6vw,4rem)", letterSpacing: "-0.03em" }}
          >
            {title}
          </h1>
          {subtitle && (
            <p className="mt-3 text-white/70 text-base leading-relaxed" style={{ maxWidth: "560px" }}>
              {subtitle}
            </p>
          )}
        </div>
      </div>

      {/* ── CONTENT ── */}
      <div className="max-w-4xl mx-auto px-6 py-14">
        {intro && (
          <div className="mb-14" style={{ maxWidth: "640px" }}>
            <p
              className="text-lg leading-relaxed m-0"
              style={{ color: "var(--ink)", fontStyle: "italic", borderLeft: "3px solid var(--orange)", paddingLeft: "1.25rem" }}
            >
              {intro}
            </p>
          </div>
        )}

        {activeSegments.length > 0 && (
          <div>
            {activeSegments.map((seg, i) => {
              if (seg.type === "text") {
                return (
                  <div key={i} className="prose prose-lg max-w-2xl" style={{ color: "var(--ink)", lineHeight: 1.8 }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                      {seg.content}
                    </ReactMarkdown>
                  </div>
                );
              }
              const spot = spotMap[seg.name];
              if (!spot) return null;
              const idx = spotIndex++;
              return <SpotFeature key={i} spot={spot} index={idx} viewLabel={t.viewBtn} isJa={isJa} />;
            })}
          </div>
        )}

        {!hasInlineSpots && spots.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-10">
            {spots.map((spot) => {
              const slug2 = (spot.english_name || spot.name)
                .toLowerCase()
                .replace(/\s+/g, "-")
                .replace(/[^\w-]/g, "");
              return (
                <Link key={spot.id} href={p(`/spots/${slug2}`)} className="group block no-underline h-full">
                  <div className="bg-white rounded-2xl overflow-hidden border border-[var(--border)] group-hover:shadow-xl group-hover:-translate-y-1 transition-all duration-200 h-full flex flex-col">
                    {spot.image_url && (
                      <div className="h-48 overflow-hidden">
                        <img src={spot.image_url} alt={spot.english_name || spot.name} className="w-full h-full object-cover" />
                      </div>
                    )}
                    <div className="p-4 flex flex-col flex-1">
                      <div className="text-[10px] font-bold tracking-widest uppercase mb-1" style={{ color: "var(--orange)" }}>{spot.region || spot.city}</div>
                      <div className="font-semibold text-sm line-clamp-2" style={{ color: "var(--ink)" }}>{spot.english_name || spot.name}</div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}

        <div className="mt-14 pt-8 border-t border-[var(--border)]">
          <Link href={p("/guides")} className="text-sm font-bold no-underline hover:opacity-60 transition-opacity" style={{ color: "var(--orange)" }}>
            {t.backLink}
          </Link>
        </div>
      </div>
    </div>
  );
}
