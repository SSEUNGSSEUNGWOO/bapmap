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

  const spotCount = recent?.length ?? 0;

  return (
    <div>
      {/* ── HERO ── */}
      <section className="relative min-h-[90vh] flex flex-col overflow-hidden">
        <div
          className="absolute inset-0 bg-cover"
          style={{ backgroundImage: "url('/hero.jpg')", backgroundPosition: "center 40%" }}
        />
        <div className="absolute inset-0" style={{ background: "linear-gradient(to bottom, rgba(10,8,6,0.55) 0%, rgba(10,8,6,0.4) 50%, rgba(10,8,6,0.72) 100%)" }} />

        {/* Title */}
        <div className="relative flex-1 flex flex-col items-center justify-center px-4 pb-40 pt-48">
          <p className="animate-fadeUp delay-1 text-white/60 text-xs font-semibold tracking-[0.22em] uppercase mb-3 mt-16">
            Korean Food · Mapped for You
          </p>
          <h1 className="font-display animate-fadeUp delay-2 text-white text-center leading-none"
            style={{ fontSize: "clamp(5rem,14vw,12rem)", letterSpacing: "-0.02em" }}>
            Bapmap
          </h1>
          <p className="animate-fadeUp delay-3 text-white/80 font-light mt-8 max-w-lg text-center leading-relaxed"
            style={{ fontSize: "clamp(1.2rem,2.5vw,1.75rem)" }}>
            Follow the locals. Eat like one.
          </p>
        </div>

        {/* Overlapping cards */}
        <div className="relative z-10 px-6" style={{ transform: "translateY(50%)" }}>
          <div className="max-w-5xl mx-auto grid grid-cols-3 gap-4">
            {[
              { title: "Spots", desc: "Every place here is somewhere we've actually been. No tourist traps.", href: "/spots", icon: "📍" },
              { title: "By Location", desc: "Seoul, Gangwon, Jeju — browse spots by where you're headed.", href: "/spots", icon: "🗺️" },
              { title: "About", desc: "Bad at English. Great at eating. Here's the story behind Bapmap.", href: "/about", icon: "👤" },
            ].map((card) => (
              <Link key={card.title} href={card.href} className="group block no-underline">
                <div className="bg-white rounded-2xl p-6 shadow-xl group-hover:-translate-y-1 group-hover:shadow-2xl transition-all duration-200">
                  <div className="text-2xl mb-3">{card.icon}</div>
                  <div className="font-bold text-base mb-2" style={{ color: "var(--ink)" }}>{card.title}</div>
                  <p className="text-xs leading-relaxed mb-4" style={{ color: "var(--muted)" }}>{card.desc}</p>
                  <span className="text-xs font-semibold" style={{ color: "var(--orange)" }}>View →</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── STATS ── */}
      <section className="bg-white pt-28 pb-16 border-b border-[var(--border)]">
        <div className="max-w-5xl mx-auto px-6 grid grid-cols-4 gap-8 text-center">
          {[
            { value: `${spotCount}+`, label: "Spots Curated" },
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
        <section className="max-w-5xl mx-auto px-6 py-20">
          <div className="flex items-end justify-between mb-10">
            <div>
              <p className="text-xs font-semibold tracking-[0.18em] uppercase mb-1" style={{ color: "var(--orange)" }}>Fresh picks</p>
              <h2 className="font-serif text-4xl m-0" style={{ color: "var(--ink)" }}>Latest Spots</h2>
            </div>
            <Link href="/spots" className="text-sm font-semibold no-underline hover:opacity-70 transition-opacity" style={{ color: "var(--orange)" }}>View all →</Link>
          </div>
          <div className="grid grid-cols-3 gap-6">
            {recent.map((spot: Spot) => (
              <SpotCard key={spot.id} spot={spot} />
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
      <div className="bg-white rounded-2xl overflow-hidden border border-[var(--border)] group-hover:shadow-lg group-hover:-translate-y-1 transition-all duration-200">
        {spot.image_url && (
          <div className="h-48 overflow-hidden">
            <img
              src={spot.image_url}
              alt={spot.english_name}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
          </div>
        )}
        <div className="p-4">
          <div className="text-xs font-semibold tracking-widest uppercase mb-1" style={{ color: "var(--orange)" }}>
            {spot.region || spot.city}
          </div>
          <div className="font-semibold text-sm" style={{ color: "var(--ink)" }}>{spot.english_name || spot.name}</div>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-xs" style={{ color: "var(--muted)" }}>★ {spot.rating}</span>
            {spot.price_level && <span className="text-xs" style={{ color: "var(--muted)" }}>{spot.price_level}</span>}
          </div>
        </div>
      </div>
    </Link>
  );
}
