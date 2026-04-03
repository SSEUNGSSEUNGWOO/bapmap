"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const router = useRouter();

  const submit = (q: string) => {
    if (!q.trim()) return;
    router.push(`/search?q=${encodeURIComponent(q.trim())}`);
  };

  const suggestions = [
    "spicy food near Hongdae",
    "ramen in Seongsu",
    "Korean BBQ for groups",
    "cheap eats in Gangnam",
  ];

  return (
    <div className="w-full max-w-xl mx-auto">
      <form onSubmit={(e) => { e.preventDefault(); submit(query); }} className="relative">
        <input
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
          className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full flex items-center justify-center hover:opacity-80 transition-opacity"
          style={{ background: "var(--orange)" }}
        >
          <span className="text-white text-sm font-bold">→</span>
        </button>
      </form>

      <div className="flex flex-wrap gap-2 mt-3 justify-center">
        {suggestions.map((s) => (
          <button
            key={s}
            onClick={() => submit(s)}
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
    </div>
  );
}
