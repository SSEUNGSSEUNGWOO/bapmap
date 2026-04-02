import Link from "next/link";
import Image from "next/image";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-[var(--border)]">
      <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link href="/">
          <Image src="/logo.png" alt="Bapmap" width={90} height={28} style={{ objectFit: "contain" }} />
        </Link>
        <nav className="flex gap-8">
          {[["Spots", "/spots"], ["About", "/about"]].map(([label, href]) => (
            <Link key={href} href={href}
              className="text-sm font-medium no-underline hover:text-[#F5A623] transition-colors"
              style={{ color: "var(--muted)" }}
            >
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
