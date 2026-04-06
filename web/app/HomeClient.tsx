"use client";

import Link from "next/link";
import type { Spot } from "@/lib/supabase";
import SpotCard from "./SpotCard";
import SearchBar from "./SearchBar";
import MessageTicker from "@/components/MessageTicker";
import { useLang } from "@/lib/LanguageContext";

const T = {
  en: {
    eyebrow: "Korean Food · Mapped for You",
    subtitle: "Follow the locals. Eat like one.",
    aiHint: "✦ AI-powered · Ask anything about Korean food & culture",
    cards: [
      { title: "Spots", desc: "Every place here is somewhere we've actually eaten.", badge: (n: number) => `${n}+ spots` },
      { title: "By Location", desc: "Seoul, Gangwon, Jeju — browse by where you're headed.", badge: "Interactive map" },
      { title: "About", desc: "Bad at English. Great at eating. The story behind Bapmap.", badge: "My story" },
    ],
    statsLabels: ["Spots Curated", "Cities", "Personally Visited", "Tourist Traps"],
    whyEyebrow: "Why Bapmap",
    whyTitle: "Not your average food guide",
    whyItems: [
      { title: "We ate here. All of it.", desc: "Every single spot on Bapmap is somewhere we've personally visited and eaten at. No desk research, no stock photos of food we've never tasted." },
      { title: "Zero ads. Zero sponsors.", desc: "No restaurant has paid to be featured here. We pick based on taste, value, and vibe — nothing else. If we don't like it, it doesn't make the cut." },
      { title: "Built for foreigners.", desc: "We know what it's like to not read the menu. Every recommendation comes with context you actually need: subway stop, price range, what to order." },
    ],
    guidesEyebrow: "Bapmap Guides",
    guidesTitle: "Know before you go.",
    allGuides: "All guides →",
    spotsEyebrow: "Latest Bapmap Picks",
    spotsTitle: "Recent Posts.",
    allSpots: "All spots →",
    ctaEyebrow: "Ready to eat?",
    ctaTitle: "Find your next meal in Korea",
    ctaBtn: "Browse All Spots →",
  },
  ja: {
    eyebrow: "韓国グルメ · あなたのための地図",
    subtitle: "地元の人が行く店へ。地元の人のように食べる。",
    aiHint: "✦ AI搭載 · 韓国グルメ・文化について何でも聞いてください",
    cards: [
      { title: "スポット", desc: "ここにあるすべての場所は、実際に食べた店です。", badge: (n: number) => `${n}+ スポット` },
      { title: "エリアから探す", desc: "ソウル、江原道、済州島 — 行き先でブラウズ。", badge: "インタラクティブマップ" },
      { title: "について", desc: "英語は苦手。食べることは得意。Bapmapのストーリー。", badge: "ストーリー" },
    ],
    statsLabels: ["掲載スポット数", "都市", "実際に訪問済み", "観光客向け店"],
    whyEyebrow: "Bapmapとは",
    whyTitle: "普通のグルメガイドじゃない",
    whyItems: [
      { title: "全部、実際に食べました。", desc: "Bapmapに掲載されているすべてのスポットは、実際に訪れて食べた場所です。デスクリサーチなし、食べたことのない料理のストック写真もなし。" },
      { title: "広告なし。スポンサーなし。", desc: "掲載料を払ったレストランはゼロ。味・コスパ・雰囲気だけで選んでいます。気に入らなければ掲載しません。" },
      { title: "外国人のために作りました。", desc: "メニューが読めない気持ち、わかります。すべてのおすすめには、本当に必要な情報が付いています：最寄り駅、価格帯、注文すべきもの。" },
    ],
    guidesEyebrow: "Bapmapガイド",
    guidesTitle: "行く前に知っておこう。",
    allGuides: "すべてのガイド →",
    spotsEyebrow: "最新スポット",
    spotsTitle: "新着情報",
    allSpots: "すべてのスポット →",
    ctaEyebrow: "食べる準備はできた？",
    ctaTitle: "韓国での次の食事を見つけよう",
    ctaBtn: "すべてのスポットを見る →",
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
};

type Message = { id: string; message: string; reply: string };

export default function HomeClient({
  recent,
  messages,
  guides,
  spotCount,
}: {
  recent: Spot[];
  messages: Message[];
  guides: Guide[];
  spotCount: number;
}) {
  const { lang } = useLang();
  const t = T[lang];
  const isJa = lang === "ja";

  return (
    <div>
      {/* ── HERO ── */}
      <section className="relative flex flex-col overflow-hidden" style={{ height: "100svh", minHeight: "600px" }}>
        <div className="absolute inset-0 bg-cover scale-105" style={{ backgroundImage: "url('/hero.jpg')", backgroundPosition: "center 40%", willChange: "transform" }} />
        <div className="absolute inset-0" style={{ background: "linear-gradient(160deg, rgba(8,6,4,0.62) 0%, rgba(8,6,4,0.28) 40%, rgba(8,6,4,0.85) 100%)" }} />
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")", backgroundSize: "200px" }} />

        <div className="relative flex-1 flex flex-col items-center justify-center px-4 text-center" style={{ paddingBottom: "80px" }}>
          <div className="animate-fadeUp delay-1 flex items-center gap-3 mb-0">
            <div style={{ width: "32px", height: "1px", background: "rgba(245,166,35,0.7)" }} />
            <p className="text-white/60 text-[10px] font-semibold tracking-[0.35em] uppercase">{t.eyebrow}</p>
            <div style={{ width: "32px", height: "1px", background: "rgba(245,166,35,0.7)" }} />
          </div>
          <h1 className="font-display animate-fadeUp delay-2 text-white" style={{ fontSize: "clamp(6rem,18vw,14rem)", letterSpacing: "-0.035em", lineHeight: 0.9, textShadow: "0 4px 40px rgba(0,0,0,0.3)" }}>
            Bapmap
          </h1>
          <p className="animate-fadeUp delay-4 text-white/65 font-light mt-14 max-w-sm leading-relaxed" style={{ fontSize: "clamp(0.95rem,2vw,1.2rem)", letterSpacing: "0.01em" }}>
            {t.subtitle}
          </p>
          <div className="animate-fadeUp delay-4 mt-10 w-full px-4" style={{ maxWidth: "520px" }}>
            <p className="text-white/80 text-xs text-center mb-3 tracking-wide">{t.aiHint}</p>
            <SearchBar />
          </div>
        </div>
        <div className="absolute bottom-0 left-0 right-0" style={{ height: "200px", background: "linear-gradient(to bottom, transparent, rgba(8,6,4,0.6))" }} />
      </section>

      {/* ── NAV CARDS ── */}
      <div className="relative z-10 px-6" style={{ marginTop: "-110px" }}>
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { ...t.cards[0], href: "/spots", img: "/card-spots.jpg", badgeVal: typeof t.cards[0].badge === "function" ? t.cards[0].badge(spotCount) : t.cards[0].badge },
            { ...t.cards[1], href: "/map", img: "/card-location.jpg", badgeVal: t.cards[1].badge as string },
            { ...t.cards[2], href: "/about", img: "/card-about.jpg", badgeVal: t.cards[2].badge as string },
          ].map((card) => (
            <Link key={card.href} href={card.href} className="group block no-underline relative rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-1.5" style={{ height: "220px", boxShadow: "0 16px 48px rgba(0,0,0,0.25), 0 2px 8px rgba(0,0,0,0.1)" }}>
              <img src={card.img} alt={card.title} className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
              <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 55%, rgba(0,0,0,0.05) 100%)" }} />
              <div className="absolute top-4 left-4">
                <span className="text-[9px] font-bold tracking-[0.2em] uppercase px-2.5 py-1 rounded-full" style={{ background: "var(--orange)", color: "#fff" }}>{card.badgeVal}</span>
              </div>
              <div className="absolute bottom-0 left-0 p-5">
                <div className="font-display text-white text-xl font-bold mb-1.5 leading-tight">{card.title}</div>
                <p className="text-white/65 text-xs leading-relaxed">{card.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ── MESSAGE TICKER ── */}
      <MessageTicker messages={messages} />

      {/* ── STATS ── */}
      <section className="bg-white" style={{ paddingTop: "6rem", paddingBottom: "5rem" }}>
        <div className="max-w-4xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-0">
            {[
              { value: `${spotCount}+`, label: t.statsLabels[0] },
              { value: "5+", label: t.statsLabels[1] },
              { value: "100%", label: t.statsLabels[2] },
              { value: "0", label: t.statsLabels[3] },
            ].map((stat, i) => (
              <div key={stat.label} className="text-center py-6" style={{ borderLeft: i > 0 ? "1px solid var(--border)" : "none" }}>
                <div className="font-display leading-none mb-2" style={{ fontSize: "3.5rem", color: "var(--orange)" }}>{stat.value}</div>
                <div className="text-[10px] font-bold tracking-[0.2em] uppercase" style={{ color: "var(--muted)" }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── WHY BAPMAP ── */}
      <section className="border-t border-b border-[var(--border)]" style={{ background: "var(--surface)", paddingTop: "5rem", paddingBottom: "5rem" }}>
        <div className="max-w-4xl mx-auto px-6">
          <div className="mb-14 text-center">
            <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-3" style={{ color: "var(--orange)" }}>{t.whyEyebrow}</p>
            <h2 className="font-display m-0" style={{ fontSize: "clamp(2rem,5vw,3.2rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.1 }}>{t.whyTitle}</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            {t.whyItems.map((item, i) => (
              <div key={i} className="flex flex-col">
                <div className="rounded-2xl overflow-hidden mb-6" style={{ height: "180px" }}>
                  <img src={["/why-eat.jpg", "/why-honest.jpg", "/why-travel.jpg"][i]} alt={item.title} className="w-full h-full object-cover" />
                </div>
                <div className="flex items-start gap-4">
                  <span className="font-display flex-shrink-0 mt-0.5" style={{ fontSize: "1.5rem", color: "var(--orange)", lineHeight: 1, opacity: 0.4 }}>
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <div>
                    <div className="font-bold text-sm mb-2" style={{ color: "var(--ink)" }}>{item.title}</div>
                    <p className="text-sm leading-relaxed m-0" style={{ color: "var(--muted)" }}>{item.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── GUIDES ── */}
      {guides.length > 0 && (
        <section className="max-w-4xl mx-auto px-6" style={{ paddingTop: "5rem", paddingBottom: "5rem" }}>
          <div className="flex items-end justify-between mb-10">
            <div>
              <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-3" style={{ color: "var(--orange)" }}>{t.guidesEyebrow}</p>
              <h2 className="font-display m-0" style={{ fontSize: "clamp(2rem,5vw,3.2rem)", color: "var(--ink)", letterSpacing: "-0.02em" }}>{t.guidesTitle}</h2>
            </div>
            <Link href="/guides" className="text-sm font-bold no-underline hover:opacity-60 transition-opacity" style={{ color: "var(--orange)" }}>{t.allGuides}</Link>
          </div>
          <div className="flex flex-col gap-5">
            {guides[0] && (
              <Link href={`/guides/${guides[0].slug}`} className="group block no-underline">
                <article className="rounded-2xl overflow-hidden border border-[var(--border)] transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-xl" style={{ background: "var(--surface)" }}>
                  <div className="relative overflow-hidden" style={{ height: "380px" }}>
                    {guides[0].cover_image ? <img src={guides[0].cover_image} alt={guides[0].title} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" /> : <div className="w-full h-full" style={{ background: "var(--ink)" }} />}
                    <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.1) 55%)" }} />
                    {guides[0].category_tag && <div className="absolute top-4 left-4"><span className="text-[9px] font-bold tracking-[0.2em] uppercase px-2.5 py-1 rounded-full" style={{ background: "var(--orange)", color: "#fff" }}>{guides[0].category_tag}</span></div>}
                    <div className="absolute bottom-0 left-0 p-7">
                      <h3 className="font-display text-white m-0 leading-tight" style={{ fontSize: "clamp(1.6rem,3vw,2.2rem)", letterSpacing: "-0.02em" }}>{isJa && guides[0].title_ja ? guides[0].title_ja : guides[0].title}</h3>
                      {(guides[0].subtitle || guides[0].subtitle_ja) && <p className="text-sm text-white/70 mt-2 m-0 line-clamp-2" style={{ maxWidth: "560px" }}>{isJa && guides[0].subtitle_ja ? guides[0].subtitle_ja : guides[0].subtitle}</p>}
                    </div>
                  </div>
                </article>
              </Link>
            )}
            {guides.length > 1 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {guides.slice(1).map((guide) => (
                  <Link key={guide.id} href={`/guides/${guide.slug}`} className="group block no-underline">
                    <article className="rounded-2xl overflow-hidden border border-[var(--border)] transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-xl" style={{ background: "var(--surface)" }}>
                      <div className="relative overflow-hidden" style={{ height: "220px" }}>
                        {guide.cover_image ? <img src={guide.cover_image} alt={guide.title} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" /> : <div className="w-full h-full" style={{ background: "var(--ink)" }} />}
                        <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.1) 60%)" }} />
                        {guide.category_tag && <div className="absolute top-4 left-4"><span className="text-[9px] font-bold tracking-[0.2em] uppercase px-2.5 py-1 rounded-full" style={{ background: "var(--orange)", color: "#fff" }}>{guide.category_tag}</span></div>}
                        <div className="absolute bottom-0 left-0 p-5">
                          <h3 className="font-display text-white m-0 leading-tight" style={{ fontSize: "1.2rem", letterSpacing: "-0.02em" }}>{isJa && guide.title_ja ? guide.title_ja : guide.title}</h3>
                        </div>
                      </div>
                      {(guide.subtitle || guide.subtitle_ja) && <div className="px-4 py-3"><p className="text-xs leading-relaxed m-0 line-clamp-2" style={{ color: "var(--muted)" }}>{isJa && guide.subtitle_ja ? guide.subtitle_ja : guide.subtitle}</p></div>}
                    </article>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>
      )}

      {/* ── LATEST SPOTS ── */}
      {recent.length > 0 && (
        <section className="max-w-4xl mx-auto px-6" style={{ paddingTop: "5rem", paddingBottom: "5rem" }}>
          <div className="flex items-end justify-between mb-10">
            <div>
              <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-3" style={{ color: "var(--orange)" }}>{t.spotsEyebrow}</p>
              <h2 className="font-display m-0" style={{ fontSize: "clamp(2rem,5vw,3.2rem)", color: "var(--ink)", letterSpacing: "-0.02em" }}>{t.spotsTitle}</h2>
            </div>
            <Link href="/spots" className="text-sm font-bold no-underline hover:opacity-60 transition-opacity" style={{ color: "var(--orange)" }}>{t.allSpots}</Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {recent.map((spot) => <SpotCard key={spot.id} spot={spot} />)}
          </div>
        </section>
      )}

      {/* ── BOTTOM CTA ── */}
      <section className="relative text-center overflow-hidden" style={{ paddingTop: "7rem", paddingBottom: "7rem" }}>
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: "url('/seoul-cta.jpg')", backgroundPosition: "center 60%" }} />
        <div className="absolute inset-0" style={{ background: "linear-gradient(to bottom, rgba(0,0,0,0.55), rgba(0,0,0,0.7))" }} />
        <div className="relative z-10">
          <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-4" style={{ color: "var(--orange)" }}>{t.ctaEyebrow}</p>
          <h2 className="font-display mb-6 text-white" style={{ fontSize: "clamp(2rem,5vw,3rem)", letterSpacing: "-0.02em" }}>{t.ctaTitle}</h2>
          <Link href="/spots" className="inline-flex items-center gap-2 no-underline font-semibold text-sm px-8 py-3.5 rounded-full text-white transition-all duration-200 hover:opacity-85" style={{ background: "var(--orange)", boxShadow: "0 4px 24px rgba(245,166,35,0.4)" }}>
            {t.ctaBtn}
          </Link>
        </div>
      </section>
    </div>
  );
}
