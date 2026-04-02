import Link from "next/link";
import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";

export default async function Home() {
  const { data: recent } = await supabase
    .from("spots")
    .select("id, name, english_name, city, region, image_url, rating, price_level, subway")
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
      <section className="relative h-screen flex flex-col overflow-hidden">
        {/* Background */}
        <div
          className="absolute inset-0 bg-cover"
          style={{ backgroundImage: "url('/hero.jpg')", backgroundPosition: "center 40%" }}
        />
        {/* Gradient overlay */}
        <div
          className="absolute inset-0"
          style={{ background: "linear-gradient(to bottom, rgba(8,6,4,0.5) 0%, rgba(8,6,4,0.35) 45%, rgba(8,6,4,0.78) 100%)" }}
        />

        {/* Center content */}
        <div className="relative flex-1 flex flex-col items-center justify-center px-4 text-center" style={{ paddingBottom: "14rem" }}>
          <p
            className="animate-fadeUp delay-1 text-white/50 text-[10px] font-semibold tracking-[0.3em] uppercase mb-6"
          >
            Korean Food · Mapped for You
          </p>
          <h1
            className="font-display animate-fadeUp delay-2 text-white leading-none"
            style={{ fontSize: "clamp(5.5rem,16vw,13rem)", letterSpacing: "-0.03em" }}
          >
            Bapmap
          </h1>
          <p
            className="animate-fadeUp delay-3 text-white/70 font-light mt-6 max-w-md leading-relaxed"
            style={{ fontSize: "clamp(1rem,2vw,1.35rem)" }}
          >
            Follow the locals. Eat like one.
          </p>
        </div>

        {/* Overlapping nav cards */}
        <div className="absolute bottom-0 left-0 right-0 z-10 px-6" style={{ transform: "translateY(50%)" }}>
          <div className="max-w-4xl mx-auto grid grid-cols-3 gap-4">
            {[
              { title: "Spots", desc: "Every place here is somewhere we've actually been. No tourist traps.", href: "/spots", icon: "📍" },
              { title: "By Location", desc: "Seoul, Gangwon, Jeju — browse spots by where you're headed.", href: "/spots", icon: "🗺️" },
              { title: "About", desc: "Bad at English. Great at eating. Here's the story behind Bapmap.", href: "/about", icon: "👤" },
            ].map((card) => (
              <Link key={card.title} href={card.href} className="group block no-underline">
                <div className="bg-white rounded-2xl p-6 shadow-2xl group-hover:-translate-y-1.5 group-hover:shadow-[0_24px_48px_rgba(0,0,0,0.15)] transition-all duration-200">
                  <div className="text-2xl mb-3">{card.icon}</div>
                  <div className="font-bold text-[15px] mb-2" style={{ color: "var(--ink)" }}>{card.title}</div>
                  <p className="text-xs leading-relaxed mb-4" style={{ color: "var(--muted)" }}>{card.desc}</p>
                  <span className="text-xs font-bold tracking-wide" style={{ color: "var(--orange)" }}>View →</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── STATS ── */}
      <section className="bg-white border-b border-[var(--border)]" style={{ paddingTop: "10rem", paddingBottom: "4rem" }}>
        <div className="max-w-4xl mx-auto px-6 grid grid-cols-4 gap-8 text-center">
          {[
            { value: `${spotCount ?? 0}+`, label: "Spots Curated" },
            { value: "5+", label: "Cities" },
            { value: "100%", label: "Personally Visited" },
            { value: "0", label: "Tourist Traps" },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="font-display leading-none" style={{ fontSize: "3rem", color: "var(--orange)" }}>{stat.value}</div>
              <div className="text-xs font-semibold tracking-widest uppercase mt-2" style={{ color: "var(--muted)" }}>{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── LATEST SPOTS ── */}
      {recent && recent.length > 0 && (
        <section className="max-w-4xl mx-auto px-6 py-20">
          <div className="flex items-end justify-between mb-10">
            <div>
              <p className="text-xs font-bold tracking-[0.2em] uppercase mb-1" style={{ color: "var(--orange)" }}>Fresh picks</p>
              <h2 className="font-display text-4xl m-0" style={{ color: "var(--ink)", letterSpacing: "-0.02em" }}>Latest Spots</h2>
            </div>
            <Link href="/spots" className="text-sm font-bold no-underline hover:opacity-60 transition-opacity" style={{ color: "var(--orange)" }}>
              View all →
            </Link>
          </div>
          <div className="grid grid-cols-3 gap-5">
            {recent.map((spot) => (
              <SpotCard key={spot.id} spot={spot as Spot} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function SpotCard({ spot }: { spot: Spot }) {
  const slug = (spot.english_name || spot.name).toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
  return (
    <Link href={`/spots/${slug}`} className="group block no-underline">
      <div className="bg-white rounded-2xl overflow-hidden border border-[var(--border)] group-hover:shadow-xl group-hover:-translate-y-1 transition-all duration-200">
        {spot.image_url ? (
          <div className="h-48 overflow-hidden bg-gray-100">
            <img
              src={spot.image_url}
              alt={spot.english_name}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
          </div>
        ) : (
          <div className="h-48 bg-[#faf8f5] flex items-center justify-center">
            <span style={{ fontSize: "2.5rem" }}>🍜</span>
          </div>
        )}
        <div className="p-4">
          <div className="text-[10px] font-bold tracking-widest uppercase mb-1" style={{ color: "var(--orange)" }}>
            {spot.region || spot.city}
          </div>
          <div className="font-semibold text-sm mb-2" style={{ color: "var(--ink)" }}>{spot.english_name || spot.name}</div>
          <div className="flex items-center gap-3">
            <span className="text-xs" style={{ color: "var(--muted)" }}>★ {spot.rating}</span>
            {spot.price_level && <span className="text-xs" style={{ color: "var(--muted)" }}>{spot.price_level}</span>}
          </div>
        </div>
      </div>
    </Link>
  );
}
