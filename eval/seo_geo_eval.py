"""
═══════════════════════════════════════════════════════════════════
SEO / GEO 평가 도구
═══════════════════════════════════════════════════════════════════

■ 개요
  회사명 입력 → 공식 사이트 자동 탐색 → SEO/GEO 점수 자동 평가

■ 평가 방식 두 가지
  ┌─────────────────────────────────────────────────────────────┐
  │ SEO (Search Engine Optimization)                            │
  │  - 전통적인 검색엔진(Google, Naver) 최적화 지표             │
  │  - Rule-based: HTML 구조를 직접 파싱해 규칙으로 점수화      │
  │  - 기준: Google Search Central 공식 가이드라인              │
  ├─────────────────────────────────────────────────────────────┤
  │ GEO (Generative Engine Optimization)                        │
  │  - AI 검색엔진(ChatGPT, Perplexity, Google AI Overview)     │
  │    에서 콘텐츠가 얼마나 잘 인용되는지 평가                  │
  │  - LLM 평가: G-Eval 방식으로 GPT가 직접 채점               │
  │  - 기준: GEO 논문(arxiv 2311.09735) 기반 5개 항목 재정의    │
  └─────────────────────────────────────────────────────────────┘

■ 참고 논문
  - GEO: Generative Engine Optimization (arxiv.org/abs/2311.09735)
    → AI 검색엔진에서 콘텐츠 노출을 높이는 최적화 전략 연구
    → 인용/통계 추가, 권위성 강화가 가장 효과적 (최대 40% 향상)
  - G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment
    → LLM을 평가자로 활용, Chain-of-Thought로 점수 + 근거 생성
    → 인간 평가와 높은 상관관계 (기존 BLEU/ROUGE 대비 우수)

■ 점수 체계
  - SEO: 8개 항목 각 10점 만점 → 평균으로 100점 환산
  - GEO: 5개 항목 각 10점 만점 → 평균으로 100점 환산
  - 종합: SEO + GEO 평균
  - 뱃지: 7~10점 = 우수(초록), 4~6점 = 보통(노랑), 1~3점 = 미흡(빨강)

■ 의존성
  pip install streamlit duckduckgo-search requests beautifulsoup4
              openai plotly python-dotenv
═══════════════════════════════════════════════════════════════════
"""

