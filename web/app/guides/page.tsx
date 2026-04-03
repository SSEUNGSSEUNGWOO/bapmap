import { supabase } from "@/lib/supabase";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Food Guides | Bapmap",
  description: "Curated food guides for Korea — late night eats, budget spots, solo dining, and more.",
};

export const revalidate = 300;

type Guide = {
  id: string;
  slug: string;
  title: string;
  subtitle: string;
  cover_image: string;
  category_tag: string;
  created_at: string;
};

export default async function GuidesPage() {
  const { data: guides } = await supabase
    .from("guides")
    .select("id, slug, title, subtitle, cover_image, category_tag, created_at")
    .eq("status", "published")
    .order("created_at", { ascending: false });

  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      {/* Header */}
      <div className="mb-14">
        <p className="text-[10px] font-bold tracking-[0.25em] uppercase mb-3" style={{ color: "var(--orange)" }}>
          Bapmap Guides
        </p>
        <h1
          className="font-display m-0"
          style={{ fontSize: "clamp(2.5rem,6vw,4rem)", color: "var(--ink)", letterSpacing: "-0.03em", lineHeight: 1.05 }}
        >
          Eat with purpose.
        </h1>
        <p className="mt-4 text-base leading-relaxed" style={{ color: "var(--muted)", maxWidth: "480px" }}>
          Not just lists. Real situations, real picks — for every kind of night in Korea.
        </p>
      </div>

      {/* Guide Grid */}
      {!guides || guides.length === 0 ? (
        <p style={{ color: "var(--muted)" }}>Guides coming soon.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {(guides as Guide[]).map((guide, i) => (
            <Link
              key={guide.id}
              href={`/guides/${guide.slug}`}
              className="group block no-underline"
            >
              <article
                className="rounded-2xl overflow-hidden border border-[var(--border)] transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-xl"
                style={{ background: "var(--surface)" }}
              >
                {/* Cover Image */}
                <div className="relative overflow-hidden" style={{ height: i === 0 ? "320px" : "220px" }}>
                  {guide.cover_image ? (
                    <img
                      src={guide.cover_image}
                      alt={guide.title}
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                    />
                  ) : (
                    <div className="w-full h-full" style={{ background: "var(--ink)" }} />
                  )}
                  <div
                    className="absolute inset-0"
                    style={{ background: "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.1) 60%)" }}
                  />
                  {guide.category_tag && (
                    <div className="absolute top-4 left-4">
                      <span
                        className="text-[9px] font-bold tracking-[0.2em] uppercase px-2.5 py-1 rounded-full"
                        style={{ background: "var(--orange)", color: "#fff" }}
                      >
                        {guide.category_tag}
                      </span>
                    </div>
                  )}
                  <div className="absolute bottom-0 left-0 p-6">
                    <h2
                      className="font-display text-white m-0 leading-tight"
                      style={{ fontSize: i === 0 ? "2rem" : "1.4rem", letterSpacing: "-0.02em" }}
                    >
                      {guide.title}
                    </h2>
                  </div>
                </div>

                {/* Body */}
                {guide.subtitle && (
                  <div className="px-5 py-4">
                    <p className="text-sm leading-relaxed m-0" style={{ color: "var(--muted)" }}>
                      {guide.subtitle}
                    </p>
                  </div>
                )}
              </article>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
