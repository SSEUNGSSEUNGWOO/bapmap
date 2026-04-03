"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

const NAV = [
  { label: "Spots", href: "/spots" },
  { label: "Map", href: "/map" },
  { label: "About", href: "/about" },
];

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();
  const isHome = pathname === "/";

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const transparent = isHome && !scrolled;

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
        <Link href="/" className="flex items-center no-underline group">
          <div className="relative overflow-hidden">
            <Image
              src="/logo.png"
              alt="Bapmap"
              width={110}
              height={34}
              style={{
                objectFit: "contain",
                filter: transparent ? "brightness(0) invert(1)" : "none",
                transition: "filter 0.5s ease",
              }}
            />
          </div>
        </Link>

        {/* Nav */}
        <nav className="flex items-center gap-1">
          {NAV.map(({ label, href }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className="relative no-underline px-4 py-2 text-sm font-semibold tracking-wide transition-all duration-200 rounded-full"
                style={{
                  color: transparent
                    ? active ? "#fff" : "rgba(255,255,255,0.7)"
                    : active ? "var(--orange)" : "var(--muted)",
                  background: active && !transparent ? "rgba(245,166,35,0.08)" : "transparent",
                  letterSpacing: "0.04em",
                }}
                onMouseEnter={(e) => {
                  if (!active) {
                    (e.currentTarget as HTMLElement).style.color = transparent ? "#fff" : "var(--orange)";
                    (e.currentTarget as HTMLElement).style.background = transparent
                      ? "rgba(255,255,255,0.12)"
                      : "rgba(245,166,35,0.08)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!active) {
                    (e.currentTarget as HTMLElement).style.color = transparent
                      ? "rgba(255,255,255,0.7)"
                      : "var(--muted)";
                    (e.currentTarget as HTMLElement).style.background = "transparent";
                  }
                }}
              >
                {label}
                {active && !transparent && (
                  <span
                    className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full"
                    style={{ background: "var(--orange)" }}
                  />
                )}
              </Link>
            );
          })}

          {/* CTA */}
          <Link
            href="/search"
            className="ml-3 no-underline px-4 py-2 rounded-full text-sm font-semibold tracking-wide transition-all duration-200 hover:opacity-80 hover:scale-[0.97]"
            style={{
              background: "var(--orange)",
              color: "#fff",
              letterSpacing: "0.04em",
              boxShadow: "0 2px 12px rgba(245,166,35,0.35)",
            }}
          >
            Search ✦
          </Link>
        </nav>
      </div>
    </header>
  );
}
