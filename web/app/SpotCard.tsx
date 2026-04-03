"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import type { Spot } from "@/lib/supabase";

function SpotCardImage({ images, name }: { images: string[]; name: string }) {
  const [idx, setIdx] = useState(0);
  const [hovering, setHovering] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const handleMouseEnter = () => {
    if (images.length <= 1) return;
    setHovering(true);
    intervalRef.current = setInterval(() => {
      setIdx((prev) => (prev + 1) % images.length);
    }, 700);
  };

  const handleMouseLeave = () => {
    setHovering(false);
    if (intervalRef.current) clearInterval(intervalRef.current);
    setIdx(0);
  };

  return (
    <div className="h-48 overflow-hidden bg-gray-100 relative" onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave}>
      {images.map((url, i) => (
        <img
          key={i}
          src={url}
          alt={`${name} ${i + 1}`}
          className="absolute inset-0 w-full h-full object-cover transition-opacity duration-300"
          style={{ opacity: idx === i ? 1 : 0 }}
        />
      ))}
      {images.length > 1 && hovering && (
        <div className="absolute bottom-2 left-0 right-0 flex justify-center gap-1 z-10">
          {images.map((_, i) => (
            <div key={i} className="w-1.5 h-1.5 rounded-full transition-all" style={{ background: idx === i ? "#fff" : "rgba(255,255,255,0.5)" }} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function SpotCard({ spot }: { spot: Spot }) {
  const slug = (spot.english_name || spot.name).toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
  const images = Array.isArray(spot.image_urls) && spot.image_urls.length > 0
    ? spot.image_urls.slice(0, 3)
    : spot.image_url ? [spot.image_url] : [];

  return (
    <Link href={`/spots/${slug}`} className="group block no-underline h-full">
      <div className="bg-white rounded-2xl overflow-hidden border border-[var(--border)] group-hover:shadow-xl group-hover:-translate-y-1 transition-all duration-200 h-full flex flex-col">
        {images.length > 0 ? (
          <SpotCardImage images={images} name={spot.english_name || spot.name} />
        ) : (
          <div className="h-48 bg-[#faf8f5] flex items-center justify-center">
            <span style={{ fontSize: "2.5rem" }}>🍜</span>
          </div>
        )}
        <div className="p-4 flex flex-col flex-1">
          <div className="text-[10px] font-bold tracking-widest uppercase mb-1" style={{ color: "var(--orange)" }}>
            {spot.region || spot.city}
          </div>
          <div className="font-semibold text-sm mb-1.5 line-clamp-2" style={{ color: "var(--ink)" }}>{spot.english_name || spot.name}</div>
          {spot.tagline && (
            <p className="text-xs italic mb-2 line-clamp-1" style={{ color: "var(--muted)" }}>"{spot.tagline}"</p>
          )}
          <div className="flex items-center gap-3 mt-auto">
            <span className="text-xs" style={{ color: "var(--muted)" }}>★ {spot.rating}</span>
            {spot.price_level && <span className="text-xs" style={{ color: "var(--muted)" }}>{spot.price_level}</span>}
          </div>
        </div>
      </div>
    </Link>
  );
}
