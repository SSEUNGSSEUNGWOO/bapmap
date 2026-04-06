import os
import re
import json
import math
import requests
from pathlib import Path
from urllib.parse import unquote_plus
from unidecode import unidecode
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
BASE_URL = "https://places.googleapis.com/v1/places"
DATA_FILE = Path(__file__).parent.parent / "restaurants.json"

HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
}


PRICE_MAP = {
    "PRICE_LEVEL_FREE": "$",
    "PRICE_LEVEL_INEXPENSIVE": "$",
    "PRICE_LEVEL_MODERATE": "$$",
    "PRICE_LEVEL_EXPENSIVE": "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}

CATEGORY_MAP = {
    "korean_restaurant": "Korean",
    "korean_barbecue_restaurant": "Korean BBQ",
    "japanese_restaurant": "Japanese",
    "ramen_restaurant": "Noodles",
    "sushi_restaurant": "Japanese",
    "chinese_restaurant": "Chinese",
    "italian_restaurant": "Italian",
    "pizza_restaurant": "Italian",
    "french_restaurant": "Western",
    "american_restaurant": "Western",
    "hamburger_restaurant": "Western",
    "thai_restaurant": "Asian",
    "vietnamese_restaurant": "Asian",
    "seafood_restaurant": "Seafood",
    "cafe": "Bakery & Cafe",
    "bakery": "Bakery & Cafe",
    "coffee_shop": "Bakery & Cafe",
    "bar": "Bar",
    "wine_bar": "Bar",
    "restaurant": "Korean",
    "meal_takeaway": "Korean",
    "meal_delivery": "Korean",
    "fast_food_restaurant": "Western",
}


def parse_maps_url(url: str) -> tuple[str | None, float | None, float | None]:
    """Google Maps URL에서 가게 이름, 위도, 경도 추출."""
    name_match = re.search(r'/maps/place/([^/]+)/', url)
    name = clean_name(unquote_plus(name_match.group(1))) if name_match else None

    lat_match = re.search(r'!3d(-?\d+\.\d+)', url)
    lng_match = re.search(r'!4d(-?\d+\.\d+)', url)
    lat = float(lat_match.group(1)) if lat_match else None
    lng = float(lng_match.group(1)) if lng_match else None

    return name, lat, lng


def search_place_by_url(maps_url: str) -> dict | None:
    """Google Maps URL로 정확한 장소 조회 (좌표 기반 location bias 사용)."""
    name, lat, lng = parse_maps_url(maps_url)
    if not lat or not lng:
        return None

    fields = ",".join([
        "places.displayName",
        "places.formattedAddress",
        "places.location",
        "places.rating",
        "places.userRatingCount",
        "places.googleMapsUri",
        "places.regularOpeningHours",
        "places.photos",
        "places.primaryType",
        "places.addressComponents",
        "places.id",
        "places.priceLevel",
        "places.servesVegetarianFood",
        "places.reservable",
        "places.goodForGroups",
        "places.reviews",
    ])
    query = name or "restaurant"
    resp = requests.post(
        f"{BASE_URL}:searchText",
        headers={**HEADERS, "X-Goog-FieldMask": fields},
        json={
            "textQuery": query,
            "languageCode": "en",
            "maxResultCount": 1,
            "locationBias": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": 100.0,
                }
            },
        },
    )
    places = resp.json().get("places", [])
    return places[0] if places else None


def search_place(name: str) -> dict | None:
    fields = ",".join([
        "places.displayName",
        "places.formattedAddress",
        "places.location",
        "places.rating",
        "places.userRatingCount",
        "places.googleMapsUri",
        "places.regularOpeningHours",
        "places.photos",
        "places.primaryType",
        "places.addressComponents",
        "places.id",
        "places.priceLevel",
        "places.servesVegetarianFood",
        "places.reservable",
        "places.goodForGroups",
        "places.reviews",
    ])
    for query in [name, name.split()[0]]:
        resp = requests.post(
            f"{BASE_URL}:searchText",
            headers={**HEADERS, "X-Goog-FieldMask": fields},
            json={"textQuery": f"{query} 한국", "languageCode": "en", "maxResultCount": 1},
        )
        places = resp.json().get("places", [])
        if places:
            return places[0]
    return None


def get_korean_address(name: str) -> str:
    resp = requests.post(
        f"{BASE_URL}:searchText",
        headers={**HEADERS, "X-Goog-FieldMask": "places.formattedAddress"},
        json={"textQuery": f"{name} 한국", "languageCode": "ko", "maxResultCount": 1},
    )
    places = resp.json().get("places", [])
    return places[0].get("formattedAddress", "") if places else ""


