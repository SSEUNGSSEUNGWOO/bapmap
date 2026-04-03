"""
서울 랜드마크 가이드 생성 (쇼핑몰, 관광지, K-팝 명소, 대학가)
Wikipedia + Google Places 기반으로 Claude가 생성 후 임베딩 저장

실행: python -m pipeline.rag.generate_landmarks
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

LANDMARKS = [
    # 쇼핑몰
    {
        "title": "Garden Five — Seoul's Largest Lifestyle Mall",
        "area": "Munjeong-dong, Songpa",
        "slug": "garden-five",
        "wiki": "Garden Five",
        "lat": 37.4772, "lng": 127.1231,
        "context": "Garden Five is one of Seoul's largest shopping complexes located in Songpa-gu. It has five themed buildings covering electronics, furniture, fashion, and food. Very popular with locals, less touristy than Gangnam malls. Near Jangji Station on Line 8.",
    },
    {
        "title": "COEX Mall — Underground City in Gangnam",
        "area": "Samseong-dong, Gangnam",
        "slug": "coex-mall",
        "wiki": "COEX Mall",
        "lat": 37.5125, "lng": 127.0588,
        "context": "COEX Mall is a massive underground shopping complex in Gangnam. Home to SM Town COEX Artium (K-pop flagship store), Starfield Library, CGV IMAX, aquarium, and hundreds of restaurants. One of the most visited spots by tourists and locals alike.",
    },
    {
        "title": "Times Square — Yeongdeungpo's Mega Mall",
        "area": "Yeongdeungpo",
        "slug": "times-square-seoul",
        "wiki": "Times Square (Seoul)",
        "lat": 37.5173, "lng": 126.9038,
        "context": "Times Square in Yeongdeungpo is a large Western-style shopping mall with department store, CGV, E-Mart, and many restaurants. Popular with west Seoul residents. Near Yeongdeungpo Station on Lines 1 and 5.",
    },
    {
        "title": "The Hyundai Seoul — Most Instagrammable Mall in Korea",
        "area": "Yeouido",
        "slug": "the-hyundai-seoul",
        "wiki": "The Hyundai Seoul",
        "lat": 37.5257, "lng": 126.9285,
        "context": "The Hyundai Seoul opened in 2021 and quickly became the most talked-about mall in Korea. Known for its massive indoor garden atrium, natural light-filled spaces, and curated F&B lineup. The food hall in the basement is exceptional. Very popular with younger Koreans and international visitors.",
    },
    {
        "title": "Lotte World Mall & Tower — Jamsil's Landmark",
        "area": "Jamsil, Songpa",
        "slug": "lotte-world-mall",
        "wiki": "Lotte World Tower",
        "lat": 37.5126, "lng": 127.1021,
        "context": "Lotte World Mall sits at the base of Lotte World Tower (555m, Korea's tallest building). The mall has 6 floors of shopping, restaurants, and an aquarium. Lotte World Theme Park is adjacent. The observation deck 'Seoul Sky' offers panoramic views. Near Jamsil Station on Lines 2 and 8.",
    },
    {
        "title": "Starfield COEX & Gangnam Underground Shopping",
        "area": "Gangnam / Samseong",
        "slug": "starfield-coex",
        "wiki": "Starfield COEX Mall",
        "lat": 37.5125, "lng": 127.0588,
        "context": "The Gangnam underground shopping district connects COEX to Samseong Station via a long underground mall. Includes fashion, accessories, and street food stalls. The famous Starfield Library inside COEX is a must-see — a stunning multi-story library open to the public inside the mall.",
    },
    {
        "title": "IFC Seoul Mall — Yeouido Finance District Shopping",
        "area": "Yeouido",
        "slug": "ifc-seoul",
        "wiki": "IFC Seoul",
        "lat": 37.5256, "lng": 126.9248,
        "context": "IFC Seoul is an upscale mall in Yeouido's financial district. Connected to Yeouido Station. Houses CGV IMAX, luxury brands, and a premium food court. Popular with finance workers and weekend shoppers. Near The Hyundai Seoul.",
    },

    # 관광지
    {
        "title": "Gyeongbokgung Palace — Seoul's Royal Heart",
        "area": "Jongno",
        "slug": "gyeongbokgung",
        "wiki": "Gyeongbokgung",
        "lat": 37.5796, "lng": 126.9770,
        "context": "Gyeongbokgung is the main royal palace of the Joseon dynasty, built in 1395. Located in central Seoul, it's the city's most iconic landmark. The changing of the royal guard ceremony happens daily. Renting a hanbok (traditional Korean dress) gets you free entry. Adjacent to Bukchon Hanok Village and Insadong.",
    },
    {
        "title": "Namsan & N Seoul Tower — The View Everyone Wants",
        "area": "Namsan, Jung-gu",
        "slug": "namsan-n-tower",
        "wiki": "N Seoul Tower",
        "lat": 37.5512, "lng": 126.9882,
        "context": "N Seoul Tower sits atop Namsan mountain at 479m above sea level. Famous for love padlocks, panoramic city views, and night scenery. Accessible by cable car from Myeongdong or hiking trail. The surrounding Namsan park is great for walking. Featured in countless K-dramas.",
    },
    {
        "title": "Han River Parks — Seoul's Outdoor Living Room",
        "area": "Hangang, Various",
        "slug": "hangang-parks",
        "wiki": "Han River (Korea)",
        "lat": 37.5283, "lng": 126.9320,
        "context": "The Han River parks stretch across Seoul and are a core part of local life. Yeouido Hangang Park is the most popular — people gather for convenience store chicken and beer (chimaek), picnics, and cycling. Ttukseom is great for water sports. Banpo Bridge Rainbow Fountain is a must-see at night. Best experienced on weekends.",
    },
    {
        "title": "Changdeokgung Palace & Secret Garden",
        "area": "Jongno",
        "slug": "changdeokgung",
        "wiki": "Changdeokgung",
        "lat": 37.5794, "lng": 126.9910,
        "context": "Changdeokgung is a UNESCO World Heritage Site and arguably more beautiful than Gyeongbokgung. The 'Secret Garden' (Huwon) at the back requires a separate guided tour ticket — worth it for the stunning traditional landscape. Located near Anguk Station on Line 3.",
    },
    {
        "title": "Deoksugung Palace & Daehan Gate",
        "area": "Jung-gu, City Hall",
        "slug": "deoksugung",
        "wiki": "Deoksugung",
        "lat": 37.5658, "lng": 126.9753,
        "context": "Deoksugung is the only royal palace in Seoul with Western-style buildings alongside traditional Korean architecture. The walking path around the palace wall (Deoksugung Doldam-gil) is one of Seoul's most romantic walks. Right next to City Hall Station on Lines 1 and 2.",
    },
    {
        "title": "Dongdaemun Design Plaza (DDP) — Seoul's Futuristic Icon",
        "area": "Dongdaemun",
        "slug": "ddp",
        "wiki": "Dongdaemun Design Plaza",
        "lat": 37.5669, "lng": 127.0094,
        "context": "DDP is a massive curved silver building designed by Zaha Hadid, opened in 2014. Houses design exhibitions, pop-up stores, fashion events, and a night market. The surrounding Dongdaemun market area is famous for 24-hour fashion wholesale shopping and street food. Dongdaemun History & Culture Park Station on Lines 2, 4, and 5.",
    },
    {
        "title": "Bukchon Hanok Village — Traditional Seoul",
        "area": "Bukchon, Jongno",
        "slug": "bukchon-hanok",
        "wiki": "Bukchon Hanok Village",
        "lat": 37.5826, "lng": 126.9830,
        "context": "Bukchon Hanok Village is a historic area with hundreds of traditional Korean houses (hanok) dating back to the Joseon era. The narrow alleyways and rooftop views are iconic. Featured in many K-dramas. Best visited early morning to avoid crowds and be respectful of residents. Between Gyeongbokgung and Changdeokgung palaces.",
    },
    {
        "title": "Cheonggyecheon Stream — Urban Nature Walk",
        "area": "Jung-gu / Jongno",
        "slug": "cheonggyecheon",
        "wiki": "Cheonggyecheon",
        "lat": 37.5694, "lng": 126.9780,
        "context": "Cheonggyecheon is a 10.9km urban stream that runs through central Seoul. Restored in 2005, it's a popular walking path lined with art installations, waterfalls, and stepping stones. Connects Gwanghwamun area to Dongdaemun. Especially beautiful lit up at night.",
    },
    {
        "title": "Myeongdong — Seoul's Tourist & Shopping Hub",
        "area": "Myeongdong, Jung-gu",
        "slug": "myeongdong",
        "wiki": "Myeongdong",
        "lat": 37.5636, "lng": 126.9849,
        "context": "Myeongdong is Seoul's most visited tourist area. Packed with K-beauty shops (Olive Young, Innisfree, Etude), street food vendors, and international brands. The street food here — egg bread, tornado potatoes, tteokbokki — is the quintessential first-night-in-Seoul experience. Gets very crowded on weekends and evenings.",
    },
    {
        "title": "Lotte World Theme Park & Jamsil Area",
        "area": "Jamsil, Songpa",
        "slug": "lotte-world",
        "wiki": "Lotte World",
        "lat": 37.5111, "lng": 127.0980,
        "context": "Lotte World is one of the world's largest indoor theme parks. Includes an indoor park (Adventureland), outdoor Magic Island on a lake, folk museum, and aquarium. Popular with families and young couples. Adjacent to Lotte World Tower and Mall. Jamsil Station on Lines 2 and 8.",
    },

    # 쇼핑몰 추가
    {
        "title": "Shinsegae Gangnam — Korea's Largest Department Store",
        "area": "Seocho, Gangnam",
        "slug": "shinsegae-gangnam",
        "wiki": "Shinsegae Department Store",
        "lat": 37.5047, "lng": 127.0049,
        "context": "Shinsegae Gangnam is Korea's largest department store by floor space. Known for high-end dining on upper floors, luxury brands, and an extensive food hall in the basement. Popular with upscale shoppers and tourists. Near Express Bus Terminal Station on Lines 3, 7, and 9.",
    },
    {
        "title": "Shinsegae Myeongdong — Historic Department Store",
        "area": "Myeongdong, Jung-gu",
        "slug": "shinsegae-myeongdong",
        "wiki": "Shinsegae Department Store",
        "lat": 37.5598, "lng": 126.9782,
        "context": "Shinsegae's original Myeongdong store is Korea's oldest department store, opened in 1930. The main building has a classical European facade. The basement food hall is excellent. Connected to Hoehyeon Station on Line 4, right in the heart of the tourist district.",
    },
    {
        "title": "Galleria Department Store Apgujeong — Luxury Fashion Hub",
        "area": "Apgujeong, Gangnam",
        "slug": "galleria-apgujeong",
        "wiki": "Galleria Department Store",
        "lat": 37.5271, "lng": 127.0414,
        "context": "Galleria Apgujeong is Seoul's most prestigious luxury department store, home to Hermès, Chanel, Louis Vuitton and more. The WEST wing building facade is covered in disc-shaped panels that change color at night. The surrounding Apgujeong Rodeo Street is a high-end fashion and dining district popular with celebrities.",
    },
    {
        "title": "Lotte Department Store Myeongdong — Tourist Central",
        "area": "Myeongdong, Jung-gu",
        "slug": "lotte-dept-myeongdong",
        "wiki": "Lotte Department Store",
        "lat": 37.5649, "lng": 126.9820,
        "context": "Lotte Department Store's main Myeongdong branch is one of the most visited retail destinations in Seoul. Duty-free shopping on upper floors is extremely popular with international tourists. Directly connected to Euljiro 1-ga Station on Lines 2 and 3.",
    },
    {
        "title": "Hyundai Department Store Apgujeong — Fashion & Dining",
        "area": "Apgujeong, Gangnam",
        "slug": "hyundai-dept-apgujeong",
        "wiki": "Hyundai Department Store",
        "lat": 37.5274, "lng": 127.0286,
        "context": "Hyundai Department Store in Apgujeong is a classic upscale shopping destination with high-end fashion and a well-regarded food floor. The Apgujeong area around it has celebrity restaurants, plastic surgery clinics, and K-pop agency offices nearby.",
    },
    {
        "title": "iPark Mall Yongsan — Electronics & Shopping Complex",
        "area": "Yongsan",
        "slug": "ipark-mall-yongsan",
        "wiki": "Yongsan Electronics Market",
        "lat": 37.5298, "lng": 126.9646,
        "context": "iPark Mall sits above Yongsan Station and is connected to the massive Yongsan Electronics Market — once Asia's largest electronics market. The mall has a CGV multiplex, restaurants, and shopping. HYBE headquarters is a 10-minute walk away. Near Yongsan Station on Lines 1 and 4 and KTX.",
    },
    {
        "title": "Starfield Hanam — Suburban Mega Mall",
        "area": "Hanam, Gyeonggi",
        "slug": "starfield-hanam",
        "wiki": "Starfield Hanam",
        "lat": 37.5398, "lng": 127.2050,
        "context": "Starfield Hanam is one of Korea's largest shopping malls, opened in 2016. Located just outside Seoul in Hanam, it features a massive sports complex, IMAX, luxury brands, and an extensive food court. Popular day-trip destination from Seoul. Accessible by shuttle bus from Gangbyeon Station.",
    },
    {
        "title": "AK Plaza & Suwon — Day Trip Shopping",
        "area": "Suwon, Gyeonggi",
        "slug": "ak-plaza-suwon",
        "wiki": "Suwon",
        "lat": 37.2636, "lng": 127.0286,
        "context": "Suwon is an easy day trip from Seoul (30 min by subway on Line 1). AK Plaza near Suwon Station is a major shopping hub. Suwon is also famous for Hwaseong Fortress (UNESCO) and galbi (BBQ ribs) — the city's signature dish. Worth combining shopping with a fortress visit.",
    },

    # 대학가
    {
        "title": "Ewha Womans University Area — Fashion & Cafes",
        "area": "Sinchon / Ewha",
        "slug": "ewha-university",
        "wiki": "Ewha Womans University",
        "lat": 37.5629, "lng": 126.9467,
        "context": "The streets around Ewha Womans University are famous for affordable fashion, beauty, and cafes. The campus itself has a stunning glass building (ECC) worth visiting. Popular with young women and fashion-conscious shoppers. Near Sinchon Station on Line 2.",
    },
    {
        "title": "Sogang & Sinchon University District",
        "area": "Sinchon",
        "slug": "sogang-sinchon",
        "wiki": "Sogang University",
        "lat": 37.5513, "lng": 126.9411,
        "context": "The Sinchon area clusters Yonsei, Sogang, Ewha, and Hongik universities. This makes it one of Seoul's most energetic student districts — cheap eats, late-night bars, and lively street culture. The area between Sinchon Station and Hongdae is worth exploring on foot.",
    },
    {
        "title": "Korea University & Anam — Student Dining District",
        "area": "Anam, Seongbuk",
        "slug": "korea-university-anam",
        "wiki": "Korea University",
        "lat": 37.5894, "lng": 127.0320,
        "context": "Korea University's surrounding Anam-dong is packed with affordable student restaurants, pojangmacha (street food tents), and bars. Less touristy than Hongdae but authentic university culture. The KU campus itself is beautiful with traditional architecture. Near Anam Station on Line 6.",
    },
    {
        "title": "Kyung Hee University & Hoegi Area",
        "area": "Hoegi-dong, Dongdaemun",
        "slug": "kyunghee-hoegi",
        "wiki": "Kyung Hee University",
        "lat": 37.5965, "lng": 127.0537,
        "context": "Kyung Hee University has one of the most beautiful campuses in Seoul — the neo-Gothic architecture is stunning. The Hoegi-dong area nearby has a growing cafe and restaurant scene. Near Hoegi Station on Line 1.",
    },
    {
        "title": "Hanyang University & Wangsimni",
        "area": "Wangsimni, Seongdong",
        "slug": "hanyang-wangsimni",
        "wiki": "Hanyang University",
        "lat": 37.5573, "lng": 127.0454,
        "context": "Hanyang University is near Wangsimni, one of Seoul's underrated food neighborhoods. The area between Hanyang University Station and Wangsimni has affordable local restaurants and is less crowded than Hongdae or Gangnam. Good starting point for exploring Seongsu-dong nearby.",
    },
    {
        "title": "Sungshin Women's University & Dongsomun Area",
        "area": "Dongsomun, Seongbuk",
        "slug": "sungshin-dongsomun",
        "wiki": "Sungshin Women's University",
        "lat": 37.5924, "lng": 127.0163,
        "context": "The area around Sungshin Women's University and Dongsomun is a hidden gem for affordable food. Less crowded than major university areas, with a local neighborhood vibe. Near Sungshin Women's University Station on Line 4.",
    },
    {
        "title": "Dongguk University & Chungmuro Film District",
        "area": "Chungmuro, Jung-gu",
        "slug": "dongguk-chungmuro",
        "wiki": "Dongguk University",
        "lat": 37.5579, "lng": 127.0050,
        "context": "Dongguk University sits on a hill near Chungmuro, historically the center of Korea's film industry. The area has indie cinemas, film-related cafes, and affordable local restaurants popular with students and creative types. Near Dongguk University Station on Line 3.",
    },
    {
        "title": "Sungkyunkwan University & Hyehwa",
        "area": "Hyehwa, Jongno",
        "slug": "skku-hyehwa",
        "wiki": "Sungkyunkwan University",
        "lat": 37.5880, "lng": 126.9994,
        "context": "Sungkyunkwan University (SKKU) is one of Korea's oldest universities, founded in 1398. The campus borders the historic Daehangno (대학로) theater district in Hyehwa — Seoul's arts and performing arts hub. The area has small theaters, art cafes, and affordable student restaurants. Near Hyehwa Station on Line 4.",
    },
    {
        "title": "Chung-Ang University &흑석 — Han River Neighborhood",
        "area": "Heukseok-dong, Dongjak",
        "slug": "cau-heukseok",
        "wiki": "Chung-Ang University",
        "lat": 37.5045, "lng": 126.9558,
        "context": "Chung-Ang University's Seoul campus is in Heukseok-dong (흑석), near the Han River. The neighborhood has a good mix of student restaurants and local eateries. Near Heukseok Station on Line 9, which connects quickly to Yeouido and Gangnam.",
    },
    {
        "title": "Sookmyung Women's University & Samgakji",
        "area": "Cheongpa-dong, Yongsan",
        "slug": "sookmyung-samgakji",
        "wiki": "Sookmyung Women's University",
        "lat": 37.5453, "lng": 126.9644,
        "context": "Sookmyung Women's University is near Samgakji and Noksapyeong in Yongsan. The area has a local neighborhood feel with affordable restaurants and cafes. Near Sookmyung Women's University Station on Line 4, and close to the Itaewon/Haebangchon dining scene.",
    },
]


GUIDE_PROMPT = """You are a travel writer for Bapmap — a Korean food and culture guide for English-speaking tourists visiting Korea.

