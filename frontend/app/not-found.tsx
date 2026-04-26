import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center px-6 text-center">
      <div className="text-5xl mb-6">🍜</div>
      <p className="text-xs font-bold tracking-[0.2em] uppercase mb-2" style={{ color: "var(--orange)" }}>
        Coming Soon
      </p>
      <h1 className="font-display mb-3" style={{ fontSize: "clamp(1.8rem,4vw,2.8rem)", color: "var(--ink)", letterSpacing: "-0.02em" }}>
        This spot isn't on the map yet
      </h1>
      <p className="text-sm mb-8 max-w-xs" style={{ color: "var(--muted)" }}>
        We're still curating this one. Check back soon — or explore what's already here.
      </p>
      <Link
        href="/spots"
        className="px-6 py-3 rounded-full text-sm font-semibold no-underline transition-all hover:opacity-80"
        style={{ background: "var(--orange)", color: "#fff" }}
      >
        Browse all spots →
      </Link>
    </div>
  );
}
