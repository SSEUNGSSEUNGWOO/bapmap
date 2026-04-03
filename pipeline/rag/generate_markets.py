"""
서울 시장 가이드 생성
실행: python -m pipeline.rag.generate_markets
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

MARKETS = [
    # 대형 음식 시장
    {
        "title": "Gwangjang Market — Seoul's Greatest Street Food",
        "area": "Gwangjang Market",
        "slug": "gwangjang-market-guide",
        "wiki": "Gwangjang Market",
        "context": "One of Korea's oldest and largest traditional markets. Famous for bindaetteok (mung bean pancakes), mayak gimbap (addictive small gimbap), yukhoe (beef tartare), and silk fabrics. The food alley is packed with ajummas cooking at open stalls. Best visited for lunch or early dinner. Jongno 5-ga station.",
    },
    {
        "title": "Noryangjin Fish Market — Fresh Seafood at Dawn",
        "area": "Noryangjin",
        "slug": "noryangjin-fish-market-guide",
        "wiki": "Noryangjin fish market",
        "context": "Seoul's largest wholesale fish market, open 24 hours. You can buy live seafood directly from vendors and have it prepared at restaurants upstairs. Famous for sashimi (hoe), live octopus, king crab, and abalone. Most lively in early morning (5-8am) for the auction. Noryangjin station.",
    },
    {
        "title": "Namdaemun Market — Seoul's Biggest Traditional Market",
        "area": "Namdaemun",
        "slug": "namdaemun-market-guide",
        "wiki": "Namdaemun Market",
        "context": "One of the largest traditional markets in Korea with over 10,000 shops. Famous for kal국수 (knife-cut noodle soup), hotteok (sweet pancakes), and imported goods. Great for cheap clothing, accessories, and wholesale goods. Open 24 hours except Sundays. Hoehyeon station.",
    },
    {
        "title": "Tongin Market — Lunchbox Cafe Experience",
        "area": "Tongin Market",
        "slug": "tongin-market-guide",
        "wiki": "Tongin Market",
        "context": "Historic market in Seochon village near Gyeongbokgung Palace. Famous for the unique 'dosirak cafe' experience — buy old Korean coins (엽전) and use them to fill a lunchbox with dishes from different stalls: tteokbokki, japchae, bindaetteok, gamja-jorim. Budget-friendly and very photogenic. Gyeongbokgung station.",
    },
    {
        "title": "Mangwon Market — Local Neighborhood Market",
        "area": "Mangwondong",
        "slug": "mangwon-market-guide",
        "wiki": "Mangwon-dong",
        "context": "A beloved local market in the Mangwon/Hapjeong area, popular with young Koreans and foodies. Known for fresh produce, street snacks, and the famous Mangwon ddukbokki. Less touristy than Gwangjang, more authentic neighborhood feel. Instagram-worthy food stalls. Mangwon station.",
    },
    {
        "title": "Gyeongdong Market — Seoul's Herb & Medicine Market",
        "area": "Gyeongdong Market",
        "slug": "gyeongdong-market-guide",
        "wiki": "Gyeongdong Market",
        "context": "Korea's largest traditional medicine and herb market near Cheongnyangni. Hundreds of stalls selling dried herbs, roots, mushrooms, and traditional Korean medicinal ingredients. Also has a large food section with haejangguk (hangover soup) restaurants. Unique sensory experience with pungent aromas. Jegi-dong station.",
    },
    {
        "title": "Majang Meat Market — Korea's Beef District",
        "area": "Majang-dong",
        "slug": "majang-meat-market-guide",
        "wiki": "Majang-dong",
        "context": "Seoul's largest wholesale meat market, specifically known for Korean beef (hanwoo). Multiple floors of butchers selling fresh cuts of beef, pork, and offal. You can buy meat at wholesale prices and have it grilled at restaurants in the same building. A must for Korean BBQ lovers. Majang station.",
    },
    {
        "title": "Garak Market — Seoul's Largest Produce Market",
        "area": "Garak Market",
        "slug": "garak-market-guide",
        "wiki": "Garak Market",
        "context": "Seoul's largest agricultural wholesale market in Songpa. Fresh fruits, vegetables, seafood, and meat at wholesale prices. Open from midnight to morning for wholesale buyers, but retail available all day. Great for buying Korean seasonal fruits and vegetables. Garak Market station.",
    },
    # 동네/특수 시장
    {
        "title": "Dongmyo Flea Market — Seoul's Vintage Treasure Hunt",
        "area": "Dongmyo",
        "slug": "dongmyo-flea-market-guide",
        "wiki": "Dongmyo",
        "context": "Seoul's most famous flea market near Dongmyo shrine. Hundreds of vendors selling vintage clothes, antiques, old electronics, military surplus, and oddities. Popular with young Koreans hunting for retro fashion. Best on weekends. Dongmyo station. Adjacent to the Euljiro vintage district.",
    },
    {
        "title": "Hwanghak-dong Flea Market — Antiques and Curiosities",
        "area": "Hwanghak-dong",
        "slug": "hwanghak-flea-market-guide",
        "wiki": "Hwanghak-dong",
        "context": "One of Seoul's oldest flea markets near Sindang station. Known for antiques, second-hand goods, traditional Korean items, and vintage collectibles. Less fashionable than Dongmyo but more authentic for actual antiques. Great for finding unique Korean souvenirs at low prices.",
    },
    {
        "title": "Bangsan Market — Baking & Packaging Supplies",
        "area": "Bangsan Market",
        "slug": "bangsan-market-guide",
        "wiki": "Eulji-ro",
        "context": "Seoul's go-to market for baking supplies, cake decorating tools, packaging materials, and party supplies. Located in the Euljiro area. Popular with home bakers and small business owners. Great for unique Korean baking molds, rice cake molds, and food packaging. Euljiro 4-ga station.",
    },
    {
        "title": "Seoul Yangnyeong Market — Traditional Medicine Street",
        "area": "Yangnyeong Market",
        "slug": "yangnyeong-market-guide",
        "wiki": "Gyeongdong Market",
        "context": "Korea's premier traditional herbal medicine street in Dongdaemun area. Over 1,000 shops selling ginseng, deer antler, dried seafood, and hundreds of medicinal herbs. The ginseng market here is particularly famous — you can buy fresh Korean ginseng (홍삼) at competitive prices. A fascinating cultural experience. Jegi-dong station.",
    },
    # 야시장/특수 문화
    {
        "title": "Hongdae Free Market — Weekend Art & Crafts",
        "area": "Hongdae",
        "slug": "hongdae-free-market-guide",
        "wiki": "Hongdae, Seoul",
        "context": "A beloved weekend outdoor market in Hongdae's main park (Hongik Children's Park). Local artists and crafters sell handmade jewelry, art prints, accessories, and vintage items. Runs Saturday afternoons (weather permitting, spring to fall). K-pop street performances nearby. Very popular with tourists and locals. Hongdae station.",
    },
    {
        "title": "DDP Night Market — Design & Street Food",
        "area": "Dongdaemun",
        "slug": "ddp-night-market-guide",
        "wiki": "Dongdaemun Design Plaza",
        "context": "Seasonal night market held at the iconic Dongdaemun Design Plaza (DDP). Food trucks, design goods, and cultural performances in front of the stunning Zaha Hadid-designed building. Runs during spring and fall. Great combination of Korean street food, local design brands, and nighttime Seoul skyline. Dongdaemun History & Culture Park station.",
    },
    {
        "title": "Cheonggyecheon Stream Market — Urban Night Walk",
        "area": "Cheonggyecheon",
        "slug": "cheonggyecheon-market-guide",
        "wiki": "Cheonggyecheon",
        "context": "Along the restored Cheonggyecheon stream, various pop-up markets and food stalls appear seasonally. The stream itself is a beautiful urban oasis in central Seoul, lit up at night. Nearby Euljiro and Jongno areas have late-night pojangmacha (street food tents) popular with office workers. Gwanghwamun or City Hall station.",
    },
    {
        "title": "Han River Convenience Store Culture",
        "area": "Han River Parks",
        "slug": "hangang-convenience-culture-guide",
        "wiki": "Han River",
        "context": "A uniquely Korean experience: buying convenience store food (GS25, CU, 7-Eleven) and eating by the Han River. Favorites include cup ramen, triangle gimbap, fried chicken delivered to the park, and Samgak Gimbap. Han River parks (Yeouido, Banpo, Ttukseom) have convenience stores steps from the water. Free lawn seating, stunning city views, especially at night. Popular year-round.",
    },
    {
        "title": "Insadong Ssamziegil — Arts & Traditional Snacks",
        "area": "Insadong",
        "slug": "insadong-ssamziegil-guide",
        "wiki": "Insadong",
        "context": "Ssamziegil is a unique spiral-shaped open-air shopping complex in the heart of Insadong. Local craft shops, galleries, and traditional Korean snack vendors fill the space. Famous for dalgona (Korean candy), traditional teas, and handmade crafts. The main Insadong street outside is lined with tteok (rice cake) shops and antique dealers. Anguk station.",
    },
]

GUIDE_PROMPT = """You are a market & food travel writer for Bapmap — a Korean food and culture guide for English-speaking tourists.

