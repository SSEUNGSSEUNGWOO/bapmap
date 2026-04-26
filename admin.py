import os
import sys
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pipeline.enrich import normalize_region, CATEGORIES
from pipeline.rag.embed_v2 import embed_spot

load_dotenv()

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

st.set_page_config(page_title="Bapmap Admin", page_icon="🍚", layout="wide")
st.title("🍚 Bapmap Admin")

col_f1, col_f2 = st.columns(2)
with col_f1:
    status_filter = st.selectbox("상태 필터", ["전체", "메모필요", "메모완료", "업로드완료"])

res = sb.table("spots").select(
    "id, name, english_name, city, region, subway, category, status, memo, rating, content, spice_level"
).order("created_at", desc=True).execute()
all_spots = res.data

cities = ["전체"] + sorted(set(r.get("city") or "기타" for r in all_spots))
with col_f2:
    city_filter = st.selectbox("도시 필터", cities)

restaurants = all_spots
if status_filter != "전체":
    restaurants = [r for r in restaurants if r.get("status") == status_filter]
if city_filter != "전체":
    restaurants = [r for r in restaurants if r.get("city") == city_filter]

st.write(f"총 {len(restaurants)}개")

for r in restaurants:
    location = r.get("region") or r.get("city") or ""
    subway = r.get("subway") or ""
    category = r.get("category") or ""
    with st.expander(
        f"{r['name']} ({r.get('english_name', '')}) — {r.get('status', '')} "
        f"| ★{r.get('rating', '')} | {location}"
        f"{' · 🚇' + subway if subway else ''}"
        f"{' · ' + category if category else ''}"
    ):
        loc_col1, loc_col2, loc_col3 = st.columns(3)
        with loc_col1:
            new_region = st.text_input("지역 (region)", value=r.get("region") or "", key=f"region_{r['id']}")
        with loc_col2:
            new_subway = st.text_input(
                "지하철역 (예: Gangnam Station, 5 min walk)",
                value=r.get("subway") or "", key=f"subway_{r['id']}"
            )
        with loc_col3:
            cur = r.get("category") or ""
            idx = CATEGORIES.index(cur) if cur in CATEGORIES else 0
            new_category = st.selectbox("카테고리", CATEGORIES, index=idx, key=f"category_{r['id']}")

        new_spice = st.select_slider(
            "매운맛",
            options=[0, 1, 2, 3],
            value=r.get("spice_level") or 0,
            format_func=lambda x: ["없음", "🌶️", "🌶️🌶️", "🌶️🌶️🌶️"][x],
            key=f"spice_{r['id']}"
        )

        memo = st.text_area("메모 (내부용)", value=r.get("memo") or "", key=f"memo_{r['id']}")
        content = st.text_area("본문", value=r.get("content") or "", height=200, key=f"content_{r['id']}")

        col_save, col_embed = st.columns(2)
        with col_save:
            if st.button("저장", key=f"save_{r['id']}"):
                auto_status = "업로드완료" if content.strip() else (
                    "메모완료" if memo.strip() else "메모필요"
                )
                sb.table("spots").update({
                    "memo": memo,
                    "content": content,
                    "status": auto_status,
                    "region": normalize_region(new_region),
                    "subway": new_subway,
                    "category": new_category,
                    "spice_level": new_spice if new_spice > 0 else None,
                }).eq("id", r["id"]).execute()
                st.success("저장됨!")
                st.rerun()
        with col_embed:
            if st.button("🔄 임베딩 재실행", key=f"embed_{r['id']}"):
                if not content.strip():
                    st.error("본문이 없습니다")
                else:
                    with st.spinner("임베딩 중..."):
                        spot_data = sb.table("spots").select("*").eq("id", r["id"]).single().execute().data
                        spot_data["content"] = content
                        embed_spot(spot_data)
                    st.success("✅ 임베딩 완료")
