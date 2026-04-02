import Link from "next/link";
import { supabase } from "@/lib/supabase";
import type { Spot } from "@/lib/supabase";

export default async function SpotsPage() {
  const { data: spots } = await supabase
    .from("spots")
    .select("id, name, english_name, city, region, image_url, rating, category, price_level, subway")
    .eq("status", "업로드완료")
    .order("created_at", { ascending: false });

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">All Spots</h1>
      <p className="text-gray-400 mb-10">Every place on here is somewhere we've actually been.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {spots?.map((spot: Spot) => {
          const slug = (spot.english_name || spot.name).toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
          return (
            <Link key={spot.id} href={`/spots/${slug}`} className="group bg-white rounded-2xl overflow-hidden border border-gray-100 hover:shadow-md transition-all">
              {spot.image_url && (
                <div className="h-48 overflow-hidden">
                  <img src={spot.image_url} alt={spot.english_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                </div>
              )}
              <div className="p-4">
                <div className="text-xs text-orange-500 font-medium mb-1">{spot.region || spot.city}</div>
                <div className="font-semibold text-gray-900">{spot.english_name || spot.name}</div>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-sm text-gray-400">★ {spot.rating}</span>
                  <span className="text-sm text-gray-400">{spot.price_level}</span>
                </div>
                {spot.subway && <div className="text-xs text-gray-300 mt-1">🚇 {spot.subway}</div>}
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
