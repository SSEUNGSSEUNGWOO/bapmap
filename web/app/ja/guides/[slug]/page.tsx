import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import GuideContent from "../../../guides/[slug]/GuideContent";

export const revalidate = 300;

type Guide = {
  id: string;
  slug: string;
  title: string;
  subtitle: string;
  cover_image: string;
  category_tag: string;
  intro: string;
  body: string;
  title_ja?: string;
  subtitle_ja?: string;
  intro_ja?: string;
  body_ja?: string;
  spot_slugs: string[];
  created_at: string;
};

type Segment =
  | { type: "text"; content: string }
  | { type: "spot"; name: string };

function parseBody(body: string): Segment[] {
  const parts = body.split(/\[spot:([^\]]+)\]/g);
  const segments: Segment[] = [];
  parts.forEach((part, i) => {
    if (i % 2 === 0) {
      if (part.trim()) segments.push({ type: "text", content: part });
    } else {
      segments.push({ type: "spot", name: part.trim() });
    }
  });
  return segments;
}

export async function generateStaticParams() {
  const { data } = await supabase
    .from("guides")
    .select("slug")
    .eq("status", "published");
  return (data ?? []).map((g) => ({ slug: g.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const { data } = await supabase
    .from("guides")
    .select("title, subtitle, title_ja, subtitle_ja")
    .eq("slug", slug)
    .single();
  if (!data) return {};
  return {
    title: `${data.title_ja || data.title} | Bapmap`,
    description: data.subtitle_ja || data.subtitle || "",
    alternates: {
      canonical: `https://bapmap.com/ja/guides/${slug}`,
      languages: {
        "en": `https://bapmap.com/guides/${slug}`,
        "ja": `https://bapmap.com/ja/guides/${slug}`,
      },
    },
  };
}

export default async function JaGuidePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  const { data: guide } = await supabase
    .from("guides")
    .select("*")
    .eq("slug", slug)
    .eq("status", "published")
    .single();

  if (!guide) notFound();

  const g = guide as Guide;

  let spots: Spot[] = [];
  if (g.spot_slugs && g.spot_slugs.length > 0) {
    const { data: spotData } = await supabase
      .from("spots")
      .select("id, name, english_name, city, region, image_url, image_urls, rating, category, price_level, subway, tagline")
      .eq("status", "업로드완료")
      .in("english_name", g.spot_slugs);

    const orderMap = Object.fromEntries(g.spot_slugs.map((s, i) => [s, i]));
    spots = ((spotData ?? []) as Spot[]).sort((a, b) =>
      (orderMap[a.english_name] ?? 99) - (orderMap[b.english_name] ?? 99)
    );
  }

  const spotMap = Object.fromEntries(spots.map((s) => [s.english_name, s]));
  const segments = g.body ? parseBody(g.body) : [];
  const segmentsJa = g.body_ja ? parseBody(g.body_ja) : [];
  const hasInlineSpots = segments.some((s) => s.type === "spot");

  return (
    <GuideContent
      guide={g}
      spots={spots}
      segments={segments}
      segmentsJa={segmentsJa}
      spotMap={spotMap}
      hasInlineSpots={hasInlineSpots}
    />
  );
}
