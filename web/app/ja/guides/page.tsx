import { supabase } from "@/lib/supabase";
import type { Metadata } from "next";
import GuidesClient from "../../guides/GuidesClient";

export const revalidate = 300;

export const metadata: Metadata = {
  title: "フードガイド | Bapmap",
  description: "韓国グルメガイド — 深夜グルメ、コスパ店、一人飯など厳選キュレーション。",
  alternates: {
    canonical: "https://bapmap.com/ja/guides",
    languages: {
      "en": "https://bapmap.com/guides",
      "ja": "https://bapmap.com/ja/guides",
    },
  },
};

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

export default async function JaGuidesPage() {
  const { data: guides } = await supabase
    .from("guides")
    .select("id, slug, title, subtitle, title_ja, subtitle_ja, cover_image, category_tag, created_at")
    .eq("status", "published")
    .order("created_at", { ascending: false });

  return <GuidesClient guides={(guides ?? []) as Guide[]} />;
}
