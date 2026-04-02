import os
import sys
import json
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client
from anthropic import Anthropic

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pipeline.enrich import search_place, get_korean_address, get_photo_url, get_subway, parse_hours, parse_address_components
from pipeline.generator import generate_post

load_dotenv()

# Streamlit Cloud secrets 우선, 없으면 .env
for key in ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "GOOGLE_PLACES_API_KEY", "ANTHROPIC_API_KEY", "WORDPRESS_URL", "WORDPRESS_USER", "WORDPRESS_APP_PASSWORD"]:
    if key in st.secrets:
        os.environ[key] = st.secrets[key]

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PRICE_MAP = {
    "PRICE_LEVEL_FREE": "$",
    "PRICE_LEVEL_INEXPENSIVE": "$",
    "PRICE_LEVEL_MODERATE": "$$",
    "PRICE_LEVEL_EXPENSIVE": "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}

st.set_page_config(page_title="Bapmap Admin", page_icon="🍚", layout="wide")
st.title("🍚 Bapmap Admin")

tab1, tab2 = st.tabs(["가게 추가", "전체 목록"])

with tab1:
    st.subheader("새 가게 추가")
    name = st.text_input("가게 이름 (한글)", placeholder="예: 멘야코노하 성수")
    address_hint = st.text_input("주소 (이름으로 못 찾을 때)", placeholder="예: 서울 성동구 왕십리로4길 10-1")

    if st.button("검색", type="primary"):
        if not name:
            st.error("가게 이름을 입력해주세요")
        else:
            with st.spinner(f"{name} 검색 중..."):
                place = search_place(name)
                if not place and address_hint:
                    st.warning("이름으로 못 찾아 주소로 재시도 중...")
                    place = search_place(address_hint)
                if not place:
                    st.error("Google Places에서 찾을 수 없습니다. 주소를 입력해보세요.")
                else:
                    st.session_state["found_place"] = place
                    st.session_state["found_name"] = name

    if "found_place" in st.session_state:
        place = st.session_state["found_place"]
        name = st.session_state["found_name"]

        lat = place["location"]["latitude"]
        lng = place["location"]["longitude"]
        city, region = parse_address_components(place.get("addressComponents", []))
        english_name = place.get("displayName", {}).get("text", "")
        english_address = place.get("formattedAddress", "")
        rating = place.get("rating", 0)
        photos = place.get("photos", [])
        image_url = get_photo_url(photos[0]["name"]) if photos else ""
        subway = get_subway(lat, lng)
        hours = parse_hours(place)
        korean_address = get_korean_address(name)
        price_level = PRICE_MAP.get(place.get("priceLevel", ""), "")
        category = place.get("primaryType", "").replace("_", " ").title()

        st.divider()
        img_col, info_col = st.columns([1, 2])
        with img_col:
            if image_url:
                st.image(image_url, width=250)
        with info_col:
            st.markdown(f"**평점:** ★{rating} ({place.get('userRatingCount', 0):,}개 리뷰)")
            st.markdown(f"**Google Maps:** {place.get('googleMapsUri', '')}")

        st.divider()
        st.markdown("##### 기본 정보 수정")
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            english_name = st.text_input("영어 이름", value=english_name, key="edit_english_name")
        with r1c2:
            city = st.text_input("도시 (city)", value=city, key="edit_city")
        with r1c3:
            region = st.text_input("지역 (region)", value=region, key="edit_region")

        CATEGORIES = [
            "Bakery", "Bar", "Buckwheat Noodles", "Burger", "Cafe", "Chinese", "Chicken",
            "Chicken Feet", "Dak Galbi", "French", "Galbi", "Gopchang", "Hangover Soup",
            "Italian", "Japanese", "Kimbap", "Korean", "Korean BBQ", "Korean Chicken Soup",
            "Korean Soup", "Lamb", "Lamb Skewers", "Makchang", "Makgeolli Bar", "Mulhoe",
            "Noodles", "Pizza", "Pork Bone Soup", "Ramen", "Raw Fish", "Seafood",
            "Soft Tofu", "Spicy Squid", "Sundae", "Sundae Soup", "Teppanyaki",
            "Thai", "Tofu", "Tonkatsu", "Tteokbokki", "Vietnamese", "Western", "Wine Bar",
        ]

        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            category_options = ["직접 입력"] + CATEGORIES
            cat_select = st.selectbox("카테고리", category_options,
                                      index=category_options.index(category) if category in category_options else 0,
                                      key="edit_category_select")
            if cat_select == "직접 입력":
                category = st.text_input("카테고리 직접 입력 (영어)", value=category, key="edit_category")
            else:
                category = cat_select
        with r2c2:
            price_level = st.text_input("가격대", value=price_level, key="edit_price_level")
        with r2c3:
            subway = st.text_input("지하철", value=subway, key="edit_subway")

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            korean_address = st.text_input("한국어 주소", value=korean_address, key="edit_address")
        with r3c2:
            english_address = st.text_input("영어 주소", value=english_address, key="edit_english_address")

        r4c1, r4c2, r4c3 = st.columns(3)
        with r4c1:
            vegetarian = st.checkbox("채식 가능", value=place.get("servesVegetarianFood", False), key="edit_veg")
        with r4c2:
            reservable = st.checkbox("예약 가능", value=place.get("reservable", False), key="edit_res")
        with r4c3:
            good_for_groups = st.checkbox("단체 가능", value=place.get("goodForGroups", False), key="edit_groups")

        st.divider()
        memo = st.text_area("메모", placeholder="직접 가본 느낌, 추천 메뉴, 팁 등 자유롭게")
        uploaded_files = st.file_uploader("내 사진 업로드 (최대 2장, 없으면 Google 사진 사용)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ 추가 확정", type="primary"):
                existing = sb.table("spots").select("id").eq("name", name).execute()
                if existing.data:
                    st.error(f"⚠️ '{name}'은 이미 등록된 가게입니다.")
                    st.stop()
                with st.spinner("저장 중..."):
                    photo_name = photos[0].get("name", "") if photos else ""
                    image_urls = [get_photo_url(p["name"]) for p in photos[:3] if p.get("name")]

                    if uploaded_files:
                        slug = english_name.lower().replace(" ", "-")
                        uploaded_urls = []
                        for i, f in enumerate(uploaded_files[:2]):
                            path = f"{slug}-upload-{i+1}.jpg"
                            sb.storage.from_("restaurant-images").upload(path, f.read(), {"content-type": "image/jpeg", "upsert": "true"})
                            pub_url = sb.storage.from_("restaurant-images").get_public_url(path)
                            uploaded_urls.append(pub_url)
                        image_urls = image_urls[:1] + uploaded_urls

                    raw_reviews = place.get("reviews", [])
                    reviews = [rv["text"]["text"] for rv in raw_reviews if rv.get("text", {}).get("languageCode") == "en"][:3]

                    data = {
                        "name": name,
                        "english_name": english_name,
                        "city": city,
                        "region": region,
                        "category": category,
                        "address": korean_address,
                        "english_address": english_address,
                        "lat": lat,
                        "lng": lng,
                        "google_maps_url": place.get("googleMapsUri", ""),
                        "rating": rating,
                        "rating_count": place.get("userRatingCount", 0),
                        "price_level": price_level,
                        "hours": hours,
                        "image_url": get_photo_url(photo_name) if photo_name else "",
                        "image_urls": image_urls,
                        "subway": subway,
                        "vegetarian": vegetarian,
                        "reservable": reservable,
                        "good_for_groups": good_for_groups,
                        "google_reviews": reviews,
                        "memo": memo,
                        "status": "메모완료" if memo.strip() else "메모필요",
                    }
                    try:
                        res = sb.table("spots").insert(data).execute()
                        if res.data:
                            del st.session_state["found_place"]
                            del st.session_state["found_name"]
                            st.success(f"✅ {name} 추가 완료!")
                            st.rerun()
                        else:
                            st.error(f"저장 실패: 응답 데이터 없음. {res}")
                    except Exception as e:
                        st.error(f"저장 중 오류 발생: {e}")
        with col_b:
            if st.button("❌ 취소"):
                del st.session_state["found_place"]
                del st.session_state["found_name"]
                st.rerun()

with tab2:
    st.subheader("전체 가게 목록")

    status_filter = st.selectbox("상태 필터", ["전체", "메모필요", "메모완료", "업로드완료"])

    res = sb.table("spots").select("id, name, english_name, city, status, memo, rating, content").order("created_at", desc=True).execute()
    restaurants = res.data

    if status_filter != "전체":
        restaurants = [r for r in restaurants if r.get("status") == status_filter]

    st.write(f"총 {len(restaurants)}개")

    for r in restaurants:
        with st.expander(f"{r['name']} ({r.get('english_name', '')}) — {r.get('status', '')} | ★{r.get('rating', '')}"):
            memo = st.text_area("메모 (내부용)", value=r.get("memo") or "", key=f"memo_{r['id']}")
            content = st.text_area("본문 (사이트 표시)", value=r.get("content") or "", height=200, key=f"content_{r['id']}")
            status = st.selectbox("상태", ["메모필요", "메모완료", "업로드완료"],
                                  index=["메모필요", "메모완료", "업로드완료"].index(r.get("status", "메모필요")),
                                  key=f"status_{r['id']}")
            col_save, col_gen = st.columns([1, 1])
            with col_save:
                if st.button("저장", key=f"save_{r['id']}"):
                    sb.table("spots").update({"memo": memo, "content": content, "status": status}).eq("id", r["id"]).execute()
                    st.success("저장됨!")
                    st.rerun()
            with col_gen:
                if st.button("✨ 글 생성 + 업로드", key=f"gen_{r['id']}", type="primary"):
                    if not memo.strip():
                        st.error("메모를 먼저 써주세요")
                    else:
                        with st.spinner("글 생성 중..."):
                            sb.table("spots").update({"memo": memo}).eq("id", r["id"]).execute()
                            full_spot = sb.table("spots").select("*").eq("id", r["id"]).execute().data[0]
                            generated = generate_post(full_spot)
                            sb.table("spots").update({"content": generated, "status": "업로드완료"}).eq("id", r["id"]).execute()
                        st.success("✅ 글 생성 완료! 업로드됨")
                        st.rerun()
