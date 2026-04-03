"""
K-culture 가이드 생성 (K-pop / K-drama / K-film)
Wikipedia + 자체 지식 기반으로 Claude가 생성 후 임베딩 저장

실행: python -m pipeline.rag.generate_kculture
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

KCULTURE_GUIDES = [
    # K-pop 회사/성지
    {
        "title": "HYBE & BTS in Yongsan",
        "area": "Yongsan",
        "slug": "hybe-yongsan",
        "wiki": "HYBE Corporation",
        "kpop_context": "HYBE headquarters, BTS, TXT, SEVENTEEN, NewJeans, Le Sserafim. The HYBE Insight museum is open to fans. Yongsan iPark Mall nearby.",
    },
    {
        "title": "SM & JYP in Cheongdam — Kpop Agency District",
        "area": "Cheongdam",
        "slug": "cheongdam-kpop",
        "wiki": "SM Entertainment",
        "kpop_context": "SM Entertainment (EXO, aespa, NCT, SHINee, Red Velvet) and JYP Entertainment (TWICE, Stray Kids, ITZY, GOT7) are both in Cheongdam-dong. Fans often wait outside hoping to spot idols. High-end restaurants and cafes in the area.",
    },
    {
        "title": "YG Entertainment in Hapjeong",
        "area": "Hapjeong",
        "slug": "hapjeong-yg",
        "wiki": "YG Entertainment",
        "kpop_context": "YG Entertainment headquartered in Hapjeong. Home of BLACKPINK, BIGBANG, 2NE1. The area around YG is a hotspot for fans. Nearby Mangwondong and Hongdae are popular with idols off-duty.",
    },
    {
        "title": "Hongdae K-pop Street & Live Music",
        "area": "Hongdae",
        "slug": "hongdae-kpop",
        "wiki": "Hongdae, Seoul",
        "kpop_context": "Hongdae is the birthplace of Korean indie and K-pop street culture. K-pop dance covers happen regularly on the main street (especially weekends). K-pop shops, photo card cafes, and idol goods stores line the streets. Many idol trainees and artists live or hang out in this area.",
    },
    {
        "title": "Hannam-dong Celebrity Neighborhood",
        "area": "Hannam-dong",
        "slug": "hannam-celebrity",
        "wiki": "Hannam-dong",
        "kpop_context": "Hannam-dong is known as the celebrity neighborhood of Seoul. BTS members (RM, Jin, Suga, etc.) have been known to live here. BLACKPINK's Jennie and Rosé have been spotted in this area. High-end restaurants, private clubs, and luxury boutiques make it a favorite for celebrities dining out.",
    },
    {
        "title": "Gangnam K-pop Idol Spots",
        "area": "Gangnam",
        "slug": "gangnam-idol",
        "wiki": "Gangnam District",
        "kpop_context": "Gangnam is where many idols go for high-end dining, shopping at COEX, and entertainment. SM Town COEX Artium has the SM Store and regular fan events. K-pop music video locations around Gangnam include COEX Mall, Gangnam Station area.",
    },

    # K-drama 촬영지
    {
        "title": "Itaewon Class Filming Locations",
        "area": "Itaewon",
        "slug": "itaewon-class-drama",
        "wiki": "Itaewon Class",
        "kpop_context": "The hit drama Itaewon Class (이태원클라쓰, 2020) starring Park Seo-joon was filmed extensively in Itaewon. The fictional 'DanBam' bar is based on real Itaewon alley bars. The drama boosted Itaewon's popularity with international fans. Real filming spots include Itaewon main street, Gyeongridangil alleyways, and Hangang riverside.",
    },
    {
        "title": "Goblin (도깨비) Drama Spots in Seoul",
        "area": "Various",
        "slug": "goblin-drama",
        "wiki": "Goblin (TV series)",
        "kpop_context": "Goblin (도깨비, 2016) starring Gong Yoo and Lee Dong-wook is one of the most beloved K-dramas internationally. Key Seoul filming locations include Bukchon Hanok Village (북촌 한옥마을), Insadong streets, and Jongno area. The Quebec scenes were filmed in Canada but the Seoul scenes are very accessible to fans.",
    },
    {
        "title": "Crash Landing on You Spots in Seoul",
        "area": "Various",
        "slug": "cloy-drama",
        "wiki": "Crash Landing on You",
        "kpop_context": "Crash Landing on You (사랑의 불시착, 2019) starring Hyun Bin and Son Ye-jin became a massive international hit. Seoul filming locations include Namsan Seoul Tower area, Hannam-dong streets, and various upscale restaurants in Gangnam. The drama sparked huge interest in Korean culture across Asia.",
    },
    {
        "title": "My Love from the Star & Gangnam Drama Spots",
        "area": "Gangnam",
        "slug": "my-love-star-drama",
        "wiki": "My Love from the Star",
        "kpop_context": "My Love from the Star (별에서 온 그대, 2013) starring Kim Soo-hyun and Jun Ji-hyun became iconic across Asia. Many scenes were filmed in Gangnam, Cheongdam, and the Han River area. The drama sparked the Korean Wave in China and introduced many to Korean food culture — especially the fried chicken and beer combination.",
    },
    {
        "title": "Squid Game Filming Locations",
        "area": "Various",
        "slug": "squid-game",
        "wiki": "Squid Game",
        "kpop_context": "Squid Game (오징어게임, 2021) became Netflix's most-watched series ever. Most filming was done on sets, but the urban Seoul scenes were filmed in Dobong-gu and Ssangmun-dong area (the apartment complex scenes), Mapo Bridge area, and various subway stations. The show put Korean pop culture on the global map.",
    },
    {
        "title": "Descendants of the Sun & Military Drama Culture",
        "area": "Various",
        "slug": "dots-drama",
        "wiki": "Descendants of the Sun",
        "kpop_context": "Descendants of the Sun (태양의 후예, 2016) starring Song Joong-ki and Song Hye-kyo was filmed partly in Seoul and partly in Greece/Taean. The drama exploded in popularity across Asia. Seoul scenes were filmed in Mapo and Yeouido areas. The cast's favorite restaurants in Mapo became fan destinations.",
    },

    # K-pop 문화 일반
    {
        "title": "Seoul K-pop Photo Card Cafes",
        "area": "Hongdae / Sinchon",
        "slug": "photo-card-cafes",
        "wiki": "K-pop",
        "kpop_context": "K-pop photo card cafes (포토카드 카페) are a uniquely Korean phenomenon where fans celebrate their favorite idols' birthdays. These themed cafes — concentrated in Hongdae, Sinchon, and Mapo — are decorated with photos, banners, and offer free photo cards with drinks. They run for limited periods around idol birthdays. Searching '[idol name] 생일 카페' on Instagram will show current events.",
    },
    {
        "title": "SM Town COEX Artium & K-pop Shopping",
        "area": "Gangnam / COEX",
        "slug": "smtown-coex",
        "wiki": "SM Town",
        "kpop_context": "SM Town COEX Artium in Gangnam is the official SM Entertainment flagship store and cultural space. The SM Store sells official merchandise for EXO, aespa, NCT, SHINee, Red Velvet, and more. The building also hosts SM Town Theater with 4D performances. Inside COEX Mall you'll also find K-pop merchandise shops, the famous COEX Library, and Star Field bookstore.",
    },
    {
        "title": "Myeongdong K-culture & Street Food",
        "area": "Myeongdong",
        "slug": "myeongdong-kculture",
        "wiki": "Myeongdong",
        "kpop_context": "Myeongdong is Seoul's most visited tourist district and a K-culture hub. K-pop merchandise stores, K-beauty shops (Innisfree, Etude, Olive Young), and street food stalls line every block. Many K-pop music videos have been filmed here. The area attracts international fans looking for the 'Seoul experience' — it's touristy but genuinely buzzing with energy.",
    },
    {
        "title": "Bukchon Hanok Village — Drama & Film Hotspot",
        "area": "Bukchon",
        "slug": "bukchon-drama",
        "wiki": "Bukchon Hanok Village",
        "kpop_context": "Bukchon Hanok Village is one of Seoul's most filmed locations. Featured in Goblin, My Love from the Star, and countless K-pop music videos. The traditional Korean houses (hanok) against the Seoul cityscape create an iconic visual. Many cafes in the area are popular with tourists and idols alike. Arrive early morning to avoid crowds.",
    },
    {
        "title": "NewJeans & Aespa Generation — Seongsu Cool Factor",
        "area": "Seongsu",
        "slug": "seongsu-gen-z-kpop",
        "wiki": "Seongsu-dong",
        "kpop_context": "Seongsu-dong has become the go-to neighborhood for 4th generation K-pop acts and their fans. NewJeans, aespa, IVE, and (G)I-DLE have all shot content and attended events in Seongsu. The area's industrial-chic aesthetic makes it perfect for music video shoots. Pop-up stores from SM, HYBE, and independent labels regularly appear here. The neighborhood represents the new face of Korean cool.",
    },
]

GUIDE_PROMPT = """You are a K-culture travel writer for Bapmap — a Korean food and culture guide for English-speaking tourists.

