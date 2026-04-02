"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
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

      const slug = (spot.english_name || spot.name).toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");

      const el = document.createElement("div");
      el.style.cssText = "width: 28px; height: 28px; cursor: pointer;";
      const inner = document.createElement("div");
      inner.style.cssText = `
        width: 28px; height: 28px; border-radius: 50%;
        background: #F5A623; border: 2px solid #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: transform 0.15s;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px;
      `;
      inner.innerHTML = "🍽";
      el.appendChild(inner);
      el.addEventListener("mouseenter", () => { inner.style.transform = "scale(1.3)"; });
      el.addEventListener("mouseleave", () => { inner.style.transform = "scale(1)"; });

      const popupHtml = `
        <div style="width:220px; font-family: inherit;">
          ${spot.image_url ? `<img src="${spot.image_url}" style="width:100%; height:120px; object-fit:cover; border-radius:8px 8px 0 0; display:block;" />` : ""}
          <div style="padding: 10px 12px 12px;">
            <div style="font-size:9px; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:#F5A623; margin-bottom:4px;">
              ${spot.region || spot.city}
            </div>
            <div style="font-size:13px; font-weight:600; color:#1a1a1a; margin-bottom:6px; line-height:1.3;">
              ${spot.english_name || spot.name}
            </div>
            <div style="display:flex; align-items:center; justify-content:space-between;">
              <span style="font-size:11px; color:#888;">★ ${spot.rating} · ${spot.category || ""}</span>
              <a href="/spots/${slug}" style="font-size:11px; font-weight:700; padding:4px 10px; border-radius:20px; background:#F5A623; color:#fff; text-decoration:none;">
                View →
              </a>
            </div>
          </div>
        </div>
      `;

      const popup = new mapboxgl.Popup({
        offset: 16,
        closeButton: true,
        closeOnClick: false,
        maxWidth: "240px",
      }).setHTML(popupHtml);

      new mapboxgl.Marker(el)
        .setLngLat([spot.lng, spot.lat])
        .setPopup(popup)
        .addTo(map.current!);
    });
  }, [spots]);

  return (
    <div className="relative w-full" style={{ height: "calc(100vh - 64px)" }}>
      <div ref={mapContainer} className="w-full h-full" />
      <div
        className="absolute top-4 left-4 px-3 py-2 rounded-xl text-xs font-semibold"
        style={{ background: "#fff", border: "1px solid var(--border)", color: "var(--muted)", boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
      >
        {spots.length} spots on map
      </div>
    </div>
  );
}