Write a landmark/destination guide for: **{title}**
Location: {area}, Seoul, South Korea

--- REFERENCE DATA ---
Wikipedia context:
{wiki_summary}

Additional context:
{context}

Top-rated nearby spots (Google Places):
{nearby_spots}
--- END DATA ---

Write the guide covering:
1. **What it is** — brief description, why visitors come here (2-3 sentences)
2. **What to do & see** — specific highlights, must-see spots within or nearby
3. **Food & dining nearby** — what kinds of food are available in this area (general types, not specific restaurants — Bapmap will handle specific spot recommendations)
4. **Getting there** — nearest subway station and line, approximate travel time from city center
5. **Best time to visit** — time of day, day of week, seasonal tips
6. **Practical tips** — admission fees if any, what to avoid, insider advice

Tone: helpful and specific, like advice from a well-traveled Korean local. Not overly enthusiastic.
English only. 250-320 words."""


def get_wikipedia_summary(query: str) -> str:
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get("extract", "")[:800]
    except Exception:
        pass
    return ""


def get_google_places_nearby(lat: float, lng: float) -> list[dict]:
    try:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_KEY,
            "X-Goog-FieldMask": "places.displayName,places.primaryTypeDisplayName,places.rating",
        }
        body = {
            "includedTypes": [
                "tourist_attraction", "museum", "shopping_mall",
                "park", "market", "landmark",
            ],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": 300.0,
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


def generate_guide(item: dict) -> str:
    wiki = get_wikipedia_summary(item["wiki"])
    nearby = get_google_places_nearby(item["lat"], item["lng"])
    nearby_str = "\n".join(f"- {p['name']} ({p['type']}, ★{p['rating']})" for p in nearby) if nearby else "No data"

    res = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        messages=[{"role": "user", "content": GUIDE_PROMPT.format(
            title=item["title"],
            area=item["area"],
            wiki_summary=wiki or "No Wikipedia data available",
            context=item["context"],
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
    existing = {r["slug"] for r in sb.table("rag_data").select("slug").execute().data}
    targets = [l for l in LANDMARKS if overwrite or l["slug"] not in existing]

    print(f"\n랜드마크 가이드 생성: {len(targets)}개 (전체 {len(LANDMARKS)}개)\n")

    for i, item in enumerate(targets):
        print(f"[{i+1}/{len(targets)}] {item['title']}")
        try:
            content = generate_guide(item)
            embedding = get_embedding(f"{item['title']}\n{item['area']} Seoul\n{content}")
            sources = ["Claude AI"]
            if get_wikipedia_summary(item["wiki"]):
                sources.append("Wikipedia")
            if get_google_places_nearby(item["lat"], item["lng"]):
                sources.append("Google Places")

            sb.table("rag_data").upsert({
                "title": item["title"],
                "area": item["area"],
                "slug": item["slug"],
                "content": content,
                "embedding": embedding,
                "type": "landmark",
                "sources": sources,
            }, on_conflict="slug").execute()
            print(f"  ✅ 저장 ({len(content)}자)")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ❌ 오류: {e}")

    print(f"\n완료! {len(targets)}개 랜드마크 가이드 생성됨")


if __name__ == "__main__":
    import sys
    run(overwrite="--overwrite" in sys.argv)
