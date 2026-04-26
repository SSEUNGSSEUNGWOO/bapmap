import { supabase } from "@/lib/supabase";
import { notFound } from "next/navigation";
import { cache } from "react";
import type { Metadata } from "next";
import SpotClient from "./SpotClient";

function haversineKm(lat1: number, lng1: number, lat2: number, lng2: number) {
  const R = 6371;
  const p = Math.PI / 180;
  const a = Math.sin((lat2 - lat1) * p / 2) ** 2 +
    Math.cos(lat1 * p) * Math.cos(lat2 * p) * Math.sin((lng2 - lng1) * p / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

function toSlug(name: string) {
  return name.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
}

const getSpot = cache(async (slug: string) => {
  const { data: spots } = await supabase
    .from("spots")
    .select("id, english_name, name")
    .eq("status", "업로드완료");
  const match = spots?.find((s) => toSlug(s.english_name || s.name) === slug);
  if (!match) return null;
  const { data } = await supabase.from("spots").select("*").eq("id", match.id).single();
  return data ?? null;
});

export async function generateStaticParams() {
  const { data: spots } = await supabase
    .from("spots")
    .select("english_name, name")
    .eq("status", "업로드완료");
  return (spots ?? []).map((s) => ({ slug: toSlug(s.english_name || s.name) }));
}

async function getNearbySpots(spot: { id: string; lat: number; lng: number }) {
  const { data: spots } = await supabase
    .from("spots")
    .select("id, name, english_name, city, region, image_url, rating, lat, lng")
    .eq("status", "업로드완료")
    .neq("id", spot.id);

  if (!spots || !spot.lat || !spot.lng) return [];

  return spots
    .filter((s) => s.lat && s.lng)
    .map((s) => ({ ...s, dist: haversineKm(spot.lat, spot.lng, s.lat, s.lng) }))
    .sort((a, b) => a.dist - b.dist)
    .slice(0, 3);
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const spot = await getSpot(slug);
  if (!spot) return {};

  const title = `${spot.english_name || spot.name} — Bapmap`;
  const description = `${spot.english_name || spot.name} in ${spot.region || spot.city}, Korea. ★${spot.rating} · ${spot.price_level || "Local pick"} · ${spot.subway || ""}`.trim();

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `https://bapmap.com/spots/${slug}`,
      images: spot.image_url ? [{ url: spot.image_url, width: 800, height: 600, alt: spot.english_name }] : [],
      type: "article",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: spot.image_url ? [spot.image_url] : [],
    },
  };
}

export default async function SpotPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const spot = await getSpot(slug);
  if (!spot) notFound();

  const nearby = await getNearbySpots({ id: spot.id, lat: spot.lat, lng: spot.lng });

  const images: string[] = Array.isArray(spot.image_urls) && spot.image_urls.length > 0
    ? spot.image_urls
    : spot.image_url ? [spot.image_url] : [];

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "name": spot.english_name || spot.name,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": spot.english_address || spot.address,
      "addressLocality": spot.city,
      "addressRegion": spot.region,
      "addressCountry": "KR",
    },
    "geo": spot.lat && spot.lng ? {
      "@type": "GeoCoordinates",
      "latitude": spot.lat,
      "longitude": spot.lng,
    } : undefined,
    "aggregateRating": spot.rating ? {
      "@type": "AggregateRating",
      "ratingValue": spot.rating,
      "reviewCount": spot.rating_count || 1,
      "bestRating": 5,
    } : undefined,
    "priceRange": spot.price_level || undefined,
    "servesCuisine": spot.category || undefined,
    "image": images[0] || undefined,
    "url": `https://bapmap.com/spots/${slug}`,
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <SpotClient spot={spot} nearby={nearby} images={images} />
    </>
  );
}
