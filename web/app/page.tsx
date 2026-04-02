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
        <div className="relative flex-1 flex flex-col items-center justify-center px-4 text-center">
          <p className="animate-fadeUp delay-1 text-white/50 text-[10px] font-semibold tracking-[0.3em] uppercase mb-6">
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
      </section>

      {/* Overlapping nav cards — outside hero to avoid overflow-hidden clipping */}
      <div className="relative z-10 px-6" style={{ marginTop: "-90px" }}>
        <div className="max-w-4xl mx-auto grid grid-cols-3 gap-4">
          {[
            { title: "Spots", desc: "Every place here is somewhere we've actually been.", href: "/spots", img: "/card-spots.jpg" },
            { title: "By Location", desc: "Seoul, Gangwon, Jeju — browse by where you're headed.", href: "/spots", img: "/card-location.jpg" },
            { title: "About", desc: "Bad at English. Great at eating. The story behind Bapmap.", href: "/about", img: "/card-about.jpg" },
          ].map((card) => (
            <Link key={card.title} href={card.href} className="group block no-underline relative rounded-2xl overflow-hidden shadow-2xl group-hover:-translate-y-1.5 group-hover:shadow-[0_24px_48px_rgba(0,0,0,0.3)] transition-all duration-200" style={{ height: "180px" }}>
              <img src={card.img} alt={card.title} className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0.1) 60%)" }} />
              <div className="absolute bottom-0 left-0 p-5">
                <div className="font-display text-white text-xl font-bold mb-1">{card.title}</div>
                <p className="text-white/70 text-xs leading-relaxed">{card.desc}</p>
              </div>
              <div className="absolute top-4 right-4 text-xs font-bold text-white opacity-0 group-hover:opacity-100 transition-opacity">View →</div>
            </Link>
          ))}
        </div>
      </div>

      {/* ── STATS ── */}
      <section className="bg-white border-b border-[var(--border)]" style={{ paddingTop: "5rem", paddingBottom: "4rem" }}>
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

      {/* ── WHY TRUST US ── */}
      <section className="py-20 border-b border-[var(--border)]" style={{ background: "var(--surface)" }}>
        <div className="max-w-4xl mx-auto px-6">
          <div className="mb-12 text-center">
            <p className="text-xs font-bold tracking-[0.2em] uppercase mb-1" style={{ color: "var(--orange)" }}>Why Bapmap</p>
            <h2 className="font-display text-4xl m-0" style={{ color: "var(--ink)", letterSpacing: "-0.02em" }}>Not your average food guide</h2>
          </div>
          <div className="grid grid-cols-3 gap-8">
            {[
              {
                img: "/why-eat.jpg",
                title: "We ate here. All of it.",
                desc: "Every single spot on Bapmap is somewhere we've personally visited and eaten at. No desk research, no stock photos of food we've never tasted.",
              },
              {
                img: "/why-honest.jpg",
                title: "Zero ads. Zero sponsors.",
                desc: "No restaurant has paid to be featured here. We pick based on taste, value, and vibe — nothing else. If we don't like it, it doesn't make the cut.",
              },
              {
                img: "/why-travel.jpg",
                title: "Built for foreigners.",
                desc: "We know what it's like to not read the menu. Every recommendation comes with the context you actually need: subway stop, price range, what to order.",
              },
            ].map((item) => (
              <div key={item.title} className="text-center">
                <div className="mx-auto mb-5 rounded-2xl overflow-hidden" style={{ width: "80px", height: "80px" }}>
                  <img src={item.img} alt={item.title} className="w-full h-full object-cover" />
                </div>
                <div className="font-bold text-base mb-3" style={{ color: "var(--ink)" }}>{item.title}</div>
                <p className="text-sm leading-relaxed" style={{ color: "var(--muted)" }}>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── EXPLORE BY CITY ── */}
      <section className="max-w-4xl mx-auto px-6 py-20">
        <div className="mb-10">
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-1" style={{ color: "var(--orange)" }}>Explore by city</p>
          <h2 className="font-display text-4xl m-0" style={{ color: "var(--ink)", letterSpacing: "-0.02em" }}>Where to?</h2>
        </div>
        <div className="grid grid-cols-2 gap-4">
          {/* Seoul - active */}
          <Link href="/spots" className="group block no-underline relative rounded-2xl overflow-hidden" style={{ height: "260px" }}>
            <img src="/city-seoul.jpg" alt="Seoul" className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
            <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.1) 60%)" }} />
            <div className="absolute bottom-0 left-0 p-6">
              <div className="text-white font-display text-3xl font-bold leading-none" style={{ letterSpacing: "-0.02em" }}>Seoul</div>
              <div className="text-white/70 text-sm mt-1">View spots →</div>
            </div>
          </Link>

          {/* Right column - 2 smaller cards */}
          <div className="grid grid-rows-2 gap-4">
            {[
              { name: "Busan", img: "/city-busan.jpg" },
              { name: "Jeju", img: "/city-jeju.jpg" },
            ].map((city) => (
              <div key={city.name} className="relative rounded-2xl overflow-hidden" style={{ height: "122px" }}>
                <img src={city.img} alt={city.name} className="absolute inset-0 w-full h-full object-cover brightness-50" />
                <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.2) 100%)" }} />
                <div className="absolute bottom-0 left-0 p-4 flex items-end justify-between w-full">
                  <div className="text-white font-display text-xl font-bold">{city.name}</div>
                  <div className="text-xs font-semibold px-2.5 py-1 rounded-full text-white/80" style={{ background: "rgba(255,255,255,0.15)", backdropFilter: "blur(4px)" }}>Coming Soon</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Gangwon - bottom full width coming soon */}
        <div className="mt-4 relative rounded-2xl overflow-hidden" style={{ height: "120px" }}>
          <img src="/city-gangwon.jpg" alt="Gangwon" className="absolute inset-0 w-full h-full object-cover brightness-50" />
          <div className="absolute inset-0" style={{ background: "linear-gradient(to right, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.2) 100%)" }} />
          <div className="absolute inset-0 flex items-center justify-between px-6">
            <div className="text-white font-display text-2xl font-bold">Gangwon</div>
            <div className="text-xs font-semibold px-3 py-1.5 rounded-full text-white/80" style={{ background: "rgba(255,255,255,0.15)", backdropFilter: "blur(4px)" }}>Coming Soon</div>
          </div>
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
