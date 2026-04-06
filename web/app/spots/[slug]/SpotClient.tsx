"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useLang } from "@/lib/LanguageContext";
import { translateSubway, translateHours } from "@/lib/translateSubway";

const T = {
  en: {
    breadcrumb: "Spots",
    reviews: "reviews",
    hoursLabel: "Hours",
    whatPeopleSay: "What People Are Saying",
    googleReviews: "— Google Reviews",
    googleMaps: "Open in Google Maps →",
    moreIn: (cat: string, city: string) => `→ More ${cat} in ${city}`,
    nearbySpots: "Nearby Spots",
  },
  ja: {
    breadcrumb: "スポット",
    reviews: "件のレビュー",
    hoursLabel: "営業時間",
    whatPeopleSay: "みんなの声",
    googleReviews: "— Googleレビュー",
    googleMaps: "Google マップで開く →",
    moreIn: (cat: string, city: string) => `→ ${city}の${cat}をもっと見る`,
    nearbySpots: "近くのスポット",
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

const GOOD_FOR_JA: Record<string, string> = {
  "Solo dining": "一人飯",
  "Groups": "グループ",
  "Date night": "デート",
  "Quick lunch": "ランチ",
  "Late night": "深夜営業",
  "Vegetarian-friendly": "ベジタリアン向け",
  "Budget-friendly": "リーズナブル",
  "Special occasion": "記念日・特別な日",
  "No reservations needed": "予約不要",
  "Reservation recommended": "予約推奨",
};

const markdownComponents = {
  h1: ({ children }: { children?: React.ReactNode }) => (
    <h1 className="font-display mb-4" style={{ fontSize: "1.5rem", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.2 }}>{children}</h1>
  ),
  h2: ({ children }: { children?: React.ReactNode }) => (
    <h2 className="font-bold mt-10 mb-4 pl-4" style={{ fontSize: "1.05rem", color: "var(--ink)", borderLeft: "3px solid var(--orange)", letterSpacing: "-0.01em" }}>{children}</h2>
  ),
  h3: ({ children }: { children?: React.ReactNode }) => (
    <h3 className="font-bold mt-6 mb-2" style={{ fontSize: "0.95rem", color: "var(--ink)" }}>{children}</h3>
  ),
  p: ({ children }: { children?: React.ReactNode }) => (
    <p className="mb-6" style={{ fontSize: "1rem", lineHeight: "1.9", color: "var(--muted)" }}>{children}</p>
  ),
  strong: ({ children }: { children?: React.ReactNode }) => (
    <strong style={{ color: "var(--ink)", fontWeight: 600 }}>{children}</strong>
  ),
  ul: ({ children }: { children?: React.ReactNode }) => (
    <ul className="mb-6 space-y-1 pl-4" style={{ color: "var(--muted)", listStyleType: "disc" }}>{children}</ul>
  ),
  ol: ({ children }: { children?: React.ReactNode }) => (
    <ol className="mb-6 space-y-1 pl-4" style={{ color: "var(--muted)", listStyleType: "decimal" }}>{children}</ol>
  ),
  li: ({ children }: { children?: React.ReactNode }) => (
    <li style={{ fontSize: "1rem", lineHeight: "1.9" }}>{children}</li>
  ),
  hr: () => <div className="border-t border-[var(--border)] my-8" />,
  table: ({ children }: { children?: React.ReactNode }) => (
    <div className="overflow-x-auto mb-6 rounded-xl" style={{ border: "1px solid var(--border)" }}>
      <table className="w-full text-sm" style={{ borderCollapse: "collapse" }}>{children}</table>
    </div>
  ),
  th: ({ children }: { children?: React.ReactNode }) => (
    <th className="py-2 px-4 text-left text-xs font-bold tracking-wide uppercase" style={{ background: "var(--surface)", color: "var(--ink)", borderBottom: "1px solid var(--border)" }}>{children}</th>
  ),
  td: ({ children }: { children?: React.ReactNode }) => (
    <td className="py-2 px-4" style={{ borderBottom: "1px solid var(--border)", color: "var(--muted)" }}>{children}</td>
  ),
  a: ({ href, children }: { href?: string; children?: React.ReactNode }) => (
    <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: "var(--orange)", textDecoration: "underline" }}>{children}</a>
  ),
};

type NearbySpot = {
  id: string;
  name: string;
  english_name: string;
  city: string;
  region: string;
  image_url: string;
  rating: number;
  dist: number;
};

