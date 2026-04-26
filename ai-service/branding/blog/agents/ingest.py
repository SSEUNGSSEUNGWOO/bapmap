import os
import re
import math
import json
import requests
from pathlib import Path
from unidecode import unidecode
from supabase import create_client

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
BASE_URL = "https://places.googleapis.com/v1/places"
HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": GOOGLE_API_KEY,
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
    "barbecue_restaurant": "Korean BBQ",
    "japanese_restaurant": "Japanese",
    "ramen_restaurant": "Noodles",
    "noodle_restaurant": "Noodles",
    "sushi_restaurant": "Japanese",
    "chinese_restaurant": "Chinese",
    "italian_restaurant": "Italian",
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
    "chicken_wings_restaurant": "Chicken",
    "restaurant": "Korean",
}

TARGET_CITIES = {
    # 특별시/광역시
    "Seoul", "Busan", "Incheon",
    # 경기 주요 도시
    "Suwon", "Seongnam", "Goyang",
    # 지방 관광 도시
    "Jeju", "Jeonju", "Gyeongju", "Gangneung",
}

# 허용하는 Google Places primaryType (음식점 관련만)
ALLOWED_TYPES = {
    "restaurant", "korean_restaurant", "korean_barbecue_restaurant",
    "barbecue_restaurant", "japanese_restaurant", "ramen_restaurant",
    "noodle_restaurant", "sushi_restaurant", "izakaya_restaurant",
    "chinese_restaurant", "italian_restaurant", "pizza_restaurant",
    "french_restaurant", "american_restaurant", "hamburger_restaurant",
    "fast_food_restaurant", "thai_restaurant", "vietnamese_restaurant",
    "seafood_restaurant", "cafe", "bakery", "coffee_shop", "bar",
    "wine_bar", "chicken_wings_restaurant", "meal_takeaway", "meal_delivery",
    "steak_house", "sandwich_shop", "dessert_restaurant", "ice_cream_shop",
    "brunch_restaurant", "breakfast_restaurant",
}

# 밥맵 성격에 안 맞는 체인/프랜차이즈 (소문자) — 로컬 맛집만 남긴다
CHAIN_BLOCKLIST = {
    # 글로벌 체인
    "five guys", "mcdonald", "burger king", "subway", "kfc", "pizza hut",
    "domino", "starbucks", "dunkin", "baskin robbins", "outback",
    "tgi friday", "hard rock", "shake shack", "popeyes", "wendy",
    "lotteria", "mcdonalds",
    # 한국 프랜차이즈 — 치킨
    "교촌", "kyochon", "bbq치킨", "bhc", "굽네", "네네치킨", "처갓집",
    "맥시카나", "호식이두마리", "60계치킨", "페리카나",
    # 한국 프랜차이즈 — 커피/카페
    "이디야", "빽다방", "메가커피", "컴포즈", "투썸플레이스", "탐앤탐스",
    "할리스", "커피빈", "엔제리너스", "파스쿠찌", "droptop",
    # 한국 프랜차이즈 — 베이커리
    "파리바게뜨", "뚜레주르", "뚜레쥬르",
    # 한국 프랜차이즈 — 기타 식음료
    "본죽", "한솥", "맘스터치", "노브랜드버거", "미스터피자", "피자알볼로",
    "공차", "쥬씨", "스무디킹", "놀부", "원할머니", "청년다방",
    "국대떡볶이", "죠스떡볶이", "이삭토스트", "김가네", "옛날통닭",
}

FIELDS = ",".join([
    "places.displayName", "places.formattedAddress", "places.location",
    "places.rating", "places.userRatingCount", "places.googleMapsUri",
    "places.regularOpeningHours", "places.photos", "places.primaryType",
    "places.addressComponents", "places.id", "places.priceLevel",
    "places.reservable", "places.goodForGroups", "places.reviews",
])


def _search_place(name: str, region: str = "") -> dict | None:
    query = f"{name} {region} Korea".strip()
    resp = requests.post(
        f"{BASE_URL}:searchText",
        headers={**HEADERS, "X-Goog-FieldMask": FIELDS},
        json={"textQuery": query, "languageCode": "en", "maxResultCount": 1},
    )
    places = resp.json().get("places", [])
    return places[0] if places else None


def _get_subway(lat: float, lng: float) -> str:
    resp = requests.post(
        f"{BASE_URL}:searchNearby",
        headers={**HEADERS, "X-Goog-FieldMask": "places.displayName,places.location,places.name"},
        json={
            "includedTypes": ["subway_station"],
            "maxResultCount": 1,
            "languageCode": "en",
            "locationRestriction": {
                "circle": {"center": {"latitude": lat, "longitude": lng}, "radius": 1000}
            },
        },
    )
    places = resp.json().get("places", [])
    if not places:
        return ""
    station = places[0]
    slat = station["location"]["latitude"]
    slng = station["location"]["longitude"]
    R = 6371000
    p = math.pi / 180
    a = (math.sin((slat - lat) * p / 2) ** 2 +
         math.cos(lat * p) * math.cos(slat * p) *
         math.sin((slng - lng) * p / 2) ** 2)
    dist = 2 * R * math.asin(math.sqrt(a))
    minutes = math.ceil(dist / 67)
    name = station["displayName"]["text"]
    name = re.sub(r'[\uAC00-\uD7A3]', '', name).strip()
    name = name.replace(" Station", "").strip()
    return f"{name} Station, {minutes} min walk"


# 광역시/특별시: administrative_area_level_1이 곧 도시명
_METRO = {"Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju", "Ulsan"}
_LEVEL1_CLEANUP = [
    " Metropolitan City", " Special City", " Special Autonomous City",
    " Metropolitan Autonomous City",
]


