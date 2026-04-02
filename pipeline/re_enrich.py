import os
import math
import requests
from dotenv import load_dotenv
from supabase import create_client
from enrich import search_place, get_korean_address, get_photo_url, get_subway, parse_hours, parse_address_components

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

PRICE_MAP = {
    "PRICE_LEVEL_FREE": "$",
    "PRICE_LEVEL_INEXPENSIVE": "$",
    "PRICE_LEVEL_MODERATE": "$$",
    "PRICE_LEVEL_EXPENSIVE": "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}

res = sb.table("spots").select("id, name").execute()

for r in res.data:
    place = search_place(r["name"])
    if not place:
        print(f"  못 찾음: {r['name']}")
        continue

    lat = place["location"]["latitude"]
    lng = place["location"]["longitude"]
    city, region = parse_address_components(place.get("addressComponents", []))
    hours = parse_hours(place)
    subway = get_subway(lat, lng)
    korean_address = get_korean_address(r["name"])
    photos = place.get("photos", [])
    photo_name = photos[0].get("name", "") if photos else ""
    image_urls = [get_photo_url(p["name"]) for p in photos[:3] if p.get("name")]

    raw_reviews = place.get("reviews", [])
    reviews = [
        rv["text"]["text"]
        for rv in raw_reviews
        if rv.get("text", {}).get("languageCode") == "en"
    ][:3]

    update = {
        "english_name": place.get("displayName", {}).get("text", ""),
        "english_address": place.get("formattedAddress", ""),
        "address": korean_address,
        "city": city,
        "region": region,
        "lat": lat,
        "lng": lng,
        "google_maps_url": place.get("googleMapsUri", ""),
        "rating": place.get("rating", 0),
        "rating_count": place.get("userRatingCount", 0),
        "price_level": PRICE_MAP.get(place.get("priceLevel", ""), ""),
        "hours": hours,
        "image_url": get_photo_url(photo_name) if photo_name else "",
        "image_urls": image_urls,
        "subway": subway,
        "vegetarian": place.get("servesVegetarianFood", False),
        "reservable": place.get("reservable", False),
        "good_for_groups": place.get("goodForGroups", False),
        "google_reviews": reviews,
    }

    sb.table("spots").update(update).eq("id", r["id"]).execute()
    print(f"  ✓ {r['name']} → {update['english_name']} | {city} | {region}")

print("\n완료")
