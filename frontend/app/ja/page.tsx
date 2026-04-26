import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import HomeClient from "../HomeClient";
import type { Metadata } from "next";

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
};

type Message = { id: string; message: string; reply: string };

export const metadata: Metadata = {
  title: "Bapmap — 韓国人が実際に食べに行くお店",
  description: "旅行者向け韓国ローカルレストランガイド。本物のスポット、正直なおすすめ。観光客向けの罠なし。",
  alternates: {
    canonical: "https://bapmap.com/ja",
    languages: {
      "en": "https://bapmap.com",
      "ja": "https://bapmap.com/ja",
    },
  },
};

export default async function JaHome() {
  const { data: recent } = await supabase
    .from("spots")
    .select("id, name, english_name, city, region, image_url, image_urls, rating, price_level, subway, tagline")
    .eq("status", "업로드완료")
    .order("created_at", { ascending: false })
    .limit(6);

  const { data: messages } = await supabase
    .from("messages")
    .select("id, message, reply")
    .eq("status", "approved")
    .order("created_at", { ascending: false })
    .limit(20);

  const { data: guides } = await supabase
    .from("guides")
    .select("id, slug, title, subtitle, title_ja, subtitle_ja, cover_image, category_tag")
    .eq("status", "published")
    .order("created_at", { ascending: false })
    .limit(3);

  const { count: spotCount } = await supabase
    .from("spots")
    .select("*", { count: "exact", head: true })
    .eq("status", "업로드완료");

  return (
    <HomeClient
      recent={(recent ?? []) as Spot[]}
      messages={(messages ?? []) as Message[]}
      guides={(guides ?? []) as Guide[]}
      spotCount={spotCount ?? 0}
    />
  );
}
