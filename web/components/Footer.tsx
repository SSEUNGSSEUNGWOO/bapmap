"use client";

import { useLang } from "@/lib/LanguageContext";

export default function Footer() {
  const { lang } = useLang();
  const text = lang === "ja"
    ? "© 2026 Bapmap · 韓国グルメ、あなたのための地図"
    : "© 2026 Bapmap · Korean Food, Mapped for You";

  return (
    <footer style={{ borderTop: "1px solid var(--border)", marginTop: "6rem", padding: "2rem 1rem", textAlign: "center", fontSize: "0.8rem", color: "var(--muted)" }}>
      {text}
    </footer>
  );
}
