"""
서울 지역 가이드 생성
Wikipedia + Google Places 데이터 기반으로 Claude가 가이드 생성 후 임베딩 저장

실행: python -m pipeline.rag.generate_guides
옵션: --overwrite (기존 것도 재생성)
"""
import os
import time
import requests
from openai import OpenAI
from anthropic import Anthropic
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

AREAS = [
    # 홍대권
    {"title": "Hongdae Food Scene", "area": "Hongdae", "slug": "hongdae", "wiki": "Hongdae, Seoul", "lat": 37.5563, "lng": 126.9233},
    {"title": "Yeonnamdong Cafe Street", "area": "Yeonnamdong", "slug": "yeonnamdong", "wiki": "Yeonnam-dong", "lat": 37.5636, "lng": 126.9241},
    {"title": "Hapjeong Dining", "area": "Hapjeong", "slug": "hapjeong", "wiki": "Hapjeong station", "lat": 37.5495, "lng": 126.9143},
    {"title": "Mangwondong Local Eats", "area": "Mangwondong", "slug": "mangwondong", "wiki": "Mangwon-dong", "lat": 37.5553, "lng": 126.9025},
    # 이태원권
    {"title": "Itaewon International Food", "area": "Itaewon", "slug": "itaewon", "wiki": "Itaewon", "lat": 37.5340, "lng": 126.9944},
    {"title": "Gyeongridangil Hidden Restaurants", "area": "Gyeongridangil", "slug": "gyeongridangil", "wiki": "Gyeongnidan-gil", "lat": 37.5383, "lng": 127.0003},
    {"title": "Haebangchon Eats", "area": "Haebangchon", "slug": "haebangchon", "wiki": "Haebangchon", "lat": 37.5399, "lng": 126.9888},
    {"title": "Yongridangil Food Street", "area": "Yongridangil", "slug": "yongridangil", "wiki": "Yongsan-gu", "lat": 37.5326, "lng": 126.9808},
    # 성수/왕십리권
    {"title": "Seongsu Food & Cafe Scene", "area": "Seongsu", "slug": "seongsu", "wiki": "Seongsu-dong", "lat": 37.5445, "lng": 127.0558},
    {"title": "Wangsimni Eats", "area": "Wangsimni", "slug": "wangsimni", "wiki": "Wangsimni", "lat": 37.5612, "lng": 127.0370},
    # 강남권
    {"title": "Gangnam Dining Guide", "area": "Gangnam", "slug": "gangnam", "wiki": "Gangnam District", "lat": 37.4979, "lng": 127.0276},
    {"title": "Garosu-gil Restaurants", "area": "Garosu-gil", "slug": "garosu-gil", "wiki": "Garosu-gil", "lat": 37.5197, "lng": 127.0208},
    {"title": "Apgujeong & Cheongdam", "area": "Apgujeong", "slug": "apgujeong", "wiki": "Apgujeong-dong", "lat": 37.5274, "lng": 127.0286},
    {"title": "Seorae Village French Quarter", "area": "Seorae Village", "slug": "seorae", "wiki": "Seocho-gu", "lat": 37.5030, "lng": 126.9988},
    {"title": "Nonhyeon & Hakdong Food", "area": "Nonhyeon", "slug": "nonhyeon", "wiki": "Gangnam District", "lat": 37.5136, "lng": 127.0277},
    # 종로/광화문권
    {"title": "Jongno & Gwanghwamun Dining", "area": "Jongno", "slug": "jongno", "wiki": "Jongno District", "lat": 37.5700, "lng": 126.9820},
    {"title": "Insadong Traditional Food", "area": "Insadong", "slug": "insadong", "wiki": "Insadong", "lat": 37.5741, "lng": 126.9855},
    {"title": "Gwangjang Market Street Food", "area": "Gwangjang Market", "slug": "gwangjang-market", "wiki": "Gwangjang Market", "lat": 37.5699, "lng": 127.0092},
    {"title": "Bukchon & Samcheong-dong Cafes", "area": "Samcheong-dong", "slug": "samcheong", "wiki": "Samcheong-dong", "lat": 37.5820, "lng": 126.9817},
    {"title": "Seochon Village Food", "area": "Seochon", "slug": "seochon", "wiki": "Seochon", "lat": 37.5781, "lng": 126.9696},
    {"title": "Euljiro Old-School Dining", "area": "Euljiro", "slug": "euljiro", "wiki": "Euljiro", "lat": 37.5660, "lng": 126.9870},
    # 신촌/대학가
    {"title": "Sinchon University Food Street", "area": "Sinchon", "slug": "sinchon", "wiki": "Sinchon", "lat": 37.5554, "lng": 126.9366},
    {"title": "Hyehwa & Daehangno Eats", "area": "Hyehwa", "slug": "hyehwa", "wiki": "Daehangno", "lat": 37.5824, "lng": 127.0019},
    {"title": "Konkuk University Area", "area": "Konkuk", "slug": "konkuk", "wiki": "Konkuk University", "lat": 37.5409, "lng": 127.0704},
    # 잠실/송파권
    {"title": "Jamsil & Lotte World Dining", "area": "Jamsil", "slug": "jamsil", "wiki": "Jamsil", "lat": 37.5133, "lng": 127.1028},
    {"title": "Bangi-dong Meokjagolmok", "area": "Bangi-dong", "slug": "bangi", "wiki": "Songpa-gu", "lat": 37.5101, "lng": 127.1026},
    # 영등포/구로권
    {"title": "Yeongdeungpo & Times Square", "area": "Yeongdeungpo", "slug": "yeongdeungpo", "wiki": "Yeongdeungpo", "lat": 37.5155, "lng": 126.9069},
    {"title": "Daerim Chinatown Food", "area": "Daerim", "slug": "daerim", "wiki": "Daerim-dong", "lat": 37.4937, "lng": 126.8964},
    # 동대문/청량리권
    {"title": "Dongdaemun Night Food", "area": "Dongdaemun", "slug": "dongdaemun", "wiki": "Dongdaemun", "lat": 37.5715, "lng": 127.0097},
    # 노량진/여의도권
    {"title": "Noryangjin Fish Market", "area": "Noryangjin", "slug": "noryangjin", "wiki": "Noryangjin fish market", "lat": 37.5130, "lng": 126.9426},
    {"title": "Yeouido Han River & Food", "area": "Yeouido", "slug": "yeouido", "wiki": "Yeouido", "lat": 37.5219, "lng": 126.9241},
    # 마포/공덕권
    {"title": "Gongdeok & Mapo Local Food", "area": "Gongdeok", "slug": "gongdeok", "wiki": "Mapo District", "lat": 37.5441, "lng": 126.9516},
    # 강북/도봉
    {"title": "Uijeongbu Budae Jjigae Street", "area": "Uijeongbu", "slug": "uijeongbu", "wiki": "Uijeongbu", "lat": 37.7381, "lng": 127.0474},
    # 관악/동작권
    {"title": "Sillim Sundae Town", "area": "Sillim", "slug": "sillim", "wiki": "Gwanak-gu", "lat": 37.4847, "lng": 126.9291},
    {"title": "Nakseongdae & SNU Area", "area": "Nakseongdae", "slug": "nakseongdae", "wiki": "Seoul National University", "lat": 37.4786, "lng": 126.9527},
    {"title": "Sadang & Bangbae Dining", "area": "Sadang", "slug": "sadang", "wiki": "Dongjak-gu", "lat": 37.4766, "lng": 126.9816},

    # 성수/왕십리 추가
    {"title": "Seoul Forest Area Dining", "area": "Seoul Forest", "slug": "seoul-forest", "wiki": "Seoul Forest", "lat": 37.5445, "lng": 127.0374},

    # 마포 추가
    {"title": "Sangsu & Mapo Backstreets", "area": "Sangsu", "slug": "sangsu", "wiki": "Mapo District", "lat": 37.5488, "lng": 126.9202},
    {"title": "Ahyeon & Sinchon Backstreets", "area": "Ahyeon", "slug": "ahyeon", "wiki": "Mapo District", "lat": 37.5566, "lng": 126.9423},
    {"title": "Gongdeok & Mapo Local Food", "area": "Gongdeok", "slug": "gongdeok", "wiki": "Mapo District", "lat": 37.5441, "lng": 126.9516},

    # 이태원 추가
    {"title": "Hangangjin Dining", "area": "Hangangjin", "slug": "hangangjin", "wiki": "Yongsan-gu", "lat": 37.5300, "lng": 127.0044},

    # 강남 추가
    {"title": "Yeoksam & Seolleung Office Lunch", "area": "Yeoksam", "slug": "yeoksam", "wiki": "Gangnam District", "lat": 37.5008, "lng": 127.0366},

    # 종로 추가
    {"title": "Nakwon & Naksan Eats", "area": "Nakwon", "slug": "nakwon", "wiki": "Jongno District", "lat": 37.5801, "lng": 127.0049},

    # 대학가 추가
    {"title": "Anam & Korea University Area", "area": "Anam", "slug": "anam", "wiki": "Korea University", "lat": 37.5894, "lng": 127.0320},

    # 송파 추가
    {"title": "Songpa & Munjeong Eats", "area": "Songpa", "slug": "songpa", "wiki": "Songpa-gu", "lat": 37.5145, "lng": 127.1059},

    # 구로 추가
    {"title": "Guro Digital Complex Lunch", "area": "Guro", "slug": "guro", "wiki": "Guro-gu", "lat": 37.4851, "lng": 126.9014},

    # 청량리 추가
    {"title": "Cheongnyangni Market & Eats", "area": "Cheongnyangni", "slug": "cheongnyangni", "wiki": "Cheongnyangni", "lat": 37.5801, "lng": 127.0470},

    # 강북 추가
    {"title": "Suyu & Mia Neighborhood Eats", "area": "Suyu", "slug": "suyu", "wiki": "Gangbuk-gu", "lat": 37.6376, "lng": 127.0215},
]


