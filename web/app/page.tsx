import Link from "next/link";
import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import SpotCard from "./SpotCard";
import SearchBar from "./SearchBar";

export const revalidate = 3600;

export default async function Home() {
  const { data: recent } = await supabase
    .from("spots")
    .select("id, name, english_name, city, region, image_url, image_urls, rating, price_level, subway")
    .eq("status", "업로드완료")
    .order("created_at", { ascending: false })
    .limit(6);

  const { count: spotCount } = await supabase
    .from("spots")
    .select("*", { count: "exact", head: true })
    .eq("status", "업로드완료");

  return (
    <div>
      {/* ── HERO ── */}
      <section className="relative flex flex-col overflow-hidden" style={{ height: "100svh", minHeight: "600px" }}>
        {/* Background */}
        <div
          className="absolute inset-0 bg-cover scale-105"
          style={{
            backgroundImage: "url('/hero.jpg')",
            backgroundPosition: "center 40%",
            willChange: "transform",
          }}
        />
        {/* Layered gradient */}
        <div
          className="absolute inset-0"
          style={{
            background: "linear-gradient(160deg, rgba(8,6,4,0.62) 0%, rgba(8,6,4,0.28) 40%, rgba(8,6,4,0.85) 100%)",
          }}
        />
        {/* Noise texture overlay */}
        <div
          className="absolute inset-0 opacity-[0.03] pointer-events-none"
          style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")", backgroundSize: "200px" }}
        />

        {/* Center content */}
        <div className="relative flex-1 flex flex-col items-center justify-center px-4 text-center" style={{ paddingBottom: "80px" }}>
          {/* Eyebrow */}
          <div className="animate-fadeUp delay-1 flex items-center gap-3 mb-8">
            <div style={{ width: "32px", height: "1px", background: "rgba(245,166,35,0.7)" }} />
            <p className="text-white/60 text-[10px] font-semibold tracking-[0.35em] uppercase">
              Korean Food · Mapped for You
            </p>
            <div style={{ width: "32px", height: "1px", background: "rgba(245,166,35,0.7)" }} />
          </div>

          {/* Main title */}
          <h1
            className="font-display animate-fadeUp delay-2 text-white"
            style={{
              fontSize: "clamp(6rem,18vw,14rem)",
              letterSpacing: "-0.035em",
              lineHeight: 0.9,
              textShadow: "0 4px 40px rgba(0,0,0,0.3)",
            }}
          >
            Bapmap
          </h1>

          {/* Subtitle */}
          <p
            className="animate-fadeUp delay-3 text-white/65 font-light mt-7 max-w-sm leading-relaxed"
            style={{ fontSize: "clamp(0.95rem,2vw,1.2rem)", letterSpacing: "0.01em" }}
          >
            Follow the locals. Eat like one.
          </p>

          {/* Search */}
          <div className="animate-fadeUp delay-4 mt-10 w-full px-4" style={{ maxWidth: "520px" }}>
            <p className="text-white/80 text-xs text-center mb-3 tracking-wide">
              ✦ AI-powered · Ask anything about Korean food & culture
            </p>
            <SearchBar />
          </div>
        </div>

        {/* Bottom fade into cards */}
        <div
          className="absolute bottom-0 left-0 right-0"
          style={{ height: "200px", background: "linear-gradient(to bottom, transparent, rgba(8,6,4,0.6))" }}
        />
      </section>

      {/* ── NAV CARDS (overlapping hero) ── */}
      <div className="relative z-10 px-6" style={{ marginTop: "-110px" }}>
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            {
              title: "Spots",
              desc: "Every place here is somewhere we've actually eaten.",
              href: "/spots",
              img: "/card-spots.jpg",
              badge: `${spotCount ?? 0}+ spots`,
            },
            {
              title: "By Location",
              desc: "Seoul, Gangwon, Jeju — browse by where you're headed.",
              href: "/map",
              img: "/card-location.jpg",
              badge: "Interactive map",
            },
            {
              title: "About",
              desc: "Bad at English. Great at eating. The story behind Bapmap.",
              href: "/about",
              img: "/card-about.jpg",
              badge: "My story",
            },
          ].map((card) => (
            <Link
              key={card.title}
              href={card.href}
              className="group block no-underline relative rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-1.5"
              style={{
                height: "220px",
                boxShadow: "0 16px 48px rgba(0,0,0,0.25), 0 2px 8px rgba(0,0,0,0.1)",
              }}
            >
              <img
                src={card.img}
                alt={card.title}
                className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
              />
              <div
                className="absolute inset-0"
                style={{ background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 55%, rgba(0,0,0,0.05) 100%)" }}
              />
              {/* Badge */}
              <div className="absolute top-4 left-4">
                <span
                  className="text-[9px] font-bold tracking-[0.2em] uppercase px-2.5 py-1 rounded-full"
                  style={{ background: "var(--orange)", color: "#fff" }}
                >
                  {card.badge}
                </span>
              </div>
              <div className="absolute bottom-0 left-0 p-5">
                <div className="font-display text-white text-xl font-bold mb-1.5 leading-tight">
                  {card.title}
                </div>
                <p className="text-white/65 text-xs leading-relaxed">{card.desc}</p>
              </div>
              <div className="absolute bottom-5 right-5 text-white/0 group-hover:text-white/80 transition-all duration-200 text-xs font-bold">
                →
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ── STATS ── */}
      <section className="bg-white" style={{ paddingTop: "6rem", paddingBottom: "5rem" }}>
        <div className="max-w-4xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-0">
            {[
              { value: `${spotCount ?? 0}+`, label: "Spots Curated" },
              { value: "5+", label: "Cities" },
              { value: "100%", label: "Personally Visited" },
              { value: "0", label: "Tourist Traps" },
            ].map((stat, i) => (
              <div
                key={stat.label}
                className="text-center py-6"
                style={{
                  borderLeft: i > 0 ? "1px solid var(--border)" : "none",
                }}
              >
                <div
                  className="font-display leading-none mb-2"
                  style={{ fontSize: "3.5rem", color: "var(--orange)" }}
                >
                  {stat.value}
                </div>
                <div
                  className="text-[10px] font-bold tracking-[0.2em] uppercase"
                  style={{ color: "var(--muted)" }}
                >
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── WHY TRUST US ── */}
      <section className="border-t border-b border-[var(--border)]" style={{ background: "var(--surface)", paddingTop: "5rem", paddingBottom: "5rem" }}>
        <div className="max-w-4xl mx-auto px-6">
          <div className="mb-14 text-center">
            <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-3" style={{ color: "var(--orange)" }}>
              Why Bapmap
            </p>
            <h2
              className="font-display m-0"
              style={{ fontSize: "clamp(2rem,5vw,3.2rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.1 }}
            >
              Not your average food guide
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            {[
              {
                num: "01",
                img: "/why-eat.jpg",
                title: "We ate here. All of it.",
                desc: "Every single spot on Bapmap is somewhere we've personally visited and eaten at. No desk research, no stock photos of food we've never tasted.",
              },
              {
                num: "02",
                img: "/why-honest.jpg",
                title: "Zero ads. Zero sponsors.",
                desc: "No restaurant has paid to be featured here. We pick based on taste, value, and vibe — nothing else. If we don't like it, it doesn't make the cut.",
              },
              {
                num: "03",
                img: "/why-travel.jpg",
                title: "Built for foreigners.",
                desc: "We know what it's like to not read the menu. Every recommendation comes with context you actually need: subway stop, price range, what to order.",
              },
            ].map((item) => (
              <div key={item.num} className="flex flex-col">
                <div
                  className="rounded-2xl overflow-hidden mb-6"
                  style={{ height: "180px" }}
                >
                  <img
                    src={item.img}
                    alt={item.title}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex items-start gap-4">
                  <span
                    className="font-display flex-shrink-0 mt-0.5"
                    style={{ fontSize: "1.5rem", color: "var(--orange)", lineHeight: 1, opacity: 0.4 }}
                  >
                    {item.num}
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

      {/* ── EXPLORE BY CITY ── */}
      <section className="max-w-4xl mx-auto px-6" style={{ paddingTop: "5rem", paddingBottom: "5rem" }}>
        <div className="mb-10">
          <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-3" style={{ color: "var(--orange)" }}>
            Explore by city
          </p>
          <h2
            className="font-display m-0"
            style={{ fontSize: "clamp(2rem,5vw,3.2rem)", color: "var(--ink)", letterSpacing: "-0.02em" }}
          >
            Where to?
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Seoul - active */}
          <Link
            href="/spots"
            className="group block no-underline relative rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-1"
            style={{ height: "280px", boxShadow: "0 4px 24px rgba(0,0,0,0.1)" }}
          >
            <img
              src="/city-seoul.jpg"
              alt="Seoul"
              className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            />
            <div
              className="absolute inset-0"
              style={{ background: "linear-gradient(to top, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0.1) 60%)" }}
            />
            <div className="absolute bottom-0 left-0 p-7">
              <div
                className="text-white font-display leading-none mb-2"
                style={{ fontSize: "2.5rem", letterSpacing: "-0.03em" }}
              >
                Seoul
              </div>
              <div
                className="text-xs font-semibold flex items-center gap-1.5"
                style={{ color: "var(--orange)" }}
              >
                View spots →
              </div>
            </div>
          </Link>

          {/* Right: Busan + Jeju stacked */}
          <div className="grid grid-rows-2 gap-4">
            {[
              { name: "Busan", img: "/city-busan.jpg" },
              { name: "Jeju", img: "/city-jeju.jpg" },
            ].map((city) => (
              <div
                key={city.name}
                className="relative rounded-2xl overflow-hidden"
                style={{ height: "130px" }}
              >
                <img
                  src={city.img}
                  alt={city.name}
                  className="absolute inset-0 w-full h-full object-cover brightness-50"
                />
                <div
                  className="absolute inset-0"
                  style={{ background: "linear-gradient(to right, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.1) 100%)" }}
                />
                <div className="absolute inset-0 flex items-center justify-between px-5">
                  <div className="text-white font-display text-2xl font-bold">{city.name}</div>
                  <div
                    className="text-[10px] font-bold tracking-widest uppercase px-3 py-1.5 rounded-full"
                    style={{ background: "rgba(255,255,255,0.15)", backdropFilter: "blur(6px)", color: "rgba(255,255,255,0.75)" }}
                  >
                    Coming Soon
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Gangwon - full width */}
        <div
          className="mt-4 relative rounded-2xl overflow-hidden"
          style={{ height: "120px" }}
        >
          <img
            src="/city-gangwon.jpg"
            alt="Gangwon"
            className="absolute inset-0 w-full h-full object-cover brightness-50"
          />
          <div
            className="absolute inset-0"
            style={{ background: "linear-gradient(to right, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.15) 100%)" }}
          />
          <div className="absolute inset-0 flex items-center justify-between px-7">
            <div className="text-white font-display text-2xl font-bold">Gangwon</div>
            <div
              className="text-[10px] font-bold tracking-widest uppercase px-3 py-1.5 rounded-full"
              style={{ background: "rgba(255,255,255,0.15)", backdropFilter: "blur(6px)", color: "rgba(255,255,255,0.75)" }}
            >
              Coming Soon
            </div>
          </div>
        </div>
      </section>

      {/* ── LATEST SPOTS ── */}
      {recent && recent.length > 0 && (
        <section
          className="border-t border-[var(--border)]"
          style={{ background: "var(--surface)", paddingTop: "5rem", paddingBottom: "6rem" }}
        >
          <div className="max-w-4xl mx-auto px-6">
            <div className="flex items-end justify-between mb-10">
              <div>
                <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-3" style={{ color: "var(--orange)" }}>
                  Fresh picks
                </p>
                <h2
                  className="font-display m-0"
                  style={{ fontSize: "clamp(2rem,5vw,3.2rem)", color: "var(--ink)", letterSpacing: "-0.02em" }}
                >
                  Latest Bapmap Picks
                </h2>
              </div>
              <Link
                href="/spots"
                className="text-sm font-bold no-underline hover:opacity-60 transition-opacity"
                style={{ color: "var(--orange)" }}
              >
                View all →
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {recent.map((spot) => (
                <SpotCard key={spot.id} spot={spot as Spot} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── BOTTOM CTA ── */}
      <section className="relative text-center overflow-hidden" style={{ paddingTop: "7rem", paddingBottom: "7rem" }}>
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: "url('/seoul-cta.jpg')", backgroundPosition: "center 60%" }}
        />
        <div className="absolute inset-0" style={{ background: "linear-gradient(to bottom, rgba(0,0,0,0.55), rgba(0,0,0,0.7))" }} />
        <div className="relative z-10">
          <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-4" style={{ color: "var(--orange)" }}>
            Ready to eat?
          </p>
          <h2
            className="font-display mb-6 text-white"
            style={{ fontSize: "clamp(2rem,5vw,3rem)", letterSpacing: "-0.02em" }}
          >
            Find your next meal in Korea
          </h2>
          <Link
            href="/spots"
            className="inline-flex items-center gap-2 no-underline font-semibold text-sm px-8 py-3.5 rounded-full text-white transition-all duration-200 hover:opacity-85"
            style={{ background: "var(--orange)", boxShadow: "0 4px 24px rgba(245,166,35,0.4)" }}
          >
            Browse All Spots →
          </Link>
        </div>
      </section>
    </div>
  );
}
