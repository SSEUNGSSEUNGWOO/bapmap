import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Link from "next/link";
import SpotCard from "@/app/SpotCard";
import { Suspense } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export const revalidate = 300;

type Guide = {
  id: string;
  slug: string;
  title: string;
  subtitle: string;
  cover_image: string;
  category_tag: string;
  intro: string;
  body: string;
  spot_slugs: string[];
  created_at: string;
};

export async function generateStaticParams() {
  const { data } = await supabase
    .from("guides")
    .select("slug")
    .eq("status", "published");
  return (data ?? []).map((g) => ({ slug: g.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const { data } = await supabase
    .from("guides")
    .select("title, subtitle")
    .eq("slug", slug)
    .single();
  if (!data) return {};
  return {
    title: `${data.title} | Bapmap`,
    description: data.subtitle || "",
  };
}

export default async function GuidePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  const { data: guide } = await supabase
    .from("guides")
    .select("*")
    .eq("slug", slug)
    .eq("status", "published")
    .single();

  if (!guide) notFound();

  const g = guide as Guide;

  // spot_slugs로 스팟 fetch
  let spots: Spot[] = [];
  if (g.spot_slugs && g.spot_slugs.length > 0) {
    const conditions = g.spot_slugs.map((s) => {
      const normalized = s.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
      return `english_name.ilike.${normalized.replace(/-/g, " ")}`;
    });

    const { data: spotData } = await supabase
      .from("spots")
      .select("id, name, english_name, city, region, image_url, image_urls, rating, category, price_level, subway, tagline")
      .eq("status", "업로드완료")
      .in(
        "english_name",
        g.spot_slugs.map((s) =>
          s.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")
        )
      );
    spots = (spotData ?? []) as Spot[];
  }

  return (
    <div>
      {/* ── HERO ── */}
      <div className="relative overflow-hidden" style={{ height: "70vh", minHeight: "480px" }}>
        {g.cover_image ? (
          <img
            src={g.cover_image}
            alt={g.title}
            className="absolute inset-0 w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0" style={{ background: "var(--ink)" }} />
        )}
        <div
          className="absolute inset-0"
          style={{ background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 60%)" }}
        />
        <div className="absolute bottom-0 left-0 right-0 px-8 pb-12 max-w-4xl mx-auto">
          <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-4" style={{ color: "var(--orange)" }}>
            <Link href="/guides" style={{ color: "var(--orange)", textDecoration: "none" }}>Guides</Link>
            {g.category_tag && <> / {g.category_tag}</>}
          </p>
          <h1
            className="font-display text-white m-0 leading-tight"
            style={{ fontSize: "clamp(2.2rem,6vw,4rem)", letterSpacing: "-0.03em" }}
          >
            {g.title}
          </h1>
          {g.subtitle && (
            <p className="mt-3 text-white/70 text-base leading-relaxed" style={{ maxWidth: "560px" }}>
              {g.subtitle}
            </p>
          )}
        </div>
      </div>

      {/* ── CONTENT ── */}
      <div className="max-w-4xl mx-auto px-6 py-14">
        {/* Intro */}
        {g.intro && (
          <div className="mb-14" style={{ maxWidth: "640px" }}>
            <p
              className="text-lg leading-relaxed m-0"
              style={{ color: "var(--ink)", fontStyle: "italic", borderLeft: "3px solid var(--orange)", paddingLeft: "1.25rem" }}
            >
              {g.intro}
            </p>
          </div>
        )}

        {/* Body */}
        {g.body && (
          <div
            className="mb-14 prose prose-lg max-w-2xl"
            style={{
              color: "var(--ink)",
              lineHeight: 1.8,
            }}
          >
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h2: ({ children }) => (
                  <h2 className="font-display mt-10 mb-4" style={{ fontSize: "1.6rem", color: "var(--ink)", letterSpacing: "-0.02em" }}>{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="font-semibold mt-8 mb-3" style={{ fontSize: "1.1rem", color: "var(--ink)" }}>{children}</h3>
                ),
                p: ({ children }) => (
                  <p className="mb-5 leading-relaxed" style={{ color: "var(--ink)" }}>{children}</p>
                ),
                strong: ({ children }) => (
                  <strong style={{ color: "var(--ink)", fontWeight: 700 }}>{children}</strong>
                ),
                ul: ({ children }) => (
                  <ul className="mb-5 pl-5 space-y-1" style={{ color: "var(--muted)" }}>{children}</ul>
                ),
                li: ({ children }) => (
                  <li className="leading-relaxed">{children}</li>
                ),
                hr: () => (
                  <hr className="my-10" style={{ borderColor: "var(--border)" }} />
                ),
              }}
            >
              {g.body}
            </ReactMarkdown>
          </div>
        )}

        {/* Spots */}
        {spots.length > 0 && (
          <Suspense>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {spots.map((spot) => (
                <SpotCard key={spot.id} spot={spot} />
              ))}
            </div>
          </Suspense>
        )}

        {/* Back */}
        <div className="mt-14 pt-8 border-t border-[var(--border)]">
          <Link
            href="/guides"
            className="text-sm font-bold no-underline hover:opacity-60 transition-opacity"
            style={{ color: "var(--orange)" }}
          >
            ← All Guides
          </Link>
        </div>
      </div>
    </div>
  );
}
