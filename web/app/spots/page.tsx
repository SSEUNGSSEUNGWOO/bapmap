import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import SpotsClient from "./SpotsClient";

export const revalidate = 60;

export default async function SpotsPage() {
  const { data: spots } = await supabase
    .from("spots")
    .select("id, name, english_name, city, region, image_url, image_urls, rating, category, price_level, subway")
    .eq("status", "업로드완료")
    .order("created_at", { ascending: false });

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <p className="text-xs font-bold tracking-[0.2em] uppercase mb-2" style={{ color: "var(--orange)" }}>The list</p>
      <h1 className="font-display mb-3" style={{ fontSize: "clamp(2.5rem,6vw,4rem)", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
        Where Koreans Eat
      </h1>
      <p className="mb-10" style={{ color: "var(--muted)" }}>No tourist traps. No sponsored picks. Just the real thing.</p>

      <SpotsClient spots={(spots ?? []) as Spot[]} />
    </div>
  );
}
