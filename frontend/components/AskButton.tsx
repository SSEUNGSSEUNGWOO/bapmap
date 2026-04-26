"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { useLang } from "@/lib/LanguageContext";

const T = {
  en: {
    btnLabel: "Ask a local",
    modalTitle: "Ask Seungwoo",
    modalDesc: "I read every message and reply personally.",
    placeholder: "e.g. Where to eat late night in Hongdae?",
    emailPlaceholder: "Email (optional) — we'll notify you when answered",
    send: "Send →",
    sending: "Sending...",
    sentTitle: "Got it.",
    sentDesc: "I'll get back to you personally — and your answer might show up on the site.",
    close: "Close",
  },
  ja: {
    btnLabel: "ローカルに聞く",
    modalTitle: "スンウに聞く",
    modalDesc: "すべてのメッセージを読んで、個人的に返信します。",
    placeholder: "例: 弘大で深夜に食べられる場所は？",
    emailPlaceholder: "メール（任意）— 回答時にお知らせします",
    send: "送信 →",
    sending: "送信中...",
    sentTitle: "受け取りました。",
    sentDesc: "個人的に返信します — 回答がサイトに掲載されることもあります。",
    close: "閉じる",
  },
};

export default function AskButton() {
  const pathname = usePathname();
  const { lang } = useLang();
  const t = T[lang];
  if (pathname === "/search") return null;
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
      {/* Floating Button */}
      <button
        onClick={() => { setOpen(true); setSent(false); }}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-full text-white text-sm font-semibold shadow-lg transition-all duration-200 hover:scale-105 hover:opacity-90"
        style={{ background: "var(--orange)", boxShadow: "0 4px 20px rgba(245,166,35,0.45)" }}
      >
        <span>✦</span>
        <span>{t.btnLabel}</span>
      </button>

      {/* Modal */}
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
                <p className="font-semibold text-base mb-1" style={{ color: "var(--ink)" }}>{t.sentTitle}</p>
                <p className="text-sm" style={{ color: "var(--muted)" }}>{t.sentDesc}</p>
                <button
                  onClick={() => setOpen(false)}
                  className="mt-5 px-5 py-2.5 rounded-full text-sm font-semibold text-white"
                  style={{ background: "var(--orange)" }}
                >
                  {t.close}
                </button>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-display text-lg" style={{ color: "var(--ink)", letterSpacing: "-0.02em" }}>
                    {t.modalTitle}
                  </h3>
                  <button onClick={() => setOpen(false)} className="text-xl leading-none" style={{ color: "var(--muted)" }}>×</button>
                </div>
                <p className="text-xs mb-4" style={{ color: "var(--muted)" }}>
                  {t.modalDesc}
                </p>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={t.placeholder}
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
                  placeholder={t.emailPlaceholder}
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
                  {loading ? t.sending : t.send}
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