def clean_name(name: str) -> str:
    """이름에서 + 제거, 앞뒤 공백 정리."""
    return name.replace("+", " ").strip() if name else name


def to_english_name(name: str) -> str:
    """한글이 포함된 이름을 발음 기반 로마자로 변환. 이미 영어면 그대로."""
    name = clean_name(name)
    if not any('\uAC00' <= c <= '\uD7A3' for c in name):
        return name
    return unidecode(name).title()


def clean_english(s: str) -> str:
    s = re.sub(r'[\uac00-\ud7a3]+', '', s)
    s = re.sub(r',\s*,', ',', s)
    s = re.sub(r'\s{2,}', ' ', s)
    return re.sub(r'(,\s*)+$', '', s).strip()


def get_photo_url(photo_name: str) -> str:
    return f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=800&key={API_KEY}"


def get_subway(lat: float, lng: float) -> str:
    resp = requests.post(
        f"{BASE_URL}:searchNearby",
        headers={**HEADERS, "X-Goog-FieldMask": "places.displayName,places.location"},
        json={
            "includedTypes": ["subway_station"],
            "maxResultCount": 1,
            "languageCode": "en",
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": 1000,
                }
            },
        },
    )
    places = resp.json().get("places", [])
    if not places:
        return ""

    station = places[0]
    slat = station["location"]["latitude"]
    slng = station["location"]["longitude"]
    dist = haversine(lat, lng, slat, slng)
    minutes = math.ceil(dist / 67)
    name = station["displayName"]["text"].replace(" Station", "").strip()
    return f"{name} Station, {minutes} min walk"


def haversine(lat1, lng1, lat2, lng2) -> float:
    R = 6371000
    p = math.pi / 180
    a = (math.sin((lat2 - lat1) * p / 2) ** 2 +
         math.cos(lat1 * p) * math.cos(lat2 * p) *
         math.sin((lng2 - lng1) * p / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def parse_hours(place: dict) -> str:
    hours_data = place.get("regularOpeningHours", {})
    descriptions = hours_data.get("weekdayDescriptions", [])
    return "\n".join(descriptions)


def normalize_region(region: str) -> str:
    if not region:
        return region
    region = re.sub(r"-gu$", " District", region)
    if region == "Yeongdeungpo":
        region = "Yeongdeungpo District"
    return region


def parse_address_components(components: list) -> tuple[str, str]:
    city, region = "", ""
    for c in components:
        types = c.get("types", [])
        if "administrative_area_level_1" in types:
            city = c["longText"].replace(" Metropolitan City", "").replace(" Special City", "")
        if "sublocality_level_1" in types:
            region = normalize_region(c["longText"])
    return city, region


def enrich():
    restaurants = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    updated = 0

    for r in restaurants:
        if r.get("google_maps_url") and "google_reviews" in r and r.get("image_urls"):
            continue

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

        # 리뷰 텍스트만 추출 (영어 리뷰 우선)
        raw_reviews = place.get("reviews", [])
        reviews = [
            rv["text"]["text"]
            for rv in raw_reviews
            if rv.get("text", {}).get("languageCode") == "en"
        ][:3]

        r["english_name"] = place.get("displayName", {}).get("text", "")
        r["english_address"] = clean_english(place.get("formattedAddress", ""))
        r["address"] = r.get("address") or korean_address
        r["city"] = city or r.get("city", "")
        r["region"] = region or r.get("region", "")
        raw_type = place.get("primaryType", "")
        r["category"] = r.get("category") or CATEGORY_MAP.get(raw_type, raw_type.replace("_", " ").title())
        r["lat"] = lat
        r["lng"] = lng
        r["google_maps_url"] = place.get("googleMapsUri", "")
        r["rating"] = place.get("rating", 0)
        r["rating_count"] = place.get("userRatingCount", 0)
        r["price_level"] = PRICE_MAP.get(place.get("priceLevel", ""), "")
        r["hours"] = hours
        r["image_url"] = get_photo_url(photo_name) if photo_name else r.get("image_url", "")
        r["image_urls"] = image_urls if image_urls else r.get("image_urls", [])
        r["subway"] = subway
        r["vegetarian"] = place.get("servesVegetarianFood", False)
        r["reservable"] = place.get("reservable", False)
        r["good_for_groups"] = place.get("goodForGroups", False)
        r["google_reviews"] = reviews

        r.pop("kakao_url", None)

        updated += 1
        print(f"  ✓ {r['name']} ({r['english_name']}) | {r['subway']} | ★{r['rating']}")

    DATA_FILE.write_text(json.dumps(restaurants, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료: {updated}개 업데이트")


if __name__ == "__main__":
    enrich()
