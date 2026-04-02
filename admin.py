import os
import sys
import json
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pipeline.enrich import search_place, get_korean_address, get_photo_url, get_subway, parse_hours, parse_address_components

load_dotenv()

# Streamlit Cloud secrets 우선, 없으면 .env
for key in ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "GOOGLE_PLACES_API_KEY", "ANTHROPIC_API_KEY", "WORDPRESS_URL", "WORDPRESS_USER", "WORDPRESS_APP_PASSWORD"]:
    if key in st.secrets:
        os.environ[key] = st.secrets[key]

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

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

        st.divider()
        col1, col2 = st.columns([1, 2])
        with col1:
            if image_url:
                st.image(image_url, width=250)
        with col2:
            st.markdown(f"### {english_name}")
            st.markdown(f"**주소:** {english_address}")
            st.markdown(f"**평점:** ★{rating} ({place.get('userRatingCount', 0):,}개 리뷰)")
            subway = get_subway(lat, lng)
            st.markdown(f"**지하철:** {subway}")
            st.markdown(f"**도시:** {city} / {region}")

        st.divider()
        memo = st.text_area("메모 (선택)", placeholder="직접 가본 느낌, 추천 메뉴, 팁 등 자유롭게")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ 추가 확정", type="primary"):
                with st.spinner("저장 중..."):
                    hours = parse_hours(place)
                    korean_address = get_korean_address(name)
                    photo_name = photos[0].get("name", "") if photos else ""
                    image_urls = [get_photo_url(p["name"]) for p in photos[:3] if p.get("name")]
                    raw_reviews = place.get("reviews", [])
                    reviews = [rv["text"]["text"] for rv in raw_reviews if rv.get("text", {}).get("languageCode") == "en"][:3]

                    data = {
                        "name": name,
                        "english_name": english_name,
                        "city": city,
                        "region": region,
                        "category": place.get("primaryType", "").replace("_", " ").title(),
                        "address": korean_address,
                        "english_address": english_address,
                        "lat": lat,
                        "lng": lng,
                        "google_maps_url": place.get("googleMapsUri", ""),
                        "rating": rating,
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
                        "memo": memo,
                        "status": "메모완료" if memo.strip() else "메모필요",
                    }
                    sb.table("restaurants").insert(data).execute()
                    del st.session_state["found_place"]
                    del st.session_state["found_name"]
                    st.success(f"✅ {name} 추가 완료!")
                    st.rerun()
        with col_b:
            if st.button("❌ 취소"):
                del st.session_state["found_place"]
                del st.session_state["found_name"]
                st.rerun()

with tab2:
    st.subheader("전체 가게 목록")

    status_filter = st.selectbox("상태 필터", ["전체", "메모필요", "메모완료", "업로드완료"])

    res = sb.table("restaurants").select("id, name, english_name, city, status, memo, rating").order("created_at", desc=True).execute()
    restaurants = res.data

    if status_filter != "전체":
        restaurants = [r for r in restaurants if r.get("status") == status_filter]

    st.write(f"총 {len(restaurants)}개")

    for r in restaurants:
        with st.expander(f"{r['name']} ({r.get('english_name', '')}) — {r.get('status', '')} | ★{r.get('rating', '')}"):
            memo = st.text_area("메모", value=r.get("memo") or "", key=f"memo_{r['id']}")
            status = st.selectbox("상태", ["메모필요", "메모완료", "업로드완료"],
                                  index=["메모필요", "메모완료", "업로드완료"].index(r.get("status", "메모필요")),
                                  key=f"status_{r['id']}")
            if st.button("저장", key=f"save_{r['id']}"):
                sb.table("restaurants").update({"memo": memo, "status": status}).eq("id", r["id"]).execute()
                st.success("저장됨!")
                st.rerun()
