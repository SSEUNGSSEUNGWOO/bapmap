import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# english_name 수동 매핑 (Google에 영어 이름 없는 것들)
ENGLISH_NAME_MAP = {
    "곱창의전설노량진점": "Gopchang Uijeonseol Noryangjin",
    "잠실모소리": "Jamsil Mosori",
    "마피아피자": "Mafia Pizza",
    "철판남&심야식당": "Cheolpannam",
    "부타이 제2막": "Butai Act 2",
    "더러스틱 러스틱파이": "The Rustic",
    "라이비 케이크아웃": "Laiby Cakeout",
    "픽베이크 PICKBAKE": "Pickbake",
    "피킹플레져": "Peking Pleasure",
    "프렛팃 롯데월드몰점": "Prettit Lotte World Mall",
    "서천한우곱창": "Seocheon Hanu Gopchang",
    "가야갈매기": "Gaya Galmegi",
    "봄내제빵소": "Bomnae Bakery",
    "자유빵집": "Jayu Bread",
    "시민제과": "Simin Bakery",
    "소소식당": "Soso Sikdang",
    "뽈살집": "Ppolsaljib",
    "돈사촌 본점": "Donsachon",
    "떡하니문어떡볶이": "Tteokani Tteokbokki",
    "자미더홍 jami the hong": "Jami The Hong",
    "몽고양다리": "Monggo Yangdari",
    "미가쭈꾸미": "Miga Jukkumi",
    "오시드래요": "Osideuraeyo",
    "강릉김밥": "Gangneung Gimbap",
    "키친온유": "Kitchen On You",
    "현대메밀": "Hyundae Memil",
    "낭만국시": "Nangman Guksi",
    "황가네 감자옹심이": "Hwanggane Gamja Ongsimi",
    "썸머키친": "Summer Kitchen",
    "성북동왕돈까스": "Seongbukdong Wangdonkkaseu",
    "용두동 쭈박사": "Jubbaksa",
    "이모네중앙닭발": "Imone Dakbal",
    "행궁동 비원": "Haenggungdong Biwon",
    "석사왕막걸리": "Seoksa Makgeolli",
    "퐝할매떡볶이": "Pwaeng Halme Tteokbokki",
    "강대곱창타운": "Gangdae Gopchang Town",
    "화천 두부집": "Hwacheon Tofu",
    "대양부양꼬치": "Daeyang Yangkkochi",
    "이모네불막창": "Imone Bulmakchang",
    "김서방닭발": "Kim Seobang Dakbal",
    "브래드밀레": "Breadmille",
    "뮤땅": "Mutin",
    "골목순두부": "Golmok Sundubu",
}

def clean_city(city: str) -> str:
    return (city
        .replace("-do", "")
        .replace(" Special City", "")
        .replace(" Metropolitan City", "")
        .replace("특별자치도", "")
        .strip())

def clean_region(region: str) -> str:
    return (region
        .replace("-gu", "")
        .replace(" District", "")
        .replace("특별자치도", "")
        .replace("구", "")
        .strip())

res = sb.table("spots").select("id, name, english_name, city, region").execute()

for r in res.data:
    updates = {}

    # english_name 정리
    eng = r.get("english_name", "")
    if eng and any('\uac00' <= c <= '\ud7a3' for c in eng):  # 한글 포함
        updates["english_name"] = ENGLISH_NAME_MAP.get(eng, eng)

    # city 정리
    city = r.get("city", "")
    cleaned_city = clean_city(city)
    if cleaned_city != city:
        updates["city"] = cleaned_city

    # region 정리
    region = r.get("region", "")
    cleaned_region = clean_region(region)
    if cleaned_region != region:
        updates["region"] = cleaned_region

    if updates:
        sb.table("spots").update(updates).eq("id", r["id"]).execute()
        print(f"✓ {r['name']} → {updates}")

print("\n완료")
