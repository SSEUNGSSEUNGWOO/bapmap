import { supabase } from "@/lib/supabase";
import type { Metadata } from "next";
import GuidesClient from "./GuidesClient";

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
  title_ja?: string;
  subtitle_ja?: string;
  cover_image: string;
  category_tag: string;
  created_at: string;
};

export default async function GuidesPage() {
  const { data: guides } = await supabase
    .from("guides")
    .select("id, slug, title, subtitle, title_ja, subtitle_ja, cover_image, category_tag, created_at")
    .eq("status", "published")
    .order("created_at", { ascending: false });

  return <GuidesClient guides={(guides ?? []) as Guide[]} />;
}
