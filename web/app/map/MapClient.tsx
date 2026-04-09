"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { useLang } from "@/lib/LanguageContext";

const CATEGORY_JA: Record<string, string> = {
  "Asian": "アジア料理",
  "Bakery & Cafe": "ベーカリー・カフェ",
  "Bar": "バー",
  "Chinese": "中華料理",
  "Gopchang": "ホルモン焼き",
  "Italian": "イタリア料理",
  "Japanese": "日本料理",
  "Korean": "韓国料理",
  "Korean BBQ": "韓国焼肉",
  "Korean Soup": "韓国スープ",
  "Noodles": "麺料理",
  "Pizza": "ピザ",
  "Seafood": "海鮮",
  "Street Food": "屋台料理",
  "Tteokbokki": "トッポッキ",
  "Western": "洋食",
};

const REGION_JA: Record<string, string> = {
  "Dongdaemun District": "東大門区", "Dongdaemun-gu": "東大門区",
  "Dongjak District": "銅雀区", "Dongjak-gu": "銅雀区",
  "Gangnam District": "江南区", "Gangnam-gu": "江南区",
  "Guro District": "九老区", "Guro-gu": "九老区",
  "Gwanak District": "冠岳区", "Gwanak-gu": "冠岳区",
  "Gwangjin District": "広津区", "Gwangjin-gu": "広津区",
  "Jongno District": "鍾路区", "Jongno-gu": "鍾路区",
  "Jung District": "中区", "Jung-gu": "中区",
  "Mapo District": "麻浦区", "Mapo-gu": "麻浦区",
  "Seocho District": "瑞草区", "Seocho-gu": "瑞草区",
  "Seodaemun District": "西大門区", "Seodaemun-gu": "西大門区",
  "Seongdong District": "城東区", "Seongdong-gu": "城東区",
  "Songpa District": "松坡区", "Songpa-gu": "松坡区",
  "Yeongdeungpo": "永登浦", "Yeongdeungpo District": "永登浦区", "Yeongdeungpo-gu": "永登浦区",
  "Yongsan District": "龍山区", "Yongsan-gu": "龍山区",
};

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
  const { lang, p } = useLang();
  const langRef = useRef(lang);
  useEffect(() => { langRef.current = lang; }, [lang]);
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const popup = useRef<mapboxgl.Popup | null>(null);

  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    const m = new mapboxgl.Map({
      container: mapContainer.current,
      style: "mapbox://styles/mapbox/streets-v12",
      center: [126.9611, 37.5192],
      zoom: 11.5,
    });
    map.current = m;
    m.addControl(new mapboxgl.NavigationControl(), "top-right");

    const geojson: GeoJSON.FeatureCollection = {
      type: "FeatureCollection",
      features: spots
        .filter((s) => s.lat && s.lng)
        .map((s) => ({
          type: "Feature",
          geometry: { type: "Point", coordinates: [s.lng, s.lat] },
          properties: {
            id: s.id,
            name: s.english_name || s.name,
            category: s.category || "",
            region: s.region || s.city,
            region_ja: REGION_JA[s.region || s.city] || s.region || s.city,
            rating: s.rating,
            image_url: s.image_url || "",
            slug: (s.english_name || s.name).toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, ""),
          },
        })),
    };

    m.on("load", () => {
      m.addSource("spots", {
        type: "geojson",
        data: geojson,
        cluster: true,
        clusterMaxZoom: 13,
        clusterRadius: 50,
      });

      // Cluster circles
      m.addLayer({
        id: "clusters",
        type: "circle",
        source: "spots",
        filter: ["has", "point_count"],
        paint: {
          "circle-color": ["step", ["get", "point_count"], "#F5A623", 10, "#e8902a", 30, "#d4791a"],
          "circle-radius": ["step", ["get", "point_count"], 20, 10, 28, 30, 36],
          "circle-stroke-width": 2,
          "circle-stroke-color": "#fff",
          "circle-opacity": 0.92,
        },
      });

      // Cluster count labels
      m.addLayer({
        id: "cluster-count",
        type: "symbol",
        source: "spots",
        filter: ["has", "point_count"],
        layout: {
          "text-field": "{point_count_abbreviated}",
          "text-size": 13,
          "text-font": ["DIN Offc Pro Medium", "Arial Unicode MS Bold"],
        },
        paint: { "text-color": "#fff" },
      });

      // Individual pins
      m.addLayer({
        id: "unclustered-point",
        type: "circle",
        source: "spots",
        filter: ["!", ["has", "point_count"]],
        paint: {
          "circle-color": "#F5A623",
          "circle-radius": 10,
          "circle-stroke-width": 2,
          "circle-stroke-color": "#fff",
          "circle-opacity": 0.95,
        },
      });

      // Zoom into cluster on click
      m.on("click", "clusters", (e) => {
        const features = m.queryRenderedFeatures(e.point, { layers: ["clusters"] });
        const clusterId = features[0].properties?.cluster_id;
        (m.getSource("spots") as mapboxgl.GeoJSONSource).getClusterExpansionZoom(clusterId, (err, zoom) => {
          if (err) return;
          const coords = (features[0].geometry as GeoJSON.Point).coordinates as [number, number];
          m.easeTo({ center: coords, zoom: zoom! });
        });
      });

      // Hover tooltip
      m.on("mouseenter", "unclustered-point", (e) => {
        m.getCanvas().style.cursor = "pointer";
        const props = e.features?.[0]?.properties;
        if (!props) return;
        const coords = (e.features![0].geometry as GeoJSON.Point).coordinates as [number, number];
        popup.current?.remove();
        const isJa = langRef.current === "ja";
        const regionLabel = isJa ? props.region_ja : props.region;
        const categoryLabel = isJa ? (CATEGORY_JA[props.category] || props.category) : props.category;
        popup.current = new mapboxgl.Popup({ offset: 12, maxWidth: "220px", closeButton: false, closeOnClick: false })
          .setLngLat(coords)
          .setHTML(`
            <div style="font-family:inherit;overflow:hidden;border-radius:10px;">
              ${props.image_url ? `<img src="${props.image_url}" style="width:100%;height:110px;object-fit:cover;display:block;" />` : ""}
              <div style="padding:8px 10px;">
                <div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#F5A623;margin-bottom:3px;">${regionLabel}</div>
                <div style="font-size:12px;font-weight:600;color:#1a1a1a;margin-bottom:2px;">${props.name}</div>
                <div style="font-size:11px;color:#888;">★ ${props.rating} · ${categoryLabel}</div>
              </div>
            </div>
          `)
          .addTo(m);
      });

      m.on("mouseleave", "unclustered-point", () => {
        m.getCanvas().style.cursor = "";
        popup.current?.remove();
      });

      // Click → navigate to spot page
      m.on("click", "unclustered-point", (e) => {
        const slug = e.features?.[0]?.properties?.slug;
        if (slug) window.location.href = p(`/spots/${slug}`);
      });

      m.on("mouseenter", "clusters", () => { m.getCanvas().style.cursor = "pointer"; });
      m.on("mouseleave", "clusters", () => { m.getCanvas().style.cursor = ""; });
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
