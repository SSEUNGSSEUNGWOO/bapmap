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
    <div className="max-w-2xl mx-auto px-6 py-12">
      {/* Back */}
      <Link href="/" className="inline-flex items-center gap-1 text-xs no-underline mb-8 hover:opacity-60 transition-opacity" style={{ color: "var(--muted)" }}>
        ← Back
      </Link>

      {/* Search input */}
      <form onSubmit={handleSubmit} className="relative mb-10">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything about food in Korea..."
          className="w-full rounded-full px-6 py-4 pr-14 text-sm outline-none"
          style={{
            border: "2px solid var(--border)",
            color: "var(--ink)",
            background: "#fff",
          }}
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full flex items-center justify-center hover:opacity-80 transition-opacity"
          style={{ background: "var(--orange)" }}
        >
          <span className="text-white text-sm font-bold">→</span>
        </button>
      </form>

      {/* Query label */}
      {q && (
        <div className="mb-6">
          <p className="text-[10px] font-bold tracking-[0.2em] uppercase mb-1" style={{ color: "var(--orange)" }}>
            Search results
          </p>
          <h1 className="font-display text-2xl" style={{ color: "var(--ink)", letterSpacing: "-0.02em" }}>
            "{q}"
          </h1>
        </div>
      )}

      {/* Answer */}
      {(loading || answer) && (
        <div className="mb-8 p-6 rounded-2xl" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          {loading && !answer && (
            <div className="flex items-center gap-2" style={{ color: "var(--muted)" }}>
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              <span className="text-sm">Searching Bapmap...</span>
            </div>
          )}
          {answer && (
            <div className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: "var(--ink)" }}>
              {answer}
              {loading && (
                <span className="inline-block w-1 h-4 ml-0.5 align-middle animate-pulse" style={{ background: "var(--orange)" }} />
              )}
            </div>
          )}
        </div>
      )}

      {/* Spot cards */}
      {spots.length > 0 && (
        <div>
          <p className="text-[10px] font-bold tracking-[0.2em] uppercase mb-4" style={{ color: "var(--muted)" }}>
            Related spots
          </p>
          <div className="grid grid-cols-1 gap-3">
            {spots.map((s) => {
              const name = s.english_name || s.name;
              const slug = name.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
              const published = s.status === "업로드완료";

              return published ? (
                <Link
                  key={s.id}
                  href={`/spots/${slug}`}
                  className="group no-underline flex items-center gap-4 p-4 rounded-2xl transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
                  style={{ border: "1px solid var(--border)", background: "#fff" }}
                >
                  {s.image_url ? (
                    <img src={s.image_url} alt={name} className="w-16 h-16 rounded-xl object-cover flex-shrink-0" />
                  ) : (
                    <div className="w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: "var(--surface)" }}>
                      <span style={{ fontSize: "1.5rem" }}>🍜</span>
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="text-[10px] font-bold tracking-widest uppercase mb-0.5" style={{ color: "var(--orange)" }}>
                      {s.region || s.city}
                    </div>
                    <div className="font-semibold text-sm mb-1 truncate" style={{ color: "var(--ink)" }}>{name}</div>
                    <div className="flex items-center gap-3 text-xs" style={{ color: "var(--muted)" }}>
                      <span>★ {s.rating}</span>
                      {s.price_level && <span>{s.price_level}</span>}
                      {s.subway && <span>🚇 {s.subway}</span>}
                      {s.category && <span>{s.category}</span>}
                    </div>
                  </div>
                  <span className="text-sm font-bold opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" style={{ color: "var(--orange)" }}>→</span>
                </Link>
              ) : (
                <div
                  key={s.id}
                  className="flex items-center gap-4 p-4 rounded-2xl"
                  style={{ border: "1px solid var(--border)", background: "var(--surface)" }}
                >
                  <div className="w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: "#eee" }}>
                    <span style={{ fontSize: "1.5rem" }}>📍</span>
                  </div>
                  <div>
                    <div className="font-semibold text-sm mb-1" style={{ color: "var(--muted)" }}>{name}</div>
                    <div className="text-xs" style={{ color: "var(--muted)" }}>Coming soon to Bapmap</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
