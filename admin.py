import os
import sys
import json
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client
from anthropic import Anthropic

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pipeline.enrich import search_place, search_place_by_url, parse_maps_url, to_english_name, get_korean_address, get_photo_url, get_subway, parse_hours, parse_address_components
from pipeline.generator import generate_post, generate_metadata
from pipeline.rag.embed import embed_spot

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

CATEGORY_MAP = {
    "korean_restaurant": "Korean",
    "korean_barbecue_restaurant": "Korean BBQ",
    "barbecue_restaurant": "Korean BBQ",
    "steak_house": "Korean BBQ",
    "japanese_restaurant": "Japanese",
    "ramen_restaurant": "Noodles",
    "noodle_restaurant": "Noodles",
    "sushi_restaurant": "Japanese",
    "izakaya_restaurant": "Japanese",
    "chinese_restaurant": "Chinese",
    "italian_restaurant": "Italian",
    "pizza_restaurant": "Italian",
    "french_restaurant": "Western",
    "american_restaurant": "Western",
    "hamburger_restaurant": "Western",
    "fast_food_restaurant": "Western",
    "thai_restaurant": "Asian",
    "vietnamese_restaurant": "Asian",
    "seafood_restaurant": "Seafood",
    "cafe": "Bakery & Cafe",
    "coffee_shop": "Bakery & Cafe",
    "bakery": "Bakery & Cafe",
    "bar": "Bar",
    "wine_bar": "Bar",
    "chicken_wings_restaurant": "Chicken",
    "restaurant": "Korean",
    "meal_takeaway": "Korean",
}

st.set_page_config(page_title="Bapmap Admin", page_icon="🍚", layout="wide")
st.title("🍚 Bapmap Admin")

tab1, tab2, tab3, tab4 = st.tabs(["가게 추가", "전체 목록", "Guides", "Messages"])