def _parse_address(components: list) -> tuple[str, str]:
    level1 = level2 = sub1 = ""
    for c in components:
        types = c.get("types", [])
        t = c["longText"]
        if "administrative_area_level_1" in types:
            level1 = t
        elif "administrative_area_level_2" in types:
            level2 = t
        elif "sublocality_level_1" in types:
            sub1 = t

    # 특별시/광역시 suffix 제거
    clean_l1 = level1
    for s in _LEVEL1_CLEANUP:
        clean_l1 = clean_l1.replace(s, "")

    if clean_l1 in _METRO:
        # 서울/부산/인천 등: level1 = 도시, sub1 = 구
        city = clean_l1
        region = re.sub(r"-gu$", " District", sub1) if sub1 else ""
    elif "Jeju" in level1:
        # 제주특별자치도
        city = "Jeju"
        region = re.sub(r"-si$", "", sub1) if sub1 else ""
    elif level2:
        # 경기도·전라도·경상도 등 도 소속: level2 = 시 (예: "Suwon-si")
        city = re.sub(r"-(si|gun|gu)$", "", level2)
        region = re.sub(r"-gu$", " District", sub1) if sub1 else ""
    else:
        city = clean_l1 or "Seoul"
        region = sub1 or ""

    return city, region


def _get_photo_url(photo_name: str) -> str:
    return f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=800&key={GOOGLE_API_KEY}"


def _is_korean(text: str) -> bool:
    return bool(re.search(r'[\uAC00-\uD7A3]', text))


def _korean_to_english(name: str) -> str:
    from anthropic import Anthropic
    res = Anthropic().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=50,
        messages=[{"role": "user", "content": (
            f"Convert this Korean restaurant name to a natural English name. "
            f"Return only the English name, nothing else: {name}"
        )}],
    )
    return res.content[0].text.strip()


def _to_slug(name: str) -> str:
    s = unidecode(name).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _already_exists(sb, name: str, english_name: str) -> bool:
    res = sb.table("spots").select("id").or_(
        f"name.ilike.%{name}%,english_name.ilike.%{english_name}%"
    ).limit(1).execute()
    return bool(res.data)


def ingest(discovered: list[dict]) -> list[str]:
    sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    new_ids = []

    for item in discovered:
        name = item["name"]
        region = item.get("region", "")
        blueribbon_url = item.get("blueribbon_url", "")

        print(f"[Ingest] 검색 중: {name}")
        place = _search_place(name, region)
        if not place:
            print(f"[Ingest] Google Places 못 찾음: {name}")
            continue

        english_name = place.get("displayName", {}).get("text", name)
        if _is_korean(english_name):
            english_name = _korean_to_english(english_name)
            print(f"[Ingest] 영문명 변환: {english_name}")

        if _already_exists(sb, name, english_name):
            print(f"[Ingest] 이미 존재: {english_name}")
            continue

        # 음식점 타입 검증
        primary_type = place.get("primaryType", "")
        if primary_type and primary_type not in ALLOWED_TYPES:
            print(f"[Ingest] 음식점 아님 ({primary_type}), 스킵: {english_name}")
            continue

        # 글로벌 체인 필터
        name_lower = english_name.lower()
        if any(chain in name_lower for chain in CHAIN_BLOCKLIST):
            print(f"[Ingest] 글로벌 체인, 스킵: {english_name}")
            continue

        lat = place["location"]["latitude"]
        lng = place["location"]["longitude"]
        city, addr_region = _parse_address(place.get("addressComponents", []))
        if city not in TARGET_CITIES:
            print(f"[Ingest] 대상 도시 아님 ({city}), 스킵: {english_name}")
            continue
        subway = _get_subway(lat, lng)

        hours_data = place.get("regularOpeningHours", {})
        hours = "\n".join(hours_data.get("weekdayDescriptions", []))

        photos = place.get("photos", [])
        image_urls = [_get_photo_url(p["name"]) for p in photos[:3] if p.get("name")]
        image_url = image_urls[0] if image_urls else ""

        raw_reviews = place.get("reviews", [])
        reviews = [
            rv["text"]["text"]
            for rv in raw_reviews
            if rv.get("text", {}).get("languageCode") == "en"
        ][:3]

        raw_type = place.get("primaryType", "")
        category = CATEGORY_MAP.get(raw_type, "Korean")

        slug = _to_slug(english_name)

        row = {
            "name": name,
            "english_name": english_name,
            "category": category,
            "city": city or "Seoul",
            "region": addr_region or region,
            "lat": lat,
            "lng": lng,
            "rating": place.get("rating", 0),
            "rating_count": place.get("userRatingCount", 0),
            "price_level": PRICE_MAP.get(place.get("priceLevel", ""), ""),
            "hours": hours,
            "subway": subway,
            "google_maps_url": place.get("googleMapsUri", ""),
            "image_url": image_url,
            "image_urls": image_urls,
            "google_reviews": reviews,
            "reservable": place.get("reservable", False),
            "good_for_groups": place.get("goodForGroups", False),
            "status": "업로드완료",
        }

        res = sb.table("spots").insert(row).execute()
        if res.data:
            new_id = res.data[0]["id"]
            new_ids.append(new_id)
            print(f"[Ingest] ✓ {english_name} (id: {new_id}) | {subway} | ★{row['rating']}")
        else:
            print(f"[Ingest] 삽입 실패: {english_name}")

    print(f"[Ingest] {len(new_ids)}개 신규 스팟 추가")
    return new_ids