Write a K-culture guide about: **{title}**
Location context: {area}, Seoul (or nearby)

--- REFERENCE DATA ---
Wikipedia background:
{wiki_summary}

K-pop/K-drama context:
{kpop_context}
--- END DATA ---

Write a guide covering:
1. **Why it matters** — why fans and tourists care about this place/topic (2-3 sentences)
2. **What you'll find here** — specific things to see, do, experience
3. **Best for** — BTS fans? drama fans? general K-culture tourists?
4. **How to get there** — subway station and line
5. **Best time to visit** — time of day, days of week, seasonal events
6. **Fan tips** — practical advice only a fan or local would know
7. **Nearby Bapmap spots** — mention that great food spots are nearby (don't name specific ones, Bapmap will recommend)

Tone: enthusiastic but honest. Written for someone who loves K-pop/K-drama and is visiting Seoul for the first time.
English only. 280-350 words."""


def get_wikipedia_summary(query: str) -> str:
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get("extract", "")[:800]
    except Exception:
        pass
    return ""


def generate_guide(item: dict) -> str:
    wiki = get_wikipedia_summary(item["wiki"])
    res = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": GUIDE_PROMPT.format(
            title=item["title"],
            area=item["area"],
            wiki_summary=wiki or "No Wikipedia data",
            kpop_context=item["kpop_context"],
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
    targets = [g for g in KCULTURE_GUIDES if overwrite or g["slug"] not in existing]

    print(f"\nK-culture 가이드 생성: {len(targets)}개\n")

    for i, item in enumerate(targets):
        print(f"[{i+1}/{len(targets)}] {item['title']}")
        try:
            content = generate_guide(item)
            embedding = get_embedding(f"{item['title']}\n{item['area']}\n{content}")
            sb.table("guides").upsert({
                "title": item["title"],
                "area": item["area"],
                "slug": item["slug"],
                "content": content,
                "embedding": embedding,
                "type": "kculture",
            }, on_conflict="slug").execute()
            print(f"  ✅ 저장 ({len(content)}자)")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ❌ 오류: {e}")

    print(f"\n완료! {len(targets)}개 K-culture 가이드 생성됨")


if __name__ == "__main__":
    import sys
    run(overwrite="--overwrite" in sys.argv)