type Props = {
  spot: Record<string, any>;
  nearby: NearbySpot[];
  images: string[];
};

export default function SpotClient({ spot, nearby, images }: Props) {
  const { lang } = useLang();
  const t = T[lang];
  const isJa = lang === "ja";

  const body = isJa && spot.content_ja ? spot.content_ja : spot.content;
  const orderItems = isJa && spot.what_to_order_ja?.length ? spot.what_to_order_ja : spot.what_to_order;

  return (
    <div>
      {/* ── 이미지 갤러리 ── */}
      {images.length > 0 && (
        <div className={`grid gap-2 ${images.length >= 3 ? "grid-cols-3" : images.length === 2 ? "grid-cols-2" : "grid-cols-1"}`}>
          {images.slice(0, 3).map((url, i) => (
            <div key={i} className="overflow-hidden bg-gray-100" style={{ height: "clamp(200px, 40vw, 480px)" }}>
              <img src={url} alt={`${spot.english_name || spot.name} ${i + 1}`} className="w-full h-full object-cover" />
            </div>
          ))}
        </div>
      )}

      {/* ── 본문 ── */}
      <div className="max-w-2xl mx-auto px-6 py-12">

        {/* 브레드크럼 */}
        <div className="flex items-center gap-2 text-xs mb-6" style={{ color: "var(--muted)" }}>
          <Link href="/spots" className="no-underline hover:opacity-70" style={{ color: "var(--muted)" }}>{t.breadcrumb}</Link>
          <span>›</span>
          <span style={{ color: "var(--orange)" }}>{isJa ? (REGION_JA[spot.region || spot.city] || spot.region || spot.city) : (spot.region || spot.city)}</span>
        </div>

        {/* 헤더 */}
        <div className="mb-8">
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-2" style={{ color: "var(--orange)" }}>
            {isJa ? (REGION_JA[spot.region || spot.city] || spot.region || spot.city) : (spot.region || spot.city)}
          </p>
          <h1 className="font-display mb-4" style={{ fontSize: "clamp(2rem,5vw,3rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
            {spot.english_name || spot.name}
          </h1>
          <div className="flex flex-wrap gap-2">
            <span className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
              ★ {spot.rating} · {spot.rating_count?.toLocaleString()} {t.reviews}
            </span>
            {spot.price_level && (
              <span className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
                {spot.price_level}
              </span>
            )}
            {spot.subway && (
              <span className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
                🚇 {isJa ? translateSubway(spot.subway) : spot.subway}
              </span>
            )}
            {spot.category && (
              <span className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
                {isJa ? (CATEGORY_JA[spot.category] || spot.category) : spot.category}
              </span>
            )}
            {spot.spice_level != null && spot.spice_level > 0 && (
              <span className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
                {"🌶️".repeat(spot.spice_level)}
              </span>
            )}
          </div>
        </div>

        <div className="border-t border-[var(--border)] mb-8" />

        {/* What to Order */}
        {Array.isArray(orderItems) && orderItems.length > 0 && (
          <div className="mb-8 p-5 rounded-2xl" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
            <p className="text-xs font-bold tracking-[0.2em] uppercase mb-3" style={{ color: "var(--orange)" }}>
              {isJa ? "おすすめメニュー" : "What to Order"}
            </p>
            <ul className="space-y-2">
              {orderItems.map((item: string, i: number) => (
                <li key={i} className="flex items-start gap-2 text-sm" style={{ color: "var(--ink)" }}>
                  <span style={{ color: "var(--orange)", flexShrink: 0 }}>✦</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Good For */}
        {Array.isArray(spot.good_for) && spot.good_for.length > 0 && (
          <div className="mb-8">
            <p className="text-xs font-bold tracking-[0.2em] uppercase mb-3" style={{ color: "var(--orange)" }}>
              {isJa ? "こんな方に" : "Good For"}
            </p>
            <div className="flex flex-wrap gap-2">
              {spot.good_for.map((tag: string, i: number) => (
                <span key={i} className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
                  {isJa ? (GOOD_FOR_JA[tag] || tag) : tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 본문 */}
        {body ? (
          <div className="mb-10 prose-content">
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
              {body}
            </ReactMarkdown>
          </div>
        ) : (
          <p className="mb-10" style={{ color: "var(--muted)" }}>Content coming soon.</p>
        )}

        <div className="border-t border-[var(--border)] mb-8" />

        {/* 영업시간 */}
        {spot.hours && (
          <div className="mb-8">
            <p className="text-xs font-bold tracking-[0.2em] uppercase mb-3" style={{ color: "var(--orange)" }}>{t.hoursLabel}</p>
            <div className="text-sm leading-relaxed" style={{ color: "var(--muted)" }}>
              {(isJa ? translateHours(spot.hours) : spot.hours).split("\n").map((line: string, i: number) => (
                <div key={i}>{line}</div>
              ))}
            </div>
          </div>
        )}

        {/* 구글 리뷰 */}
        {(() => {
          const reviews = isJa && Array.isArray(spot.google_reviews_ja) && spot.google_reviews_ja.length > 0
            ? spot.google_reviews_ja
            : Array.isArray(spot.google_reviews) && spot.google_reviews.length > 0
            ? spot.google_reviews
            : null;
          if (!reviews) return null;
          return (
            <div className="mb-8">
              <div className="border-t border-[var(--border)] mb-8" />
              <p className="text-xs font-bold tracking-[0.2em] uppercase mb-4" style={{ color: "var(--orange)" }}>{t.whatPeopleSay}</p>
              <div className="space-y-4">
                {reviews.slice(0, 3).map((review: string, i: number) => (
                  <div key={i} className="p-4 rounded-xl" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
                    <p className="text-sm leading-relaxed" style={{ color: "var(--muted)" }}>"{review}"</p>
                  </div>
                ))}
              </div>
              <p className="text-xs mt-3" style={{ color: "var(--border)" }}>{t.googleReviews}</p>
            </div>
          );
        })()}

        {/* 구글맵 버튼 */}
        {spot.google_maps_url && (
          <a
            href={spot.google_maps_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 font-bold text-sm px-6 py-3 rounded-full text-white no-underline transition-opacity hover:opacity-80"
            style={{ background: "var(--orange)" }}
          >
            {t.googleMaps}
          </a>
        )}
      </div>

      {/* More in category + city */}
      {spot.category && spot.city && (
        <div className="max-w-2xl mx-auto px-6 pb-4">
          {(() => {
            const citySlug = spot.city.toLowerCase();
            const catSlug = spot.category.toLowerCase().replace(/\s+&\s+/g, "-").replace(/\s+/g, "-").replace(/[^\w-]/g, "");
            return (
              <Link
                href={`/cities/${citySlug}/${catSlug}`}
                className="inline-flex items-center gap-2 text-sm font-semibold no-underline transition-opacity hover:opacity-70"
                style={{ color: "var(--orange)" }}
              >
                {t.moreIn(isJa ? (CATEGORY_JA[spot.category] || spot.category) : spot.category, spot.city)}
              </Link>
            );
          })()}
        </div>
      )}

      {/* Nearby Spots */}
      {nearby.length > 0 && (
        <div className="max-w-2xl mx-auto px-6 pb-16">
          <div className="border-t border-[var(--border)] mb-8" />
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-6" style={{ color: "var(--orange)" }}>{t.nearbySpots}</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {nearby.map((s) => {
              const nearbySlug = (s.english_name || s.name).toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
              return (
                <Link key={s.id} href={`/spots/${nearbySlug}`} className="group block no-underline">
                  <div className="rounded-xl overflow-hidden border border-[var(--border)] group-hover:shadow-lg group-hover:-translate-y-0.5 transition-all duration-200">
                    {s.image_url ? (
                      <img src={s.image_url} alt={s.english_name || s.name} className="w-full object-cover" style={{ height: "100px" }} />
                    ) : (
                      <div className="flex items-center justify-center" style={{ height: "100px", background: "var(--surface)" }}>
                        <span style={{ fontSize: "1.8rem" }}>🍜</span>
                      </div>
                    )}
                    <div className="p-3">
                      <div className="text-[9px] font-bold tracking-widest uppercase mb-0.5" style={{ color: "var(--orange)" }}>
                        {isJa ? (REGION_JA[s.region || s.city] || s.region || s.city) : (s.region || s.city)}
                      </div>
                      <div className="font-semibold text-xs mb-1" style={{ color: "var(--ink)" }}>{s.english_name || s.name}</div>
                      <div className="text-[11px]" style={{ color: "var(--muted)" }}>★ {s.rating} · {s.dist < 1 ? `${Math.round(s.dist * 1000)}m` : `${s.dist.toFixed(1)}km`}</div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
