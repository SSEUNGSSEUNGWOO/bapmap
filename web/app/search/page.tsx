"use client";

import { useEffect, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

type Spot = {
  id: string;
  name: string;
  english_name: string;
  category: string;
  region: string;
  city: string;
  status: string;
  rating: number;
  price_level: string;
  subway: string;
  image_url: string;
};

export default function SearchPage() {
  const searchParams = useSearchParams();
  const q = searchParams.get("q") || "";
  const [answer, setAnswer] = useState("");
  const [spots, setSpots] = useState<Spot[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState(q);
  const ranRef = useRef(false);

  const search = async (raw: string) => {
    if (!raw.trim()) return;
    setLoading(true);
    setAnswer("");
    setSpots([]);
    ranRef.current = true;

    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: raw }),
    });

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const lines = decoder.decode(value).split("\n");
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        try {
          const msg = JSON.parse(line.slice(6));
          if (msg.type === "spots") setSpots(msg.data);
          if (msg.type === "text") setAnswer((prev) => prev + msg.text);
        } catch {}
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    if (q && !ranRef.current) search(q);
  }, [q]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    window.history.pushState({}, "", `/search?q=${encodeURIComponent(query)}`);
    search(query);
  };

  return (
    <div style={{ minHeight: "80vh", background: "#fafafa" }}>
      {/* Top bar */}
      <div className="border-b border-[var(--border)] bg-white sticky top-14 z-10">
        <div className="max-w-3xl mx-auto px-6 py-4">
          <form onSubmit={handleSubmit} className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything about food in Korea..."
              autoFocus
              className="w-full rounded-full px-6 py-3.5 pr-14 text-sm outline-none transition-all"
              style={{
                border: "2px solid var(--border)",
                color: "var(--ink)",
                background: "#fff",
              }}
              onFocus={(e) => (e.target.style.borderColor = "var(--orange)")}
              onBlur={(e) => (e.target.style.borderColor = "var(--border)")}
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full flex items-center justify-center hover:opacity-80 transition-opacity"
              style={{ background: "var(--orange)" }}
            >
              <span className="text-white text-sm font-bold">→</span>
            </button>
          </form>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-10">
        {/* Query heading */}
        {q && (
          <div className="mb-8">
            <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-2" style={{ color: "var(--orange)" }}>
              AI Search
            </p>
            <h1 className="font-display" style={{ fontSize: "clamp(1.5rem,4vw,2.2rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.2 }}>
              "{q}"
            </h1>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-[1fr_320px] gap-6 items-start">
          {/* Left: Answer */}
          <div>
            {/* Loading skeleton */}
            {loading && !answer && (
              <div className="rounded-2xl p-6 mb-6" style={{ background: "#fff", border: "1px solid var(--border)" }}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: "var(--orange)" }}>
                    <svg className="animate-spin w-3 h-3 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                  </div>
                  <span className="text-sm font-medium" style={{ color: "var(--muted)" }}>Finding the best spots for you...</span>
                </div>
                <div className="space-y-2">
                  {[100, 85, 92].map((w, i) => (
                    <div key={i} className="h-3 rounded-full animate-pulse" style={{ width: `${w}%`, background: "var(--border)" }} />
                  ))}
                </div>
              </div>
            )}

            {/* Answer text */}
            {answer && (
              <div className="rounded-2xl p-6 mb-6" style={{ background: "#fff", border: "1px solid var(--border)" }}>
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: "var(--orange)" }}>
                    <span style={{ fontSize: "12px" }}>✦</span>
                  </div>
                  <span className="text-[10px] font-bold tracking-[0.2em] uppercase" style={{ color: "var(--orange)" }}>
                    Bapmap AI
                  </span>
                </div>
                <div className="text-sm leading-[1.85] whitespace-pre-wrap" style={{ color: "var(--ink)" }}>
                  {answer}
                  {loading && (
                    <span className="inline-block w-0.5 h-4 ml-0.5 align-middle animate-pulse rounded-full" style={{ background: "var(--orange)" }} />
                  )}
                </div>
              </div>
            )}

            {/* Back link */}
            {!loading && answer && (
              <Link href="/" className="inline-flex items-center gap-1 text-xs no-underline hover:opacity-60 transition-opacity" style={{ color: "var(--muted)" }}>
                ← Back to home
              </Link>
            )}
          </div>

          {/* Right: Spot cards */}
          {spots.length > 0 && (
            <div className="space-y-3">
              <p className="text-[10px] font-bold tracking-[0.25em] uppercase" style={{ color: "var(--muted)" }}>
                Related spots
              </p>
              {spots.map((s) => {
                const name = s.english_name || s.name;
                const slug = name.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
                const published = s.status === "업로드완료";

                return published ? (
                  <Link
                    key={s.id}
                    href={`/spots/${slug}`}
                    className="group no-underline flex gap-3 p-3 rounded-2xl transition-all duration-200 hover:shadow-md hover:-translate-y-0.5"
                    style={{ background: "#fff", border: "1px solid var(--border)" }}
                  >
                    {s.image_url ? (
                      <img
                        src={s.image_url}
                        alt={name}
                        className="w-16 h-16 rounded-xl object-cover flex-shrink-0"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: "var(--surface)" }}>
                        <span style={{ fontSize: "1.4rem" }}>🍜</span>
                      </div>
                    )}
                    <div className="flex-1 min-w-0 flex flex-col justify-center">
                      <div className="text-[9px] font-bold tracking-widest uppercase mb-0.5" style={{ color: "var(--orange)" }}>
                        {s.region || s.city}
                      </div>
                      <div className="font-semibold text-sm leading-tight mb-1.5 truncate" style={{ color: "var(--ink)" }}>
                        {name}
                      </div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "var(--surface)", color: "var(--muted)", border: "1px solid var(--border)" }}>
                          ★ {s.rating}
                        </span>
                        {s.price_level && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "var(--surface)", color: "var(--muted)", border: "1px solid var(--border)" }}>
                            {s.price_level}
                          </span>
                        )}
                        {s.category && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "var(--surface)", color: "var(--muted)", border: "1px solid var(--border)" }}>
                            {s.category}
                          </span>
                        )}
                      </div>
                    </div>
                  </Link>
                ) : (
                  <div
                    key={s.id}
                    className="flex gap-3 p-3 rounded-2xl"
                    style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
                  >
                    <div className="w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: "#eee" }}>
                      <span style={{ fontSize: "1.4rem" }}>📍</span>
                    </div>
                    <div className="flex flex-col justify-center">
                      <div className="font-semibold text-sm mb-0.5" style={{ color: "var(--muted)" }}>{name}</div>
                      <div className="text-[10px] font-semibold px-2 py-0.5 rounded-full w-fit" style={{ background: "var(--border)", color: "var(--muted)" }}>
                        Coming soon
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