with tab1:
    st.subheader("새 가게 추가")
    maps_url = st.text_input("Google Maps URL", placeholder="https://www.google.co.kr/maps/place/...")
    parsed_name, _, _ = parse_maps_url(maps_url) if maps_url else (None, None, None)
    name = st.text_input("가게 이름 (한글)", value=parsed_name or "", placeholder="예: 멘야코노하 성수")

    if st.button("검색", type="primary"):
        if not maps_url:
            st.error("Google Maps URL을 입력해주세요")
        elif not name:
            st.error("가게 이름을 입력해주세요")
        else:
            existing = sb.table("spots").select("id, status").eq("name", name).execute()
            if existing.data:
                st.warning(f"⚠️ '{name}'은 이미 등록된 가게입니다. (상태: {existing.data[0].get('status', '')})")
                st.stop()
            with st.spinner(f"{name} 검색 중..."):
                place = search_place_by_url(maps_url)
                if not place:
                    st.error("Google Places에서 찾을 수 없습니다. URL을 확인해주세요.")
                else:
                    st.session_state["found_place"] = place
                    st.session_state["found_name"] = name

    if "found_place" in st.session_state:
        place = st.session_state["found_place"]
        name = st.session_state["found_name"]

        lat = place["location"]["latitude"]
        lng = place["location"]["longitude"]
        city, region = parse_address_components(place.get("addressComponents", []))
        english_name = to_english_name(place.get("displayName", {}).get("text", "") or name)
        english_address = place.get("formattedAddress", "")
        rating = place.get("rating", 0)
        photos = place.get("photos", [])
        image_url = get_photo_url(photos[0]["name"]) if photos else ""
        subway = get_subway(lat, lng)
        hours = parse_hours(place)
        korean_address = get_korean_address(name)
        price_level = PRICE_MAP.get(place.get("priceLevel", ""), "")
        primary_type = place.get("primaryType", "")
        category = CATEGORY_MAP.get(primary_type, primary_type.replace("_", " ").title())

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
            "Asian", "Bakery & Cafe", "Bar", "Chinese", "Chicken",
            "Gopchang", "Italian", "Japanese", "Korean", "Korean BBQ",
            "Korean Soup", "Noodles", "Seafood", "Street Food",
            "Tteokbokki", "Western",
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

        spice_level = st.select_slider(
            "매운맛 (Spice Level)",
            options=[0, 1, 2, 3],
            value=0,
            format_func=lambda x: ["없음", "🌶️ mild", "🌶️🌶️ medium", "🌶️🌶️🌶️ hot"][x],
            key="edit_spice"
        )

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
                        "spice_level": spice_level if spice_level > 0 else None,
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

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        status_filter = st.selectbox("상태 필터", ["전체", "메모필요", "메모완료", "업로드완료"])

    res = sb.table("spots").select("id, name, english_name, city, region, subway, category, status, memo, rating, content").order("created_at", desc=True).execute()
    all_spots = res.data

    cities = ["전체"] + sorted(set(r.get("city") or "기타" for r in all_spots))
    with col_f2:
        city_filter = st.selectbox("도시 필터", cities)

    restaurants = all_spots
    if status_filter != "전체":
        restaurants = [r for r in restaurants if r.get("status") == status_filter]
    if city_filter != "전체":
        restaurants = [r for r in restaurants if r.get("city") == city_filter]

    memo_done = [r for r in res.data if r.get("status") == "메모완료" and r.get("memo", "").strip()]
    if memo_done:
        st.info(f"메모완료 {len(memo_done)}개 — 한 번에 글 생성 가능")
        if st.button(f"🚀 메모완료 전체 글 생성 + 업로드 ({len(memo_done)}개)", type="primary"):
            progress = st.progress(0)
            for i, r in enumerate(memo_done):
                name = r.get("english_name") or r["name"]
                with st.spinner(f"{name} 생성 중... ({i+1}/{len(memo_done)})"):
                    full_spot = sb.table("spots").select("*").eq("id", r["id"]).execute().data[0]
                    generated = generate_post(full_spot)
                    meta = generate_metadata(full_spot)
                    update = {"content": generated, "status": "업로드완료", "what_to_order": meta.get("what_to_order") or [], "good_for": meta.get("good_for") or []}
                    try:
                        spice = meta.get("spice_level")
                        if spice is not None:
                            update["spice_level"] = int(spice)
                    except (TypeError, ValueError):
                        pass
                    sb.table("spots").update(update).eq("id", r["id"]).execute()
                    full_spot["content"] = generated
                    try:
                        embed_spot(full_spot)
                    except Exception as e:
                        st.warning(f"임베딩 실패 ({name}): {e}")
                progress.progress((i + 1) / len(memo_done))
            st.success(f"✅ {len(memo_done)}개 완료!")
            st.rerun()

    st.write(f"총 {len(restaurants)}개")

    for r in restaurants:
        location = r.get("region") or r.get("city") or ""
        subway = r.get("subway") or ""
        category = r.get("category") or ""
        with st.expander(f"{r['name']} ({r.get('english_name', '')}) — {r.get('status', '')} | ★{r.get('rating', '')} | {location} {('· 🚇' + subway) if subway else ''} {('· ' + category) if category else ''}"):
            # 위치 정보 수정
            loc_col1, loc_col2, loc_col3 = st.columns(3)
            with loc_col1:
                new_region = st.text_input("지역 (region)", value=r.get("region") or "", key=f"region_{r['id']}")
            with loc_col2:
                new_subway = st.text_input("지하철역 (subway)", value=r.get("subway") or "", key=f"subway_{r['id']}")
            with loc_col3:
                _all_cats = ["Asian", "Bakery & Cafe", "Bar", "Chinese", "Chicken",
                             "Gopchang", "Italian", "Japanese", "Korean", "Korean BBQ",
                             "Korean Soup", "Noodles", "Seafood", "Street Food",
                             "Tteokbokki", "Western"]
                _cur = r.get("category") or ""
                _idx = _all_cats.index(_cur) if _cur in _all_cats else 0
                new_category = st.selectbox("카테고리", _all_cats, index=_idx, key=f"category_{r['id']}")

            new_spice = st.select_slider(
                "매운맛",
                options=[0, 1, 2, 3],
                value=r.get("spice_level") or 0,
                format_func=lambda x: ["없음", "🌶️", "🌶️🌶️", "🌶️🌶️🌶️"][x],
                key=f"spice_{r['id']}"
            )

            memo = st.text_area("메모 (내부용)", value=r.get("memo") or "", key=f"memo_{r['id']}")
            content = st.text_area("본문 (사이트 표시)", value=r.get("content") or "", height=200, key=f"content_{r['id']}")
            col_save, col_gen = st.columns([1, 1])
            with col_save:
                if st.button("저장", key=f"save_{r['id']}"):
                    auto_status = "업로드완료" if content.strip() else ("메모완료" if memo.strip() else "메모필요")
                    sb.table("spots").update({"memo": memo, "content": content, "status": auto_status, "region": new_region, "subway": new_subway, "category": new_category, "spice_level": new_spice if new_spice > 0 else None}).eq("id", r["id"]).execute()
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
                            meta = generate_metadata(full_spot)
                            update = {"content": generated, "status": "업로드완료", "what_to_order": meta.get("what_to_order") or [], "good_for": meta.get("good_for") or []}
                            try:
                                spice = meta.get("spice_level")
                                if spice is not None:
                                    update["spice_level"] = int(spice)
                            except (TypeError, ValueError):
                                pass
                            sb.table("spots").update(update).eq("id", r["id"]).execute()
                            full_spot["content"] = generated
                            try:
                                embed_spot(full_spot)
                            except Exception as e:
                                st.warning(f"임베딩 실패: {e}")
                        st.success("✅ 글 생성 완료! 업로드됨")
                        st.rerun()

