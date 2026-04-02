# 🍜 Bapmap

> **한국 로컬 맛집을 외국인 관광객에게 연결하는 자동화 콘텐츠 플랫폼**

영어권·일본어권 외국인이 "한국인이 실제로 가는 맛집"을 찾기 어렵다는 문제를 해결합니다.
현지인 큐레이션 데이터 기반으로 콘텐츠를 자동 생성하고, SEO/GEO 최적화를 통해 검색 노출을 극대화합니다.

---

## 타겟

- 한국을 방문하는 **영어권 외국인 관광객** (1차)
- 한국을 방문하는 **일본어권 외국인 관광객** (2차 예정)

---

## 핵심 파이프라인

```
Google Sheets (가게 데이터 + 큐레이터 메모)
        ↓
카카오 로컬 API (주소·영업시간·카테고리 자동 보강)
        ↓
Claude API (영어 블로그 포스팅 자동 생성)
        ↓
WordPress REST API (자동 업로드)
        ↓
Instagram (캡션 자동 생성 및 포스팅)
        ↓
SEO / GEO 점수 자동 측정 및 전략 리포트
```

---

## 수익 모델

| 단계 | 방식 |
|------|------|
| 초기 | Google AdSense (트래픽 기반 광고 수익) |
| 성장 | Google Ads 집행 → 트래픽 가속 |
| 확장 | 제휴 마케팅 (예약 플랫폼, 투어 상품 등) |

---

## 기술 스택

| 영역 | 도구 |
|------|------|
| 언어 | Python 3.11+ |
| 콘텐츠 생성 | Claude API (Anthropic) |
| 데이터 소스 | Google Sheets API |
| 맛집 정보 보강 | 카카오 로컬 API |
| CMS | WordPress (REST API) |
| SNS | Instagram Graph API |
| SEO/GEO 평가 | 자체 구현 (`seo_geo_eval.py`) |
| UI | Streamlit |
| 시각화 | Plotly |

---

## 프로젝트 구조

```
Bapmap/
│
├── README.md
├── .env                         # API 키 모음 (git 제외)
├── requirements.txt
│
├── pipeline/
│   ├── sheets.py                # Google Sheets 데이터 읽기/쓰기
│   ├── kakao.py                 # 카카오 로컬 API로 가게 정보 보강
│   ├── generator.py             # Claude API → 영어 포스팅 생성
│   ├── wordpress.py             # WordPress REST API 업로드
│   └── instagram.py             # Instagram 자동 포스팅
│
├── eval/
│   └── seo_geo_eval.py          # SEO/GEO 점수 측정 (Streamlit 앱)
│
├── scraper/
│   └── naver_saved.py           # 네이버 지도 저장 목록 스크래핑 (Playwright)
│
└── main.py                      # CLI 진입점 (전체 파이프라인 실행)
```

---

## Google Sheets 데이터 형식

파이프라인의 입력 데이터입니다. 아래 컬럼으로 구성합니다.

| 컬럼 | 예시 | 설명 |
|------|------|------|
| 가게명 | 할매국밥 | 한국어 가게 이름 |
| 지역 | 부산 서면 | 위치 |
| 카테고리 | 국밥 | 음식 종류 |
| 메모 | 현지인만 아는 곳, 새벽 5시 오픈 | 큐레이터 한 줄 메모 (핵심 차별점) |
| 상태 | 대기중 | 대기중 / 생성완료 / 업로드완료 |
| 포스팅 URL | - | 업로드 후 자동 기입 |
| SEO 점수 | - | 평가 후 자동 기입 |
| GEO 점수 | - | 평가 후 자동 기입 |

---

## 실행 방법

### 1. 환경 설정

```bash
pip install -r requirements.txt
```

`.env` 파일 생성:

```env
ANTHROPIC_API_KEY=your_key
KAKAO_API_KEY=your_key
GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json
WORDPRESS_URL=https://bapmap.com
WORDPRESS_USER=your_user
WORDPRESS_APP_PASSWORD=your_app_password
OPENAI_API_KEY=your_key  # SEO/GEO 평가용
```

### 2. 네이버 지도 저장 목록 스크래핑

```bash
python scraper/naver_saved.py
```

브라우저가 열리면 네이버 로그인 후 대기. 자동으로 저장 목록을 수집해 `naver_saved.csv`로 저장합니다.

### 3. 전체 파이프라인 실행

```bash
# 단건 실행 (가게 하나)
python main.py --mode single --name "할매국밥"

# 배치 실행 (Google Sheets 전체 대기중 항목)
python main.py --mode batch --limit 5
```

### 4. SEO/GEO 평가 대시보드

```bash
streamlit run eval/seo_geo_eval.py
```

---

## 콘텐츠 전략

- **초기 (1~2개월)**: 하루 3~5개 포스팅으로 100~300개 빠르게 확보
- **성장 (3개월~)**: 하루 1~2개 유지, SEO 인덱싱 축적
- **수익화 (6개월~)**: 구글 인덱싱 본격화, AdSense + Google Ads 집행

---

## 차별점

일반적인 맛집 추천 사이트와 달리, Bapmap은 **현지인 큐레이터의 관점**이 들어갑니다.
네이버 지도에 저장된 개인 맛집 데이터를 기반으로 하기 때문에 관광객 위주 식당이 아닌,
실제 한국인이 즐겨 찾는 로컬 맛집을 소개합니다.

---

## 로드맵

- [x] SEO/GEO 평가 도구 구현
- [ ] 네이버 지도 저장 목록 스크래퍼
- [ ] Google Sheets 연동
- [ ] 카카오 로컬 API 연동
- [ ] Claude API 포스팅 생성
- [ ] WordPress 자동 업로드
- [ ] Instagram 자동 포스팅
- [ ] Google Ads 성과 리포트
- [ ] 일본어 포스팅 지원
