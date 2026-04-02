import { createClient } from "@supabase/supabase-js";

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export type Spot = {
  id: string;
  name: string;
  english_name: string;
  city: string;
  region: string;
  category: string;
  address: string;
  english_address: string;
  lat: number;
  lng: number;
  google_maps_url: string;
  rating: number;
  rating_count: number;
  price_level: string;
  hours: string;
  image_url: string;
  image_urls: string[];
  subway: string;
  vegetarian: boolean;
  reservable: boolean;
  good_for_groups: boolean;
  memo: string;
  content: string;
  status: string;
  created_at: string;
};