# ── TAB 3: GUIDES ──────────────────────────────────────────
with tab3:
    st.subheader("Guides 관리")

    guides_res = sb.table("guides").select("*").order("created_at", desc=True).execute()
    guides_data = guides_res.data or []

    # 새 가이드 작성
    with st.expander("➕ 새 가이드 작성", expanded=len(guides_data) == 0):
        g_title = st.text_input("제목", key="g_title")
        g_slug = st.text_input("Slug (URL)", key="g_slug", help="예: late-night-seoul")
        g_subtitle = st.text_area("부제 (카드에 표시)", key="g_subtitle", height=80)
        g_cover = st.text_input("커버 이미지 URL", key="g_cover")
        g_tag = st.text_input("카테고리 태그", key="g_tag", help="예: Late Night, Budget, Solo")
        g_intro = st.text_area("인트로 문장 (이탤릭으로 표시)", key="g_intro", height=100)
        g_body = st.text_area("본문 (마크다운)", key="g_body", height=300, help="## 소제목, **굵게**, 일반 텍스트 등 마크다운 사용 가능")
        g_spots = st.text_area(
            "스팟 english_name 목록 (한 줄에 하나)",
            key="g_spots",
            height=150,
            help="예:\nPark Makrye Cheongjin-dong Haejangguk\nDaesung Jib"
        )
        g_status = st.selectbox("상태", ["draft", "published"], key="g_status")

        if st.button("저장", key="save_guide"):
            if not g_title or not g_slug:
                st.error("제목과 Slug는 필수")
            else:
                spot_slugs = [s.strip() for s in g_spots.strip().splitlines() if s.strip()]
                sb.table("guides").upsert({
                    "slug": g_slug,
                    "title": g_title,
                    "subtitle": g_subtitle,
                    "cover_image": g_cover,
                    "category_tag": g_tag,
                    "intro": g_intro,
                    "body": g_body,
                    "spot_slugs": spot_slugs,
                    "status": g_status,
                }).execute()
                st.success(f"✅ '{g_title}' 저장 완료")
                st.rerun()

    st.divider()

    # 기존 가이드 목록
    for g in guides_data:
        with st.expander(f"{'🟢' if g.get('status') == 'published' else '⚪'} {g['title']} — /{g['slug']}"):
            e_title = st.text_input("제목", value=g["title"], key=f"et_{g['id']}")
            e_subtitle = st.text_area("부제", value=g.get("subtitle") or "", key=f"es_{g['id']}", height=80)
            e_cover = st.text_input("커버 이미지", value=g.get("cover_image") or "", key=f"ec_{g['id']}")
            e_tag = st.text_input("태그", value=g.get("category_tag") or "", key=f"etag_{g['id']}")
            e_intro = st.text_area("인트로", value=g.get("intro") or "", key=f"ei_{g['id']}", height=100)
            e_body = st.text_area("본문 (마크다운)", value=g.get("body") or "", key=f"eb_{g['id']}", height=300)
            e_spots = st.text_area(
                "스팟 목록",
                value="\n".join(g.get("spot_slugs") or []),
                key=f"esp_{g['id']}",
                height=150
            )
            e_status = st.selectbox("상태", ["draft", "published"],
                index=0 if g.get("status") == "draft" else 1,
                key=f"est_{g['id']}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("업데이트", key=f"upd_{g['id']}"):
                    spot_slugs = [s.strip() for s in e_spots.strip().splitlines() if s.strip()]
                    sb.table("guides").update({
                        "title": e_title,
                        "subtitle": e_subtitle,
                        "cover_image": e_cover,
                        "category_tag": e_tag,
                        "intro": e_intro,
                        "body": e_body,
                        "spot_slugs": spot_slugs,
                        "status": e_status,
                    }).eq("id", g["id"]).execute()
                    st.success("✅ 업데이트 완료")
                    st.rerun()
            with col2:
                if st.button("🗑️ 삭제", key=f"del_{g['id']}"):
                    sb.table("guides").delete().eq("id", g["id"]).execute()
                    st.rerun()

# ── TAB 4: MESSAGES ────────────────────────────────────────
with tab4:
    st.subheader("방문자 메시지")

    status_filter = st.selectbox("상태 필터", ["pending", "approved", "rejected"], key="msg_filter")
    msgs_res = sb.table("messages").select("*").eq("status", status_filter).order("created_at", desc=True).execute()
    msgs = msgs_res.data or []

    st.caption(f"{len(msgs)}개")

    for m in msgs:
        with st.container():
            st.markdown(f"**\"{m['message']}\"**")
            reply = st.text_input("답변", value=m.get("reply") or "", key=f"rep_{m['id']}", placeholder="답변 입력 (전광판에 표시됨)")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("✅ 승인", key=f"apr_{m['id']}"):
                    sb.table("messages").update({"status": "approved", "reply": reply}).eq("id", m["id"]).execute()
                    st.rerun()
            with col2:
                if st.button("❌ 거절", key=f"rej_{m['id']}"):
                    sb.table("messages").update({"status": "rejected"}).eq("id", m["id"]).execute()
                    st.rerun()
            with col3:
                if st.button("💾 답변저장", key=f"sav_{m['id']}"):
                    sb.table("messages").update({"reply": reply}).eq("id", m["id"]).execute()
                    st.success("저장됨")
            st.divider()