import re
import json
import requests
import streamlit as st
import plotly.graph_objects as go
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# ── 페이지 설정 ────────────────────────────────────────
st.set_page_config(
    page_title="SEO / GEO 평가",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #0f1117; color: #e0e0e0; }
[data-testid="stSidebar"] { background: #1a1d27; }

.score-card {
    background: #1e2130;
    border: 1px solid #2d3148;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
}
.score-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #8b8fa8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.3rem;
}
.score-value {
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
}
.score-seo { color: #60a5fa; }
.score-geo { color: #a78bfa; }
.score-total { color: #34d399; }

.item-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #1e2130;
    font-size: 0.88rem;
}
.item-label { color: #9ca3af; }
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-good { background: #064e3b; color: #6ee7b7; }
.badge-mid  { background: #451a03; color: #fcd34d; }
.badge-bad  { background: #450a0a; color: #fca5a5; }

.suggest-box {
    background: #1a2332;
    border-left: 3px solid #60a5fa;
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.88rem;
    color: #cbd5e1;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# 1. URL 자동 탐색
# ══════════════════════════════════════════════════════
def find_url(company_name: str) -> str | None:
    """
    DuckDuckGo 검색으로 회사 공식 사이트 URL을 자동 탐색한다.

    탐색 전략:
      1. "{회사명} 공식 사이트" 로 검색
      2. "{회사명} official website" 로 검색 (영문 회사명 대응)
      3. 회사명만으로 검색 (위 두 쿼리 실패 시 폴백)

    필터링:
      - SNS(facebook, instagram, twitter), 포털 검색결과(naver.com/search),
        위키(wikipedia, namu.wiki), 유튜브 제외
      - 검색 결과 상위 5개 중 필터 통과한 첫 번째 URL 반환
    """
    queries = [
        f"{company_name} 공식 사이트",
        f"{company_name} official website",
        f"{company_name}",
    ]
    for q in queries:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(q, max_results=5))
            for r in results:
                url = r.get("href", "")
                skip = ["facebook", "instagram", "twitter", "naver.com/search",
                        "google.", "youtube", "namu.wiki", "wikipedia"]
                if url and not any(s in url for s in skip):
                    return url
        except Exception:
            continue
    return None


# ══════════════════════════════════════════════════════
# 2. 페이지 크롤링
# ══════════════════════════════════════════════════════
def crawl(url: str) -> dict:
    """
    URL을 크롤링해 SEO/GEO 분석에 필요한 데이터를 추출한다.

    추출 항목:
      - title       : <title> 태그 텍스트
      - meta_desc   : <meta name="description"> content 값
      - h1/h2/h3    : 각 헤딩 태그 텍스트 목록
      - img_total   : 전체 이미지 수
      - img_no_alt  : alt 속성 없는 이미지 수
      - links       : 전체 링크(<a href>) 수
      - has_schema  : JSON-LD 구조화 데이터(schema.org) 존재 여부
      - has_og      : Open Graph 메타태그(og:title) 존재 여부
      - word_count  : 본문 단어 수
      - text        : 정제된 본문 텍스트 (LLM 평가용, 최대 4000자)

    전처리:
      - script, style, nav, footer 태그 제거 후 순수 텍스트 추출
      - 연속 공백 정규화
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        return {"error": str(e)}

    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()

    return {
        "url": url,
        "title": soup.title.string.strip() if soup.title else "",
        "meta_desc": (soup.find("meta", attrs={"name": "description"}) or {}).get("content", ""),
        "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
        "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
        "h3": [h.get_text(strip=True) for h in soup.find_all("h3")],
        "img_total": len(soup.find_all("img")),
        "img_no_alt": len([i for i in soup.find_all("img") if not i.get("alt")]),
        "links": len(soup.find_all("a", href=True)),
        "has_schema": bool(soup.find("script", attrs={"type": "application/ld+json"})),
        "has_og": bool(soup.find("meta", property="og:title")),
        "word_count": len(text.split()),
        "text": text[:4000],
    }


# ══════════════════════════════════════════════════════
# 2-1. 하위 페이지 탐색
# ══════════════════════════════════════════════════════
def find_subpages(base_url: str, html: str, max_pages: int = 4) -> list[str]:
    """
    메인 페이지 HTML에서 같은 도메인의 내부 링크를 추출한다.

    우선순위: blog, about, product, service 등 콘텐츠가 풍부할 가능성이
             높은 경로 키워드를 앞에 배치한다.
    필터:    이미지/파일 확장자, 쿼리 파라미터, 외부 도메인 제외.
    """
    from urllib.parse import urljoin, urlparse

    base_parsed = urlparse(base_url)
    priority_kw = ["blog", "about", "product", "service", "story", "news",
                   "소개", "제품", "블로그", "서비스", "뉴스", "포스트"]
    skip_ext = (".jpg", ".jpeg", ".png", ".gif", ".pdf", ".zip",
                ".mp4", ".svg", ".ico", ".webp")

    soup_sub = BeautifulSoup(html, "html.parser")
    priority, normal = [], []
    seen = {base_url}

    for a in soup_sub.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "#", "javascript:")):
            continue
        full_url = urljoin(base_url, href).split("?")[0].split("#")[0]
        parsed = urlparse(full_url)
        if parsed.netloc != base_parsed.netloc:
            continue
        if any(full_url.lower().endswith(ext) for ext in skip_ext):
            continue
        if full_url in seen:
            continue
        seen.add(full_url)
        if any(kw in parsed.path.lower() for kw in priority_kw):
            priority.append(full_url)
        else:
            normal.append(full_url)

    return (priority + normal)[:max_pages]


# ══════════════════════════════════════════════════════
# 2-2. 멀티페이지 크롤링
# ══════════════════════════════════════════════════════
def crawl_multipage(url: str) -> dict:
    """
    메인 페이지 + 최대 4개 하위 페이지를 크롤링해 SEO/GEO 데이터를 집계한다.

    집계 방식:
      - has_schema / has_og  : 어느 페이지든 하나라도 있으면 True (OR)
      - h1 / h2 / h3         : 전체 페이지 헤딩 합산
      - img_total / img_no_alt / links / word_count : 합산
      - title / meta_desc    : 메인 페이지 기준 (대표성 높음)
      - text                 : 각 페이지 텍스트 이어붙여 최대 4000자 (GEO 평가용)
      - pages_crawled        : 실제 성공한 페이지 수 (UI 표시용)
      - crawled_urls         : 크롤링한 URL 목록
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # 메인 페이지 fetch (HTML은 하위 링크 탐색에도 재사용)
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = resp.apparent_encoding
        main_html = resp.text
    except Exception as e:
        return {"error": str(e)}

    main_data = crawl(url)
    if "error" in main_data:
        return main_data

    sub_urls = find_subpages(url, main_html, max_pages=4)
    all_data = [main_data]
    for sub_url in sub_urls:
        sub_data = crawl(sub_url)
        if "error" not in sub_data:
            all_data.append(sub_data)

    agg = {
        "url": url,
        "title": all_data[0]["title"],
        "meta_desc": all_data[0]["meta_desc"],
        "h1": [], "h2": [], "h3": [],
        "img_total": 0, "img_no_alt": 0, "links": 0,
        "has_schema": False, "has_og": False,
        "word_count": 0, "text": "",
        "pages_crawled": len(all_data),
        "crawled_urls": [d["url"] for d in all_data],
    }
    texts = []
    for d in all_data:
        agg["h1"].extend(d.get("h1", []))
        agg["h2"].extend(d.get("h2", []))
        agg["h3"].extend(d.get("h3", []))
        agg["img_total"] += d.get("img_total", 0)
        agg["img_no_alt"] += d.get("img_no_alt", 0)
        agg["links"] += d.get("links", 0)
        agg["has_schema"] = agg["has_schema"] or d.get("has_schema", False)
        agg["has_og"] = agg["has_og"] or d.get("has_og", False)
        agg["word_count"] += d.get("word_count", 0)
        texts.append(d.get("text", ""))
    agg["text"] = " ".join(texts)[:4000]
    return agg


# ══════════════════════════════════════════════════════
# 3. SEO 분석 (Rule-based)
# ══════════════════════════════════════════════════════
def analyze_seo(data: dict) -> dict:
    """
    HTML 구조를 파싱해 SEO 점수를 rule-based로 산출한다.
    기준: Google Search Central 공식 가이드라인

    ┌──────────────────┬──────────────────────────────────────┬──────────────────────────────────────────┐
    │ 항목             │ 근거 출처                             │ 채점 기준                                 │
    ├──────────────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
    │ 타이틀 태그      │ [출처] Google Search Central 공식     │ 10~60자: 10점 / 범위 외: 6점 / 없음: 0점 │
    │                  │ 문서 (developers.google.com/search)   │ 60자 초과 시 검색결과에서 잘려 표시됨    │
    ├──────────────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
    │ 메타 디스크립션  │ [출처] Google Search Central 공식     │ 50~160자: 10점 / 범위 외: 5점 / 없음: 0점│
    │                  │ 문서 (snippet 가이드라인)              │ 검색결과 스니펫으로 직접 표시, CTR 영향  │
    ├──────────────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
    │ H1 태그          │ [출처] Google SEO 가이드 + HTML 표준  │ 1개: 10점 / 2개 이상: 6점 / 없음: 0점   │
    │                  │ (W3C HTML 명세 - 페이지당 1개 권장)   │ 복수 H1은 주제 혼란으로 감점             │
    ├──────────────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
    │ 헤딩 구조        │ [출처] Moz/Ahrefs 업계 표준           │ H2 2개 이상: 10점 / 1개: 6점 / 없음: 2점│
    │                  │ (콘텐츠 계층 구조 SEO 모범 사례)      │ 계층 구조 명확할수록 크롤링 효율 향상    │
    ├──────────────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
    │ 콘텐츠 길이      │ [출처] Backlinko 연구                 │ 800단어↑: 10점 / 300~799: 6점 / ~300: 2점│
    │                  │ (구글 상위 노출 페이지 분석, 2020)    │ 깊이 있는 콘텐츠일수록 순위 유리         │
    ├──────────────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
    │ 이미지 Alt       │ [출처] WCAG 2.1 웹 접근성 가이드라인 │ alt 없는 비율로 감점                     │
    │                  │ + Google 이미지 SEO 공식 가이드       │ (alt 있는 수 / 전체) × 10점              │
    ├──────────────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
    │ 구조화 데이터    │ [출처] Google Search Central +        │ JSON-LD 존재: 10점 / 없음: 0점           │
    │                  │ schema.org 공식 명세                  │ 리치 스니펫(별점/가격/FAQ) 표시에 필수   │
    ├──────────────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
    │ OG 태그          │ [출처] Open Graph Protocol            │ og:title 존재: 10점 / 없음: 0점          │
    │                  │ (Facebook 제정, 현재 업계 표준)       │ SNS 공유 미리보기 품질 제어              │
    └──────────────────┴──────────────────────────────────────┴──────────────────────────────────────────┘

    최종 점수 = 각 항목 점수 합계 / (항목 수 × 10) × 100
    """
    scores = {}
    details = {}

    # 타이틀 태그: Google은 60자 초과 시 검색결과에서 잘라냄
    title = data.get("title", "")
    if 10 <= len(title) <= 60:
        scores["타이틀 태그"] = 10
    elif title:
        scores["타이틀 태그"] = 6
    else:
        scores["타이틀 태그"] = 0
    details["타이틀 태그"] = f'"{title}" ({len(title)}자)'

    # 메타 디스크립션: 검색결과 스니펫 표시 영역, CTR(클릭률)에 직접 영향
    meta = data.get("meta_desc", "")
    if 50 <= len(meta) <= 160:
        scores["메타 디스크립션"] = 10
    elif meta:
        scores["메타 디스크립션"] = 5
    else:
        scores["메타 디스크립션"] = 0
    details["메타 디스크립션"] = f"{len(meta)}자" if meta else "없음"

    # H1 태그: 페이지의 주제를 나타내는 최상위 헤딩, 1개가 표준
    h1s = data.get("h1", [])
    if len(h1s) == 1:
        scores["H1 태그"] = 10
    elif len(h1s) > 1:
        scores["H1 태그"] = 6  # 복수 H1은 구조적으로 혼란
    else:
        scores["H1 태그"] = 0
    details["H1 태그"] = f"{len(h1s)}개"

    # 헤딩 구조: H2 이상이 있어야 콘텐츠 계층 구조가 명확
    h2_count = len(data.get("h2", []))
    h3_count = len(data.get("h3", []))
    if h2_count >= 2:
        scores["헤딩 구조"] = 10
    elif h2_count == 1:
        scores["헤딩 구조"] = 6
    else:
        scores["헤딩 구조"] = 2
    details["헤딩 구조"] = f"H2: {h2_count}개, H3: {h3_count}개"

    # 콘텐츠 길이: 깊이 있는 콘텐츠가 검색 순위에 유리 (업계 통계 기준)
    wc = data.get("word_count", 0)
    if wc >= 800:
        scores["콘텐츠 길이"] = 10
    elif wc >= 300:
        scores["콘텐츠 길이"] = 6
    else:
        scores["콘텐츠 길이"] = 2
    details["콘텐츠 길이"] = f"{wc}단어"

    # 이미지 Alt: 접근성(웹 표준) + 구글 이미지 검색 최적화
    # alt 없는 이미지 비율로 감점: (alt 있는 이미지 / 전체) × 10
    total_img = data.get("img_total", 0)
    no_alt = data.get("img_no_alt", 0)
    if total_img == 0 or no_alt == 0:
        scores["이미지 Alt"] = 10
    else:
        ratio = (total_img - no_alt) / total_img
        scores["이미지 Alt"] = round(ratio * 10)
    details["이미지 Alt"] = f"전체 {total_img}개 중 alt 없음 {no_alt}개"

    # 구조화 데이터: JSON-LD(schema.org) 마크업으로 리치 스니펫 활성화 가능
    # 별점, 가격, FAQ, 이벤트 등 검색결과 강조 표시에 활용
    scores["구조화 데이터"] = 10 if data.get("has_schema") else 0
    details["구조화 데이터"] = "있음" if data.get("has_schema") else "없음"

    # OG 태그: SNS 공유 시 제목/이미지/설명 미리보기 제어
    # SNS 유입 트래픽 품질에 영향
    scores["OG 태그"] = 10 if data.get("has_og") else 0
    details["OG 태그"] = "있음" if data.get("has_og") else "없음"

    total = round(sum(scores.values()) / (len(scores) * 10) * 100)
    return {"scores": scores, "details": details, "total": total}


# ══════════════════════════════════════════════════════
# 4. GEO 평가 (G-Eval 방식 LLM)
# ══════════════════════════════════════════════════════

# ────────────────────────────────────────────────────────────────────
# 평가 방법론: G-Eval (arxiv.org/abs/2303.16634)
#   - LLM을 평가자(evaluator)로 사용하는 프레임워크
#   - Chain-of-Thought: 점수만 요청하지 않고 근거(reason)도 함께 생성
#     → 단순 점수보다 신뢰도 높고 인간 평가와 상관관계 높음
#   - temperature=0: 동일 입력에 항상 같은 점수 (재현성 확보)
#   - JSON 구조화 출력: 파싱 오류 없이 안정적 처리
#
# ────────────────────────────────────────────────────────────────────
# GEO 5개 항목 출처 및 재정의 근거
# ────────────────────────────────────────────────────────────────────
#
# ┌──────────────────────┬──────────────────────────────────┬──────────────────────────────────────┐
# │ 항목                 │ 출처                              │ 재정의 여부 및 근거                   │
# ├──────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
# │ 인용 가능성          │ [논문 직접] GEO 논문 Fig.3        │ 논문 그대로 사용                      │
# │ (Citation            │ "Citations/Quotations Addition"   │ 통계/인용 추가 시 visibility +40%    │
# │  Worthiness)         │ 이 가장 효과적인 전략으로 제시    │ → 가장 효과 큰 항목으로 확인됨        │
# ├──────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
# │ 권위성               │ [논문 + 확장] GEO 논문의          │ 논문 기반 + Google E-E-A-T 확장       │
# │ (Authority Signals)  │ "Cite Sources" 전략 +             │ E-E-A-T: Experience, Expertise,      │
# │                      │ Google E-E-A-T 가이드라인         │ Authoritativeness, Trustworthiness    │
# │                      │ (search quality evaluator guide)  │ → AI도 권위 있는 소스를 우선 인용    │
# ├──────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
# │ 구조 명확성          │ [논문 기반 재정의]                 │ 논문의 "Easy-to-Understand"           │
# │ (Structural          │ GEO 논문의 가독성/파싱 용이성     │ 전략을 AI 파싱 관점으로 재해석        │
# │  Clarity)            │ 개념을 구조적 명확성으로 재정의   │ 논문 원어 항목명과 다름 (자체 재정의) │
# ├──────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
# │ 답변 직접성          │ [시중 서비스 + 자체 정의]         │ 논문에 직접 대응 항목 없음            │
# │ (Answer              │ Semrush GEO 가이드,               │ Perplexity/AI Overview 실제 인용      │
# │  Directness)         │ Search Engine Journal 분석 참고   │ 패턴 분석 기반으로 자체 정의          │
# ├──────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
# │ 고유성               │ [논문 직접] GEO 논문의            │ 논문 그대로 사용                      │
# │ (Uniqueness)         │ "Uniqueness" 항목 (Table 2)       │ 독자적 정보일수록 AI 인용 가치 높음   │
# │                      │ subjective impression metrics     │ 논문의 visibility 지표 중 하나        │
# └──────────────────────┴──────────────────────────────────┴──────────────────────────────────────┘

GEO_PROMPT = """당신은 GEO(Generative Engine Optimization) 전문 평가자입니다.
아래 웹페이지 콘텐츠를 분석하여 AI 검색엔진(ChatGPT, Perplexity, Google AI Overview 등)에서
얼마나 잘 인용될 수 있는지 평가하세요.

각 항목을 1~10점으로 채점하고 근거를 설명하세요.

[평가 항목]
1. 인용 가능성 (Citation Worthiness): 통계, 수치, 연구 결과 등 인용할 만한 구체적 정보 포함 여부
2. 권위성 (Authority Signals): 전문 용어, 출처 명시, 공신력 있는 정보 포함 여부
3. 구조 명확성 (Structural Clarity): AI가 정보를 파싱하기 쉬운 명확한 구조 (리스트, 단락 구분 등)
4. 답변 직접성 (Answer Directness): 사용자 질문에 직접적으로 답하는 형태의 콘텐츠 여부
5. 고유성 (Uniqueness): 다른 곳에서 찾기 어려운 독자적 정보나 인사이트 포함 여부

[콘텐츠]
{text}

[출력 형식 - 반드시 JSON으로만 응답]
{{
  "인용 가능성": {{"score": 점수, "reason": "근거", "suggestion": "개선 제안"}},
  "권위성": {{"score": 점수, "reason": "근거", "suggestion": "개선 제안"}},
  "구조 명확성": {{"score": 점수, "reason": "근거", "suggestion": "개선 제안"}},
  "답변 직접성": {{"score": 점수, "reason": "근거", "suggestion": "개선 제안"}},
  "고유성": {{"score": 점수, "reason": "근거", "suggestion": "개선 제안"}}
}}"""


def evaluate_geo(text: str) -> dict:
    """
    G-Eval 방식으로 GEO 점수를 LLM이 평가한다.

    G-Eval 핵심 원칙:
      1. LLM에게 평가 기준(rubric)을 명확히 제시
      2. Chain-of-Thought: 점수 + 근거 + 개선 제안 함께 생성
      3. temperature=0: 동일 입력에 일관된 점수 (재현성)
      4. JSON 구조화 출력: 파싱 오류 없이 안정적 처리

    반환값:
      scores  : {"항목명": 점수} 딕셔너리
      details : {"항목명": {"score", "reason", "suggestion"}} 딕셔너리
      total   : 100점 환산 최종 점수
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": GEO_PROMPT.format(text=text)}],
        temperature=0,           # 재현성을 위해 0으로 고정
        response_format={"type": "json_object"},  # JSON 파싱 오류 방지
    )
    result = json.loads(response.choices[0].message.content)
    scores = {k: v["score"] for k, v in result.items()}
    total = round(sum(scores.values()) / (len(scores) * 10) * 100)
    return {"scores": scores, "details": result, "total": total}


# ══════════════════════════════════════════════════════
# 5. 레이더 차트
# ══════════════════════════════════════════════════════
def make_radar(labels: list, values: list, name: str, color: str) -> go.Figure:
    """단일 레이더 차트 생성"""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        name=name,
        line_color=color,
        fillcolor=color.replace(")", ", 0.15)").replace("rgb", "rgba") if "rgb" in color
                  else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], color="#4b5563"),
            bgcolor="#1e2130",
            angularaxis=dict(color="#9ca3af", tickfont=dict(size=11)),
        ),
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        font_color="#e0e0e0",
        showlegend=False,
        margin=dict(l=50, r=50, t=30, b=30),
        height=380,
    )
    return fig


def score_badge(score: int) -> str:
    """점수 구간별 색상 뱃지 HTML 반환 (7+: 초록, 4~6: 노랑, 1~3: 빨강)"""
    if score >= 7:
        return f'<span class="badge badge-good">{score}/10</span>'
    elif score >= 4:
        return f'<span class="badge badge-mid">{score}/10</span>'
    else:
        return f'<span class="badge badge-bad">{score}/10</span>'


def make_radar_multi(labels: list, company_traces: list, height: int = 400) -> go.Figure:
    """
    여러 회사를 하나의 레이더 차트에 오버레이한다.
    company_traces: [(name, values, color), ...]
    """
    fig = go.Figure()
    for name, values, color in company_traces:
        h = color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            name=name,
            line_color=color,
            fillcolor=f"rgba({r},{g},{b},0.18)",
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], color="#4b5563"),
            bgcolor="#1e2130",
            angularaxis=dict(color="#9ca3af", tickfont=dict(size=11)),
        ),
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        font_color="#e0e0e0",
        showlegend=True,
        legend=dict(bgcolor="#1e2130", bordercolor="#2d3148",
                    font=dict(color="#e0e0e0", size=11)),
        margin=dict(l=50, r=50, t=30, b=30),
        height=height,
    )
    return fig


COMP_COLORS = ["#60a5fa", "#f97316", "#34d399"]


# ══════════════════════════════════════════════════════
# 6. UI
# ══════════════════════════════════════════════════════
st.markdown("## 📊 SEO / GEO 평가 도구")
st.markdown("<div style='color:#6b7280;margin-bottom:1.5rem;'>회사명 입력 → 공식 사이트 자동 탐색 → 멀티페이지 크롤링 → SEO/GEO 분석</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 단일 평가", "⚔️ 경쟁사 비교"])


# ─────────────────────────────────────────────────────
# Tab 1: 단일 평가 (멀티페이지 크롤링 적용)
# ─────────────────────────────────────────────────────
def _render_single_result(url, data, seo, geo):
    pages_n = data.get("pages_crawled", 1)
    if data.get("crawled_urls"):
        with st.expander(f"크롤링한 페이지 ({pages_n}개)"):
            for u in data["crawled_urls"]:
                st.markdown(f"- `{u}`")

    st.markdown("---")
    total_score = round((seo["total"] + geo["total"]) / 2)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-title">SEO 점수</div>
            <div class="score-value score-seo">{seo['total']}</div>
            <div style="color:#6b7280;font-size:0.8rem;">/ 100</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-title">GEO 점수</div>
            <div class="score-value score-geo">{geo['total']}</div>
            <div style="color:#6b7280;font-size:0.8rem;">/ 100</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-title">종합 점수</div>
            <div class="score-value score-total">{total_score}</div>
            <div style="color:#6b7280;font-size:0.8rem;">/ 100 &nbsp;·&nbsp; {url}</div>
        </div>""", unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("#### 🔵 SEO 레이더")
        fig_seo = make_radar(list(seo["scores"].keys()), list(seo["scores"].values()), "SEO", "#60a5fa")
        st.plotly_chart(fig_seo, use_container_width=True)
    with chart_col2:
        st.markdown("#### 🟣 GEO 레이더")
        fig_geo = make_radar(list(geo["scores"].keys()), list(geo["scores"].values()), "GEO", "#a78bfa")
        st.plotly_chart(fig_geo, use_container_width=True)

    col_seo, col_geo = st.columns(2)
    with col_seo:
        st.markdown("### 🔵 SEO 항목별 점수")
        for item, score in seo["scores"].items():
            detail = seo["details"].get(item, "")
            st.markdown(f"""
            <div class="item-row">
                <span class="item-label">{item}<br>
                <span style="font-size:0.75rem;color:#4b5563">{detail}</span></span>
                {score_badge(score)}
            </div>""", unsafe_allow_html=True)
    with col_geo:
        st.markdown("### 🟣 GEO 항목별 점수")
        for item, val in geo["details"].items():
            st.markdown(f"""
            <div class="item-row">
                <span class="item-label">{item}<br>
                <span style="font-size:0.75rem;color:#4b5563">{val['reason'][:60]}...</span></span>
                {score_badge(val['score'])}
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 GEO 개선 제안")
    for item, val in geo["details"].items():
        if val["score"] < 8:
            st.markdown(f"""
            <div class="suggest-box">
                <strong>{item}</strong><br>{val['suggestion']}
            </div>""", unsafe_allow_html=True)


with tab1:
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        company = st.text_input("", placeholder="예: 푸드올로지, 삼성전자, 네이버",
                                label_visibility="collapsed", key="single_company")
    with col_btn:
        run = st.button("평가 시작", type="primary", use_container_width=True, key="single_run")

    if run and company:
        with st.status(f"**{company}** 평가 중...", expanded=True) as status:
            st.write("🔍 공식 사이트 탐색 중...")
            url = find_url(company)
            if not url:
                st.error("공식 사이트를 찾지 못했습니다. 회사명을 다시 확인해주세요.")
                st.stop()
            st.write(f"✅ 사이트 발견: `{url}`")

            st.write("📄 멀티페이지 크롤링 중...")
            data = crawl_multipage(url)
            if "error" in data:
                st.error(f"크롤링 실패: {data['error']}")
                st.stop()
            pages_n = data.get("pages_crawled", 1)
            st.write(f"✅ {pages_n}개 페이지 수집 완료 ({data['word_count']}단어)")

            st.write("🔎 SEO 분석 중...")
            seo = analyze_seo(data)
            st.write("✅ SEO 분석 완료")

            st.write("🤖 GEO LLM 평가 중...")
            geo = evaluate_geo(data["text"])
            st.write("✅ GEO 평가 완료")

            status.update(label="평가 완료!", state="complete")

        _render_single_result(url, data, seo, geo)


# ─────────────────────────────────────────────────────
# Tab 2: 경쟁사 비교 (최대 3개사 동시 평가)
# ─────────────────────────────────────────────────────
with tab2:
    st.markdown("<div style='color:#6b7280;margin-bottom:1rem;'>최대 3개 회사를 동시에 평가해 레이더 차트로 비교합니다</div>",
                unsafe_allow_html=True)

    ci1, ci2, ci3 = st.columns(3)
    with ci1:
        comp1 = st.text_input("회사 1", placeholder="예: 삼성전자", key="comp1")
    with ci2:
        comp2 = st.text_input("회사 2", placeholder="예: LG전자", key="comp2")
    with ci3:
        comp3 = st.text_input("회사 3 (선택)", placeholder="예: 애플", key="comp3")

    run_compare = st.button("비교 분석 시작", type="primary", key="compare_run")

    if run_compare:
        companies_input = [c.strip() for c in [comp1, comp2, comp3] if c.strip()]
        if len(companies_input) < 2:
            st.warning("최소 2개 회사를 입력해주세요.")
            st.stop()

        results = []  # [(name, url, seo_dict, geo_dict), ...]

        with st.status("경쟁사 비교 분석 중...", expanded=True) as status:
            for i, company_name in enumerate(companies_input):
                st.write(f"**[{i+1}/{len(companies_input)}] {company_name}** 분석 시작")

                url_c = find_url(company_name)
                if not url_c:
                    st.warning(f"⚠️ {company_name}: 공식 사이트를 찾지 못했습니다. 건너뜁니다.")
                    continue
                st.write(f"  ✅ `{url_c}`")

                data_c = crawl_multipage(url_c)
                if "error" in data_c:
                    st.warning(f"⚠️ {company_name}: 크롤링 실패. 건너뜁니다.")
                    continue
                pn = data_c.get("pages_crawled", 1)
                st.write(f"  📄 {pn}개 페이지 수집 ({data_c['word_count']}단어)")

                seo_c = analyze_seo(data_c)
                geo_c = evaluate_geo(data_c["text"])
                results.append((company_name, url_c, seo_c, geo_c))
                st.write(f"  📊 SEO {seo_c['total']} / GEO {geo_c['total']}")

            if not results:
                st.error("분석 가능한 회사가 없습니다.")
                st.stop()
            status.update(label=f"비교 완료! ({len(results)}개 회사)", state="complete")

        st.markdown("---")

        # ── 종합 점수 비교 표 ──────────────────────────
        st.markdown("### 📊 종합 점수 비교")
        grid_cols = f"140px {' '.join(['1fr'] * len(results))}"
        header = f"<div style='display:grid;grid-template-columns:{grid_cols};gap:0.5rem;margin-bottom:0.6rem;'>"
        header += "<div style='color:#6b7280;font-size:0.8rem;font-weight:600;'>구분</div>"
        for name, _, _, _ in results:
            header += f"<div style='text-align:center;font-size:0.88rem;font-weight:600;color:#e0e0e0'>{name}</div>"
        header += "</div>"
        st.markdown(header, unsafe_allow_html=True)

        for label, getter in [
            ("SEO 점수",  lambda r: r[2]["total"]),
            ("GEO 점수",  lambda r: r[3]["total"]),
            ("종합 점수", lambda r: round((r[2]["total"] + r[3]["total"]) / 2)),
        ]:
            scores_row = [getter(r) for r in results]
            best = max(scores_row)
            row = f"<div style='display:grid;grid-template-columns:{grid_cols};gap:0.5rem;padding:0.4rem 0;border-bottom:1px solid #1e2130;'>"
            row += f"<div style='color:#9ca3af;font-size:0.82rem;line-height:2'>{label}</div>"
            for s in scores_row:
                style = "color:#34d399;font-weight:700;" if s == best else "color:#e0e0e0;"
                row += f"<div style='{style}font-size:1.15rem;text-align:center'>{s}</div>"
            row += "</div>"
            st.markdown(row, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 비교 레이더 차트 ──────────────────────────
        seo_traces = [(name, list(seo["scores"].values()), COMP_COLORS[i])
                      for i, (name, _, seo, _) in enumerate(results)]
        geo_traces = [(name, list(geo["scores"].values()), COMP_COLORS[i])
                      for i, (name, _, _, geo) in enumerate(results)]
        seo_labels = list(results[0][2]["scores"].keys())
        geo_labels = list(results[0][3]["scores"].keys())

        chart_c1, chart_c2 = st.columns(2)
        with chart_c1:
            st.markdown("#### 🔵 SEO 비교 레이더")
            st.plotly_chart(make_radar_multi(seo_labels, seo_traces), use_container_width=True)
        with chart_c2:
            st.markdown("#### 🟣 GEO 비교 레이더")
            st.plotly_chart(make_radar_multi(geo_labels, geo_traces), use_container_width=True)

        # ── 항목별 세부 비교 ──────────────────────────
        st.markdown("---")
        st.markdown("### 🔵 SEO 항목별 비교")
        item_cols = st.columns(len(results))
        for i, (name, _, seo, _) in enumerate(results):
            with item_cols[i]:
                st.markdown(f"**<span style='color:{COMP_COLORS[i]}'>{name}</span>**",
                            unsafe_allow_html=True)
                for item, score in seo["scores"].items():
                    detail = seo["details"].get(item, "")
                    st.markdown(f"""
                    <div class="item-row">
                        <span class="item-label" style="font-size:0.8rem">{item}<br>
                        <span style="font-size:0.72rem;color:#4b5563">{detail}</span></span>
                        {score_badge(score)}
                    </div>""", unsafe_allow_html=True)

        st.markdown("### 🟣 GEO 항목별 비교")
        item_cols2 = st.columns(len(results))
        for i, (name, _, _, geo) in enumerate(results):
            with item_cols2[i]:
                st.markdown(f"**<span style='color:{COMP_COLORS[i]}'>{name}</span>**",
                            unsafe_allow_html=True)
                for item, val in geo["details"].items():
                    st.markdown(f"""
                    <div class="item-row">
                        <span class="item-label" style="font-size:0.8rem">{item}<br>
                        <span style="font-size:0.72rem;color:#4b5563">{val['reason'][:55]}...</span></span>
                        {score_badge(val['score'])}
                    </div>""", unsafe_allow_html=True)
