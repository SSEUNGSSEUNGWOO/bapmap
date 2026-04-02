"use client";

import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import Link from "next/link";
import "mapbox-gl/dist/mapbox-gl.css";

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN!;

type Spot = {
  id: string;
  name: string;
  english_name: string;
  lat: number;
  lng: number;
  category: string;
  region: string;
  city: string;
  rating: number;
  image_url: string;
};

export default function MapClient({ spots }: { spots: Spot[] }) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [selected, setSelected] = useState<Spot | null>(null);

  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: "mapbox://styles/mapbox/light-v11",
      center: [126.9611, 37.5192],
      zoom: 11.5,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), "top-right");

    spots.forEach((spot) => {
      if (!spot.lat || !spot.lng) return;

      const el = document.createElement("div");
      el.style.cssText = `
        width: 28px; height: 28px; border-radius: 50%;
        background: #F5A623; border: 2px solid #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        cursor: pointer; transition: transform 0.15s;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px;
      `;
      el.innerHTML = "🍽";
      el.addEventListener("mouseenter", () => { el.style.transform = "scale(1.3)"; });
      el.addEventListener("mouseleave", () => { el.style.transform = "scale(1)"; });
      el.addEventListener("click", () => setSelected(spot));

      new mapboxgl.Marker(el)
        .setLngLat([spot.lng, spot.lat])
        .addTo(map.current!);
    });
  }, [spots]);

  const slug = selected
    ? (selected.english_name || selected.name).toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "")
    : "";

  return (
    <div className="relative w-full" style={{ height: "calc(100vh - 64px)" }}>
      <div ref={mapContainer} className="w-full h-full" />

      {/* 선택된 스팟 카드 */}
      {selected && (
        <div
          className="absolute bottom-6 left-1/2 -translate-x-1/2 rounded-2xl overflow-hidden shadow-2xl"
          style={{ width: "320px", background: "#fff", border: "1px solid var(--border)" }}
        >
          {selected.image_url && (
            <img src={selected.image_url} alt={selected.english_name} className="w-full object-cover" style={{ height: "140px" }} />
          )}
          <div className="p-4">
            <div className="text-[10px] font-bold tracking-widest uppercase mb-1" style={{ color: "var(--orange)" }}>
              {selected.region || selected.city}
            </div>
            <div className="font-semibold text-sm mb-1" style={{ color: "var(--ink)" }}>
              {selected.english_name || selected.name}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs" style={{ color: "var(--muted)" }}>★ {selected.rating} · {selected.category}</span>
              <Link
                href={`/spots/${slug}`}
                className="text-xs font-bold px-3 py-1.5 rounded-full text-white no-underline"
                style={{ background: "var(--orange)" }}
              >
                View →
              </Link>
            </div>
          </div>
          <button
            onClick={() => setSelected(null)}
            className="absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs"
            style={{ background: "rgba(0,0,0,0.4)", color: "#fff" }}
          >
            ✕
          </button>
        </div>
      )}

      {/* 스팟 수 */}
      <div
        className="absolute top-4 left-4 px-3 py-2 rounded-xl text-xs font-semibold"
        style={{ background: "#fff", border: "1px solid var(--border)", color: "var(--muted)", boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
      >
        {spots.length} spots on map
      </div>
    </div>
  );
}
