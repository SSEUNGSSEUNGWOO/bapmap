"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

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
  content?: string;
};

type ChatMessage = { role: "user" | "assistant"; content: string };

function ChatDrawer({
  open,
  onClose,
  spotsContext,
}: {
  open: boolean;
  onClose: () => void;
  spotsContext: string;
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");

    const newMessages: ChatMessage[] = [...messages, { role: "user", content: text }];
    setMessages(newMessages);
    setStreaming(true);

    let assistantText = "";
    setMessages([...newMessages, { role: "assistant", content: "" }]);

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: newMessages, spotsContext }),
    });

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      for (const line of decoder.decode(value).split("\n")) {
        if (!line.startsWith("data: ")) continue;
        try {
          const msg = JSON.parse(line.slice(6));
          if (msg.type === "text") {
            assistantText += msg.text;
            setMessages([...newMessages, { role: "assistant", content: assistantText }]);
          }
        } catch {}
      }
    }
    setStreaming(false);
  };

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-40 transition-opacity duration-300"
        style={{
          background: "rgba(0,0,0,0.15)",
          opacity: open ? 1 : 0,
          pointerEvents: open ? "auto" : "none",
        }}
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        className="fixed top-0 right-0 h-full z-50 flex flex-col transition-transform duration-300"
        style={{
          width: "min(420px, 100vw)",
          background: "#fff",
          borderLeft: "1px solid var(--border)",
          transform: open ? "translateX(0)" : "translateX(100%)",
          boxShadow: open ? "-8px 0 32px rgba(0,0,0,0.08)" : "none",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border)]">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full flex items-center justify-center" style={{ background: "var(--orange)" }}>
              <span style={{ fontSize: "11px", color: "#fff" }}>✦</span>
            </div>
            <span className="text-sm font-bold" style={{ color: "var(--ink)" }}>Ask Bapmap</span>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full flex items-center justify-center hover:opacity-60 transition-opacity"
            style={{ background: "var(--surface)", color: "var(--muted)", fontSize: "14px" }}
          >
            ✕
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-sm text-center py-8" style={{ color: "var(--muted)" }}>
              Ask anything about these spots or Korean food.
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className="max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
                style={
                  m.role === "user"
                    ? { background: "var(--orange)", color: "#fff", borderBottomRightRadius: "4px" }
                    : { background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)", borderBottomLeftRadius: "4px" }
                }
              >
                {m.role === "assistant" ? (
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => <p className="mb-1 last:mb-0">{children}</p>,
                      a: ({ href, children }) => (
                        <Link href={href || "#"} className="underline font-semibold" style={{ color: "var(--orange)" }}>{children}</Link>
                      ),
                      strong: ({ children }) => <strong style={{ fontWeight: 600 }}>{children}</strong>,
                    }}
                  >
                    {m.content || (streaming && i === messages.length - 1 ? "▌" : "")}
                  </ReactMarkdown>
                ) : (
                  m.content
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="px-4 py-4 border-t border-[var(--border)]">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
              placeholder="Ask a follow-up..."
              disabled={streaming}
              className="flex-1 rounded-full px-4 py-2.5 text-sm outline-none"
              style={{ border: "1.5px solid var(--border)", color: "var(--ink)", background: "#fff" }}
              onFocus={(e) => (e.target.style.borderColor = "var(--orange)")}
              onBlur={(e) => (e.target.style.borderColor = "var(--border)")}
            />
            <button
              onClick={send}
              disabled={streaming || !input.trim()}
              className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition-opacity hover:opacity-80 disabled:opacity-40"
              style={{ background: "var(--orange)" }}
            >
              <span className="text-white text-sm font-bold">→</span>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

function SearchPageInner() {
  const searchParams = useSearchParams();
  const q = searchParams.get("q") || "";
  const [answer, setAnswer] = useState("");
  const [spots, setSpots] = useState<Spot[]>([]);
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState(q);
  const [chatOpen, setChatOpen] = useState(false);
  const ranRef = useRef(false);

  const spotsContext = spots
    .filter((s) => s.status === "업로드완료")
    .map((s) => {
      const name = s.english_name || s.name;
      const slug = name.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
      return `${name} — ${s.category} · ${s.region || s.city} · ★${s.rating}\nLink: /spots/${slug}\n${String(s.content || "").slice(0, 150)}`;
    })
    .join("\n\n");

  const search = async (raw: string) => {
    if (!raw.trim()) return;
    setLoading(true);
    setAnswer("");
    setSpots([]);
    setSources([]);
    setChatOpen(false);
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
          if (msg.type === "sources") setSources(msg.data);
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

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-6 items-start">
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
                <div className="text-sm leading-[1.85]" style={{ color: "var(--ink)" }}>
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
                      strong: ({ children }) => <strong style={{ color: "var(--ink)", fontWeight: 600 }}>{children}</strong>,
                      a: ({ href, children }) => (
                        <Link
                          href={href || "#"}
                          className="font-semibold underline underline-offset-2 hover:opacity-70 transition-opacity"
                          style={{ color: "var(--orange)", textDecorationColor: "var(--orange)" }}
                        >
                          {children}
                        </Link>
                      ),
                      ul: ({ children }) => <ul className="mb-3 space-y-1 pl-4" style={{ listStyleType: "disc", color: "var(--muted)" }}>{children}</ul>,
                      li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                    }}
                  >
                    {answer}
                  </ReactMarkdown>
                  {loading && (
                    <span className="inline-block w-0.5 h-4 ml-0.5 align-middle animate-pulse rounded-full" style={{ background: "var(--orange)" }} />
                  )}
                </div>
              </div>
            )}

            {/* Sources */}
            {!loading && sources.length > 0 && (
              <div className="flex items-center gap-2 mb-4 flex-wrap">
                <span className="text-[10px] font-bold tracking-[0.2em] uppercase" style={{ color: "var(--muted)" }}>Sources</span>
                {sources.map((s, i) => (
                  <span key={i} className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "var(--surface)", color: "var(--muted)", border: "1px solid var(--border)" }}>
                    {s}
                  </span>
                ))}
              </div>
            )}

            {/* Ask more button */}
            {!loading && answer && (
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setChatOpen(true)}
                  className="inline-flex items-center gap-2 text-xs font-bold px-4 py-2 rounded-full transition-all hover:opacity-80"
                  style={{ background: "var(--orange)", color: "#fff" }}
                >
                  <span>✦</span> Ask a follow-up
                </button>
                <Link href="/" className="inline-flex items-center gap-1 text-xs no-underline hover:opacity-60 transition-opacity" style={{ color: "var(--muted)" }}>
                  ← Back to home
                </Link>
              </div>
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
                      <img src={s.image_url} alt={name} className="w-16 h-16 rounded-xl object-cover flex-shrink-0" />
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

      <ChatDrawer
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        spotsContext={spotsContext}
      />
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense>
      <SearchPageInner />
    </Suspense>
  );
}
