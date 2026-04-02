import { supabase } from "@/lib/supabase";
import { notFound } from "next/navigation";

export default async function SpotPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;

  const { data: spots } = await supabase
    .from("spots")
    .select("*")
    .eq("status", "업로드완료");

  const spot = spots?.find((s) => {
    const s_slug = (s.english_name || s.name).toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
    return s_slug === slug;
  });

  if (!spot) notFound();

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      {/* Featured image */}
      {spot.image_url && (
        <div className="rounded-2xl overflow-hidden mb-8 h-72">
          <img src={spot.image_url} alt={spot.english_name} className="w-full h-full object-cover" />
        </div>
      )}

      {/* Meta */}
      <div className="text-sm text-orange-500 font-medium mb-2">{spot.region || spot.city}</div>
      <h1 className="text-3xl font-bold text-gray-900 mb-1">{spot.english_name || spot.name}</h1>
      <div className="flex gap-4 text-sm text-gray-400 mb-8">
        <span>★ {spot.rating} ({spot.rating_count?.toLocaleString()} reviews)</span>
        <span>{spot.price_level}</span>
        {spot.subway && <span>🚇 {spot.subway}</span>}
      </div>

      {/* Content */}
      {spot.content ? (
        <div className="prose prose-gray max-w-none whitespace-pre-wrap text-gray-700 leading-relaxed">
          {spot.content}
        </div>
      ) : (
        <p className="text-gray-400">Content coming soon.</p>
      )}

      {/* Google Maps */}
      {spot.google_maps_url && (
        <div className="mt-10">
          <a
            href={spot.google_maps_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-orange-500 text-white font-semibold px-5 py-2.5 rounded-full hover:bg-orange-600 transition-colors text-sm"
          >
            Open in Google Maps →
          </a>
        </div>
      )}
    </div>
  );
}
