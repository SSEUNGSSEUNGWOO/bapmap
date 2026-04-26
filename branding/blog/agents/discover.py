import re
import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://www.bluer.co.kr"
POSTED_FILE = Path(__file__).parent.parent / "posted.json"
STATE_FILE = Path(__file__).parent.parent / "discover_state.json"
COOKIES_FILE = Path(__file__).parent.parent / "bluer_cookies.json"

# 서울 + 인천 검색 URL (페이지네이션 포함)
SEARCH_URLS = [
    BASE_URL + "/search?query=&location=%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C&ribbonType=&priceRangeMin=0&priceRangeMax=1000&sort=updatedDate,desc",
    BASE_URL + "/search?query=&location=%EC%9D%B8%EC%B2%9C%EA%B4%91%EC%97%AD%EC%8B%9C&ribbonType=&priceRangeMin=0&priceRangeMax=1000&sort=updatedDate,desc",
]


def _load_posted() -> set:
    if POSTED_FILE.exists():
        data = json.loads(POSTED_FILE.read_text())
        return set(data.get("blueribbon_names", []))
    return set()


def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"page": 0, "url_idx": 0}


def _save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def _get_driver(headless: bool = True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=opts)


def _save_cookies(driver):
    cookies = driver.get_cookies()
    COOKIES_FILE.write_text(json.dumps(cookies, ensure_ascii=False, indent=2))
    print(f"[Discover] 쿠키 저장 완료 ({len(cookies)}개)")


def _load_cookies(driver):
    if not COOKIES_FILE.exists():
        return False
    driver.get(BASE_URL)
    time.sleep(1)
    cookies = json.loads(COOKIES_FILE.read_text())
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception:
            pass
    return True


def login_and_save_cookies():
    """최초 1회 실행: 브라우저 열고 수동 로그인 후 쿠키 저장"""
    print("[Discover] 브라우저를 엽니다. 블루리본에 로그인해주세요...")
    driver = _get_driver(headless=False)
    driver.get(BASE_URL + "/login")

    print("[Discover] 로그인 완료 후 Enter를 눌러주세요...")
    input()

    _save_cookies(driver)
    driver.quit()
    print("[Discover] 로그인 완료. 이후 자동 실행됩니다.")


def _scroll_and_load(driver, scrolls: int = 3):
    for _ in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)


def _parse_spots_from_text(body: str) -> list[dict]:
    """
    블루리본 검색 결과 텍스트 구조:
      식당명
      카테고리
      서울특별시 ... (주소)
      현재 영업중 / 영업 종료
      설명
    """
    lines = [l.strip() for l in body.split('\n') if l.strip()]
    spots = []
    seen = set()

    skip_tokens = {"NEW", "목록형", "지도", "블루리본 맛집만", "내 주변", "브랜드맛집",
                   "통합검색", "식당명 검색", "서울 2026 선정", "이용약관", "개인정보처리방침"}

    for i, line in enumerate(lines):
        # 주소 라인 감지
        if not (line.startswith("서울") or line.startswith("인천")):
            continue
        if len(line) < 10:
            continue

        address = line
        city = "인천" if address.startswith("인천") else "서울"

        # 주소 2줄 위 = 식당명, 1줄 위 = 카테고리
        if i < 2:
            continue
        name = lines[i - 2].strip()
        category_hint = lines[i - 1].strip()

        # 필터링
        if name in skip_tokens or len(name) > 20 or len(name) < 2:
            continue
        if not re.search(r'[가-힣a-zA-Z]', name):
            continue
        if name in seen:
            continue

        seen.add(name)
        spots.append({"name": name, "address_hint": address, "city": city, "category_hint": category_hint})

    return spots


def _scrape_search_page(driver, url: str, scroll_count: int = 0) -> list[dict]:
    if scroll_count == 0:
        driver.get(url)
        time.sleep(4)

    body = driver.find_element(By.TAG_NAME, "body").text

    if "로그인" in body and len(body) < 500:
        raise RuntimeError("쿠키 만료 — 재로그인 필요")

    if "검색결과가 없습니다" in body:
        return []

    # 스크롤로 더 로드
    prev_len = len(body)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text

    return _parse_spots_from_text(body)


def discover(max_spots: int = 20) -> list[dict]:
    if not COOKIES_FILE.exists():
        print("[Discover] 쿠키 없음 — branding/blog/login.py 를 터미널에서 실행해주세요")
        return []

    posted_names = _load_posted()
    state = _load_state()
    url_idx = state.get("url_idx", 0)

    driver = _get_driver(headless=True)
    results = []

    try:
        _load_cookies(driver)

        while url_idx < len(SEARCH_URLS) and len(results) < max_spots:
            url = SEARCH_URLS[url_idx]
            city_name = "서울" if "서울" in url else "인천"
            print(f"[Discover] {city_name} 검색 중...")

            try:
                all_spots = _scrape_search_page(driver, url)
            except RuntimeError as e:
                print(f"[Discover] {e}")
                COOKIES_FILE.unlink(missing_ok=True)
                break

            new_spots = [s for s in all_spots if s["name"] not in posted_names]
            print(f"[Discover] {city_name}: {len(all_spots)}개 중 {len(new_spots)}개 신규")

            for spot in new_spots:
                results.append(spot)
                if len(results) >= max_spots:
                    break

            url_idx += 1

        state["url_idx"] = url_idx % len(SEARCH_URLS)
        _save_state(state)

    finally:
        driver.quit()

    print(f"[Discover] 총 {len(results)}개 발굴")
    return results