def get_wikipedia_summary(query: str) -> str:
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("extract", "")[:800]
    except Exception:
        pass
    return ""


def get_google_places_nearby(lat: float, lng: float) -> list[dict]:
    try:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_KEY,
            "X-Goog-FieldMask": "places.displayName,places.primaryTypeDisplayName,places.rating,places.userRatingCount",
        }
        body = {
            "includedTypes": [
                "tourist_attraction", "museum", "art_gallery",
                "park", "shopping_mall", "market", "night_club",
                "cultural_center", "landmark", "performing_arts_theater",
            ],
            "maxResultCount": 10,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": 500.0,
                }
            },
        }
        res = requests.post(url, headers=headers, json=body, timeout=8)
        if res.status_code == 200:
            places = res.json().get("places", [])
            return [
                {
                    "name": p.get("displayName", {}).get("text", ""),
                    "type": p.get("primaryTypeDisplayName", {}).get("text", ""),
                    "rating": p.get("rating", ""),
                }
                for p in places if p.get("rating", 0) >= 4.0
            ]
    except Exception:
        pass
    return []


GUIDE_PROMPT = """You are a food & travel writer for Bapmap — a Korean local guide for English-speaking tourists.

Write a neighborhood food & travel guide for: **{title}**
Area: {area}, Seoul, South Korea

--- REFERENCE DATA ---
Wikipedia context:
{wiki_summary}

Top-rated nearby spots (Google Places):
{nearby_spots}
--- END DATA ---

Write the guide covering:
1. **What it's known for** — food identity + street/area vibe (3-4 sentences)
2. **Must-try foods & restaurants** — mention specific types, reference nearby spots if relevant
3. **Who it's for** — students, couples, office workers, late-night crowd, tourists, etc.
4. **Best time to visit**
5. **Getting there** — nearest subway line & station
6. **Price range** — typical spend per person
7. **Insider tip** — something most tourists miss

Tone: honest, specific, like a tip from a Korean local who lives nearby.
English only. 250-320 words."""