Write a guide about: **{title}**
Location: {area}, Seoul, South Korea

--- REFERENCE DATA ---
Wikipedia background:
{wiki_summary}

Market context:
{context}
--- END DATA ---

Write a guide covering:
1. **Why visit** — what makes this market special for a tourist (2-3 sentences)
2. **What to eat / buy** — specific foods, products, or experiences
3. **Best for** — foodies? bargain hunters? cultural experience? photographers?
4. **How to get there** — subway station and line
5. **Best time to visit** — time of day, days of week, seasons
6. **Budget** — typical spend
7. **Insider tip** — something most tourists miss

Tone: enthusiastic but practical. Written for a first-time visitor to Seoul who wants authentic experiences.
English only. 280-340 words."""


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
            context=item["context"],
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
    targets = [m for m in MARKETS if overwrite or m["slug"] not in existing]

    print(f"\n시장 가이드 생성: {len(targets)}개\n")

    for i, item in enumerate(targets):
        print(f"[{i+1}/{len(targets)}] {item['title']}")
        try:
            content = generate_guide(item)
            embedding = get_embedding(f"{item['title']}\n{item['area']}\n{content}")
            sources = ["Claude AI"]
            if get_wikipedia_summary(item["wiki"]):
                sources.append("Wikipedia")

            sb.table("guides").upsert({
                "title": item["title"],
                "area": item["area"],
                "slug": item["slug"],
                "content": content,
                "embedding": embedding,
                "type": "market",
                "sources": sources,
            }, on_conflict="slug").execute()
            print(f"  ✅ 저장 ({len(content)}자)")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ❌ 오류: {e}")

    print(f"\n완료! {len(targets)}개 시장 가이드 생성됨")


if __name__ == "__main__":
    import sys
    run(overwrite="--overwrite" in sys.argv)
