"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useLang } from "@/lib/LanguageContext";

const NAV_EN = [
  { label: "Spots", href: "/spots" },
  { label: "Guides", href: "/guides" },
  { label: "Map", href: "/map" },
  { label: "About", href: "/about" },
];

const NAV_JA = [
  { label: "スポット", href: "/spots" },
  { label: "ガイド", href: "/guides" },
  { label: "マップ", href: "/map" },
  { label: "について", href: "/about" },
];

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();
  const isHome = pathname === "/";
  const { lang, setLang, p } = useLang();
  const NAV = (lang === "ja" ? NAV_JA : NAV_EN).map((n) => ({ ...n, href: p(n.href) }));
  const searchLabel = lang === "ja" ? "検索 ✦" : "Search ✦";

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  const transparent = isHome && !scrolled && !menuOpen;

  return (
    <header
      className="sticky top-0 z-50 transition-all duration-500"
      style={{
        background: transparent ? "rgba(0,0,0,0.35)" : "rgba(255,255,255,0.92)",
        backdropFilter: "blur(16px)",
        borderBottom: transparent ? "1px solid rgba(255,255,255,0.1)" : "1px solid var(--border)",
        boxShadow: transparent ? "none" : "0 1px 24px rgba(0,0,0,0.06)",
      }}
    >
      <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href={p("/")} className="flex items-center no-underline">
          <Image
            src="/logo.svg"
            alt="Bapmap"
            width={120}
            height={37}
            style={{
              objectFit: "contain",
              filter: transparent ? "brightness(0) invert(1)" : "none",
              transition: "filter 0.5s ease",
            }}
          />
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-1">
          {NAV.map(({ label, href }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className="relative no-underline px-4 py-2 text-sm font-semibold tracking-wide transition-all duration-200 rounded-full"
                style={{
                  color: transparent ? (active ? "#fff" : "rgba(255,255,255,0.7)") : (active ? "var(--orange)" : "var(--muted)"),
                  background: active && !transparent ? "rgba(245,166,35,0.08)" : "transparent",
                  letterSpacing: "0.04em",
                }}
                onMouseEnter={(e) => {
                  if (!active) {
                    (e.currentTarget as HTMLElement).style.color = transparent ? "#fff" : "var(--orange)";
                    (e.currentTarget as HTMLElement).style.background = transparent ? "rgba(255,255,255,0.12)" : "rgba(245,166,35,0.08)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!active) {
                    (e.currentTarget as HTMLElement).style.color = transparent ? "rgba(255,255,255,0.7)" : "var(--muted)";
                    (e.currentTarget as HTMLElement).style.background = "transparent";
                  }
                }}
              >
                {label}
                {active && !transparent && (
                  <span className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full" style={{ background: "var(--orange)" }} />
                )}
              </Link>
            );
          })}
          <div className="ml-3 flex items-center rounded-full overflow-hidden" style={{ border: "1px solid var(--border)", background: transparent ? "rgba(255,255,255,0.1)" : "var(--surface)" }}>
            {(["en", "ja"] as const).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className="px-3 py-1.5 text-xs font-bold tracking-wide uppercase transition-all duration-200"
                style={{
                  background: lang === l ? "var(--orange)" : "transparent",
                  color: lang === l ? "#fff" : transparent ? "rgba(255,255,255,0.6)" : "var(--muted)",
                }}
              >
                {l === "en" ? "EN" : "JP"}
              </button>
            ))}
          </div>
          <Link
            href={p("/search")}
            className="ml-3 no-underline px-4 py-2 rounded-full text-sm font-semibold tracking-wide transition-all duration-200 hover:opacity-80"
            style={{ background: "var(--orange)", color: "#fff", boxShadow: "0 2px 12px rgba(245,166,35,0.35)" }}
          >
            {searchLabel}
          </Link>
        </nav>

        {/* Mobile: Search + Hamburger */}
        <div className="flex md:hidden items-center gap-2">
          <Link
            href={p("/search")}
            className="no-underline w-9 h-9 rounded-full flex items-center justify-center"
            style={{ background: "var(--orange)" }}
          >
            <span className="text-white text-xs font-bold">✦</span>
          </Link>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="w-9 h-9 flex flex-col items-center justify-center gap-1.5 rounded-full transition-all"
            style={{ background: transparent ? "rgba(255,255,255,0.15)" : "var(--surface)", border: "1px solid " + (transparent ? "rgba(255,255,255,0.3)" : "var(--border)") }}
          >
            <span className="block w-4 h-0.5 transition-all" style={{ background: transparent ? "#fff" : "var(--ink)", transform: menuOpen ? "rotate(45deg) translate(2px, 2px)" : "none" }} />
            <span className="block h-0.5 transition-all" style={{ background: transparent ? "#fff" : "var(--ink)", width: menuOpen ? "1rem" : "0.75rem", opacity: menuOpen ? 0 : 1 }} />
            <span className="block w-4 h-0.5 transition-all" style={{ background: transparent ? "#fff" : "var(--ink)", transform: menuOpen ? "rotate(-45deg) translate(2px, -2px)" : "none" }} />
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="md:hidden border-t" style={{ background: "rgba(255,255,255,0.97)", borderColor: "var(--border)" }}>
          <div className="px-6 py-4 flex flex-col gap-1">
            {NAV.map(({ label, href }) => (
              <Link
                key={href}
                href={href}
                className="no-underline py-3 px-4 rounded-xl text-sm font-semibold transition-all"
                style={{
                  color: pathname === href ? "var(--orange)" : "var(--ink)",
                  background: pathname === href ? "rgba(245,166,35,0.08)" : "transparent",
                }}
              >
                {label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}
