"use client";

import Link from "next/link";
import AskCard from "@/components/AskCard";
import { useLang } from "@/lib/LanguageContext";

const T = {
  en: {
    eyebrow: "Bapmap Guides",
    title: "Know before you go.",
    subtitle: "Real places, written by someone who actually eats here.",
    empty: "Guides coming soon.",
  },
  ja: {
    eyebrow: "Bapmapガイド",
    title: "行く前に知っておこう。",
    subtitle: "実際に食べた人が書いた、リアルなグルメガイド。",
    empty: "ガイドは近日公開予定。",
  },
};

type Guide = {
  id: string;
  slug: string;
  title: string;
  subtitle: string;
  title_ja?: string;
  subtitle_ja?: string;
  cover_image: string;
  category_tag: string;
  created_at: string;
};

export default function GuidesClient({ guides }: { guides: Guide[] }) {
  const { lang, p } = useLang();
  const t = T[lang];
  const isJa = lang === "ja";

  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      <div className="mb-14">
        <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-3" style={{ color: "var(--orange)" }}>
          {t.eyebrow}
        </p>
        <h1
          className="font-display m-0"
          style={{ fontSize: "clamp(2.5rem,6vw,4rem)", color: "var(--ink)", letterSpacing: "-0.03em", lineHeight: 1.05 }}
        >
          {t.title}
        </h1>
        <p className="mt-4 text-base leading-relaxed" style={{ color: "var(--muted)", maxWidth: "560px" }}>
          {t.subtitle}
        </p>
      </div>

      {guides.length === 0 ? (
        <p style={{ color: "var(--muted)" }}>{t.empty}</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {guides.map((guide) => (
            <Link key={guide.id} href={p(`/guides/${guide.slug}`)} className="group block no-underline">
              <article
                className="rounded-2xl overflow-hidden border border-[var(--border)] transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-xl"
                style={{ background: "var(--surface)" }}
              >
                <div className="relative overflow-hidden" style={{ height: "240px" }}>
                  {guide.cover_image ? (
                    <img
                      src={guide.cover_image}
                      alt={guide.title}
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                    />
                  ) : (
                    <div className="w-full h-full" style={{ background: "var(--ink)" }} />
                  )}
                  <div
                    className="absolute inset-0"
                    style={{ background: "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.1) 60%)" }}
                  />
                  {guide.category_tag && (
                    <div className="absolute top-4 left-4">
                      <span
                        className="text-[9px] font-bold tracking-[0.2em] uppercase px-2.5 py-1 rounded-full"
                        style={{ background: "var(--orange)", color: "#fff" }}
                      >
                        {guide.category_tag}
                      </span>
                    </div>
                  )}
                  <div className="absolute bottom-0 left-0 p-6">
                    <h2
                      className="font-display text-white m-0 leading-tight"
                      style={{ fontSize: "1.4rem", letterSpacing: "-0.02em" }}
                    >
                      {isJa && guide.title_ja ? guide.title_ja : guide.title}
                    </h2>
                  </div>
                </div>
                {(guide.subtitle || guide.subtitle_ja) && (
                  <div className="px-5 py-4" style={{ height: "78px", overflow: "hidden" }}>
                    <p className="text-sm leading-relaxed m-0 line-clamp-2" style={{ color: "var(--muted)" }}>
                      {isJa && guide.subtitle_ja ? guide.subtitle_ja : guide.subtitle}
                    </p>
                  </div>
                )}
              </article>
            </Link>
          ))}
          <AskCard />
        </div>
      )}
    </div>
  );
}
