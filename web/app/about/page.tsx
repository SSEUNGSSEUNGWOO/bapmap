import Link from "next/link";

export default function AboutPage() {
  return (
    <div>
      {/* ── HERO ── */}
      <section className="relative flex items-end overflow-hidden" style={{ height: "50vh", minHeight: "320px" }}>
        <div
          className="absolute inset-0 bg-cover"
          style={{ backgroundImage: "url('/hero.jpg')", backgroundPosition: "center 40%" }}
        />
        <div className="absolute inset-0" style={{ background: "linear-gradient(to bottom, rgba(8,6,4,0.3) 0%, rgba(8,6,4,0.75) 100%)" }} />
        <div className="relative px-8 pb-12 max-w-3xl mx-auto w-full">
          <p className="text-white/50 text-[10px] font-semibold tracking-[0.3em] uppercase mb-3">The story</p>
          <h1 className="font-display text-white leading-none" style={{ fontSize: "clamp(3rem,8vw,6rem)", letterSpacing: "-0.03em" }}>
            About Bapmap
          </h1>
        </div>
      </section>

      {/* ── CONTENT ── */}
      <section className="max-w-2xl mx-auto px-6 py-20">

        {/* Intro block */}
        <div className="mb-16">
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-8" style={{ color: "var(--orange)" }}>Who made this</p>

          {/* Photo + intro side by side */}
          <div className="flex gap-8 items-start mb-8">
            <div className="flex-shrink-0 rounded-2xl overflow-hidden shadow-lg" style={{ width: "160px", height: "200px" }}>
              <img src="/about-me.jpg" alt="Bapmap creator" className="w-full h-full object-cover" style={{ objectPosition: "center 10%" }} />
            </div>
            <p className="text-xl font-light leading-relaxed flex-1 pt-2" style={{ color: "var(--ink)", lineHeight: "1.7" }}>
              Hi. I'm just an ordinary developer living in Seoul who really loves eating — and finding the places that don't show up on tourist lists.
            </p>
          </div>

          <p className="leading-relaxed text-base mb-5" style={{ color: "var(--muted)", lineHeight: "1.8" }}>
            When I travel abroad, I always want the same thing: not the most famous restaurant in the city, but the place where <em>actual locals</em> eat. The kind of spot that's on no listicle, has no English menu, and somehow tastes better than everywhere else.
          </p>
          <div className="rounded-2xl p-5" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
            <p className="text-sm leading-relaxed mb-3" style={{ color: "var(--muted)", lineHeight: "1.8" }}>
              Planning a trip to Korea and can't find what you're looking for? Feel free to reach out — my English is a work in progress, but my knowledge of where to eat is not.
            </p>
            <div className="flex flex-col gap-1.5">
              <a href="mailto:jsw7980@gmail.com" className="text-sm font-semibold no-underline hover:opacity-70 transition-opacity" style={{ color: "var(--orange)" }}>
                ✉️ jsw7980@gmail.com
              </a>
              <a href="https://www.instagram.com/sseungsseung_woo" target="_blank" rel="noopener noreferrer" className="text-sm font-semibold no-underline hover:opacity-70 transition-opacity" style={{ color: "var(--orange)" }}>
                📸 @sseungsseung_woo
              </a>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-[var(--border)] mb-16" />

        {/* Travel photo grid */}
        <div className="mb-16">
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-2" style={{ color: "var(--orange)" }}>Eating my way around the world</p>
          <p className="text-sm mb-2" style={{ color: "var(--muted)" }}>Poland · China · Hong Kong · Czech Republic · Germany · Japan</p>
          <p className="text-sm italic mb-8" style={{ color: "var(--muted)" }}>
            (And these are just the ones that fit on screen. My domestic Korea list? We're going to need a bigger website.)
          </p>

          <div className="grid grid-cols-3 gap-2">
            {[
              { src: "/travel-1.jpg", label: "Poland" },
              { src: "/travel-2.jpg", label: "China" },
              { src: "/travel-3.jpg", label: "China" },
              { src: "/travel-4.jpg", label: "Hong Kong" },
              { src: "/travel-5.jpg", label: "Czech Republic" },
              { src: "/travel-6.jpg", label: "Hong Kong" },
              { src: "/travel-7.jpg", label: "Germany" },
              { src: "/travel-8.jpg", label: "Poland" },
              { src: "/travel-9.jpg", label: "Japan" },
            ].map((photo, i) => (
              <div key={i} className="relative rounded-xl overflow-hidden group" style={{ aspectRatio: "1/1" }}>
                <img src={photo.src} alt={photo.label} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 60%)" }}>
                  <span className="text-white text-xs font-semibold">{photo.label}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-[var(--border)] mb-16" />

        {/* Why section */}
        <div className="mb-16">
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-4" style={{ color: "var(--orange)" }}>Why Bapmap exists</p>
          <p className="leading-relaxed text-base mb-4" style={{ color: "var(--muted)", lineHeight: "1.8" }}>
            I noticed that when foreigners search for Korean food, the results are always the same: the most famous places, the most Instagrammed spots, the ones that have been written about a thousand times. They're fine. But they're not where Koreans actually eat.
          </p>
          <p className="leading-relaxed text-base mb-4" style={{ color: "var(--muted)", lineHeight: "1.8" }}>
            So I built Bapmap. Every spot here is somewhere I've personally been. I know where to sit, what to order, how much it costs, and which subway stop to get off at. My English isn't perfect — but my taste in food is.
          </p>
          <p className="leading-relaxed text-base" style={{ color: "var(--muted)", lineHeight: "1.8" }}>
            Want to eat where Koreans actually eat? Follow along.
          </p>
        </div>

        {/* Divider */}
        <div className="border-t border-[var(--border)] mb-16" />

        {/* Values */}
        <div className="mb-16">
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-8" style={{ color: "var(--orange)" }}>How I pick spots</p>
          <div className="space-y-6">
            {[
              { label: "Personally visited", desc: "I've been to every single place on this site. No exceptions." },
              { label: "No ads, ever", desc: "Nobody pays to be listed here. I pick based on taste alone." },
              { label: "Local first", desc: "If it's famous with tourists, it probably isn't here. I go where Koreans go." },
            ].map((item) => (
              <div key={item.label} className="flex gap-6 items-start">
                <div className="w-1.5 h-1.5 rounded-full mt-2.5 flex-shrink-0" style={{ background: "var(--orange)" }} />
                <div>
                  <div className="font-semibold text-sm mb-1" style={{ color: "var(--ink)" }}>{item.label}</div>
                  <div className="text-sm" style={{ color: "var(--muted)" }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="rounded-2xl p-8 text-center" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          <div className="font-display text-2xl mb-2" style={{ color: "var(--ink)" }}>Ready to eat like a local?</div>
          <p className="text-sm mb-6" style={{ color: "var(--muted)" }}>Browse every spot I've curated — personally visited, honestly reviewed.</p>
          <Link
            href="/spots"
            className="inline-block font-bold text-sm px-6 py-3 rounded-full text-white no-underline transition-opacity hover:opacity-80"
            style={{ background: "var(--orange)" }}
          >
            Explore Spots →
          </Link>
        </div>
      </section>
    </div>
  );
}