def generate_guide(area: dict) -> str:
    wiki = get_wikipedia_summary(area["wiki"])
    nearby = get_google_places_nearby(area["lat"], area["lng"])
    nearby_str = "\n".join(f"- {p['name']} ({p['type']}, ★{p['rating']})" for p in nearby) if nearby else "No data"

    res = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        messages=[{"role": "user", "content": GUIDE_PROMPT.format(
            title=area["title"],
            area=area["area"],
            wiki_summary=wiki or "No Wikipedia data available",
            nearby_spots=nearby_str,
        )}],
    )
    return res.content[0].text


def get_embedding(text: str) -> list[float]:
    res = openai_client.embeddings.create(
        input=[text.replace("\n", " ")],
        model="text-embedding-3-small",
    )
    return res.data[0].embedding


def run(overwrite: bool = False):
    existing = {r["slug"] for r in sb.table("guides").select("slug").execute().data}
    targets = [a for a in AREAS if overwrite or a["slug"] not in existing]

    print(f"\n생성 대상: {len(targets)}개 (전체 {len(AREAS)}개)\n")

    for i, area in enumerate(targets):
        print(f"[{i+1}/{len(targets)}] {area['title']}")
        try:
            content = generate_guide(area)
            embedding = get_embedding(f"{area['title']}\n{area['area']} Seoul\n{content}")
            sources = ["Claude AI"]
            if get_wikipedia_summary(area["wiki"]):
                sources.append("Wikipedia")
            if get_google_places_nearby(area["lat"], area["lng"]):
                sources.append("Google Places")

            sb.table("guides").upsert({
                "title": area["title"],
                "area": area["area"],
                "slug": area["slug"],
                "content": content,
                "embedding": embedding,
                "sources": sources,
            }, on_conflict="slug").execute()
            print(f"  ✅ 저장 ({len(content)}자)")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ❌ 오류: {e}")

    print(f"\n완료!")


if __name__ == "__main__":
    import sys
    run(overwrite="--overwrite" in sys.argv)
