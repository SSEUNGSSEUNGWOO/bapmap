"use client";

import { useState, useRef } from "react";
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

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [spots, setSpots] = useState<Spot[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const search = async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setAnswer("");
    setSpots([]);
    setOpen(true);

    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q }),
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    search(query);
  };

  const suggestions = [
    "spicy food near Hongdae",
    "ramen in Seongsu",
    "Korean BBQ for groups",
    "cheap eats in Gangnam",
  ];

  return (
    <div className="w-full max-w-xl mx-auto">
      {/* Search Input */}
      <form onSubmit={handleSubmit} className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. spicy ramen near Hongdae..."
          className="w-full rounded-full px-6 py-4 pr-14 text-sm outline-none"
          style={{
            background: "rgba(255,255,255,0.12)",
            backdropFilter: "blur(12px)",
            border: "1px solid rgba(255,255,255,0.25)",
            color: "#fff",
            boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
          }}
        />
        <button
          type="submit"
          disabled={loading}
          className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full flex items-center justify-center transition-opacity hover:opacity-80"
          style={{ background: "var(--orange)" }}
        >
          {loading ? (
            <svg className="animate-spin w-4 h-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
          ) : (
            <span className="text-white text-sm font-bold">→</span>
          )}
        </button>
      </form>

      {/* Suggestions */}
      {!open && (
        <div className="flex flex-wrap gap-2 mt-3 justify-center">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => { setQuery(s); search(s); }}
              className="text-[11px] px-3 py-1.5 rounded-full transition-all hover:opacity-80"
              style={{
                background: "rgba(255,255,255,0.1)",
                border: "1px solid rgba(255,255,255,0.2)",
                color: "rgba(255,255,255,0.7)",
              }}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Results Panel */}
      {open && (
        <div
          className="mt-3 rounded-2xl overflow-hidden"
          style={{
            background: "rgba(255,255,255,0.97)",
            boxShadow: "0 16px 48px rgba(0,0,0,0.25)",
          }}
        >
          {/* Answer */}
          <div className="p-5">
            {(answer || loading) && (
              <div className="text-sm leading-relaxed mb-4" style={{ color: "#1a1a1a" }}>
                {answer || <span style={{ color: "#aaa" }}>Searching...</span>}
                {loading && answer && <span className="inline-block w-1 h-4 ml-0.5 align-middle animate-pulse" style={{ background: "var(--orange)" }} />}
              </div>
            )}

            {/* Spot chips */}
            {spots.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {spots.map((s) => {
                  const name = s.english_name || s.name;
                  const slug = name.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
                  const published = s.status === "업로드완료";
                  return published ? (
                    <Link
                      key={s.id}
                      href={`/spots/${slug}`}
                      className="flex items-center gap-2 no-underline px-3 py-1.5 rounded-full text-xs font-semibold transition-all hover:opacity-80"
                      style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--ink)" }}
                    >
                      {s.image_url && (
                        <img src={s.image_url} alt={name} className="w-5 h-5 rounded-full object-cover" />
                      )}
                      {name}
                      <span style={{ color: "var(--orange)" }}>→</span>
                    </Link>
                  ) : (
                    <span
                      key={s.id}
                      className="px-3 py-1.5 rounded-full text-xs font-semibold"
                      style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--muted)" }}
                    >
                      📍 {name} — soon
                    </span>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          <div
            className="px-5 py-3 flex items-center justify-between"
            style={{ borderTop: "1px solid var(--border)" }}
          >
            <span className="text-[11px]" style={{ color: "var(--muted)" }}>
              Powered by Bapmap AI
            </span>
            <button
              onClick={() => { setOpen(false); setAnswer(""); setSpots([]); setQuery(""); }}
              className="text-[11px] font-semibold hover:opacity-60 transition-opacity"
              style={{ color: "var(--muted)" }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
