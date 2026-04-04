"use client";

import { useState } from "react";

export default function AskCard() {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      await fetch("/api/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text.trim(), email: email.trim() || null }),
      });
      setSent(true);
      setText("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => { setOpen(true); setSent(false); }}
        className="group block no-underline w-full text-left"
      >
        <article
          className="rounded-2xl overflow-hidden border border-[var(--border)] transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-xl h-full flex flex-col justify-between"
          style={{ background: "var(--ink)", minHeight: "220px", padding: "2rem" }}
        >
          <p className="text-[9px] font-bold tracking-[0.2em] uppercase" style={{ color: "var(--orange)" }}>
            Ask a local
          </p>
          <div>
            <h2
              className="font-display text-white leading-tight m-0 mb-3"
              style={{ fontSize: "1.5rem", letterSpacing: "-0.02em" }}
            >
              Not sure where to go?
            </h2>
            <p className="text-sm m-0" style={{ color: "rgba(255,255,255,0.5)", lineHeight: 1.6 }}>
              Ask Seungwoo — I reply personally to every question.
            </p>
          </div>
          <div
            className="mt-6 inline-flex items-center gap-2 text-sm font-semibold"
            style={{ color: "var(--orange)" }}
          >
            Ask a question →
          </div>
        </article>
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center px-4 pb-4 sm:pb-0"
          style={{ background: "rgba(0,0,0,0.5)", backdropFilter: "blur(4px)" }}
          onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}
        >
          <div
            className="w-full rounded-2xl p-6"
            style={{ maxWidth: "480px", background: "#fff", boxShadow: "0 24px 64px rgba(0,0,0,0.2)" }}
          >
            {sent ? (
              <div className="text-center py-4">
                <div className="text-3xl mb-3">✦</div>
                <p className="font-semibold text-base mb-1" style={{ color: "var(--ink)" }}>Got it.</p>
                <p className="text-sm" style={{ color: "var(--muted)" }}>I'll get back to you personally — and your answer might show up on the site.</p>
                <button
                  onClick={() => setOpen(false)}
                  className="mt-5 px-5 py-2.5 rounded-full text-sm font-semibold text-white"
                  style={{ background: "var(--orange)" }}
                >
                  Close
                </button>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-display text-lg" style={{ color: "var(--ink)", letterSpacing: "-0.02em" }}>
                    Ask Seungwoo
                  </h3>
                  <button onClick={() => setOpen(false)} className="text-xl leading-none" style={{ color: "var(--muted)" }}>×</button>
                </div>
                <p className="text-xs mb-4" style={{ color: "var(--muted)" }}>
                  I read every message and reply personally.
                </p>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="e.g. Where to eat late night in Hongdae?"
                  className="w-full rounded-xl px-4 py-3 text-sm resize-none outline-none"
                  style={{
                    border: "1.5px solid var(--border)",
                    color: "var(--ink)",
                    background: "var(--surface)",
                    minHeight: "100px",
                  }}
                  onKeyDown={(e) => { if (e.key === "Enter" && e.metaKey) submit(); }}
                />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email (optional) — we'll notify you when answered"
                  className="mt-2 w-full rounded-xl px-4 py-2.5 text-sm outline-none"
                  style={{
                    border: "1.5px solid var(--border)",
                    color: "var(--ink)",
                    background: "var(--surface)",
                  }}
                />
                <button
                  onClick={submit}
                  disabled={loading || !text.trim()}
                  className="mt-3 w-full py-3 rounded-full text-sm font-semibold text-white transition-opacity"
                  style={{ background: "var(--orange)", opacity: loading || !text.trim() ? 0.5 : 1 }}
                >
                  {loading ? "Sending..." : "Send →"}
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
