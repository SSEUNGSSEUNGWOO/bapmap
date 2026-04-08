import time
import pathlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def _wait_for_login(driver):
    print("\n[Medium] 브라우저가 열렸습니다.")
    print("[Medium] Google 로그인 후 Medium 홈이 뜨면 엔터를 눌러주세요...")
    input("[Medium] 로그인 완료 후 엔터 ▶ ")


def _create_post(driver, title: str, body: str, tags: list[str]) -> str:
    print("[Medium] 새 글 작성 페이지로 이동...")
    driver.get("https://medium.com/new-story")
    time.sleep(3)

    wait = WebDriverWait(driver, 15)

    # 제목 입력
    title_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3[data-testid='editor-title']")))
    title_el.click()
    title_el.send_keys(title)
    time.sleep(0.5)

    # 본문 클릭 후 입력 (탭으로 이동)
    from selenium.webdriver.common.keys import Keys
    title_el.send_keys(Keys.TAB)
    time.sleep(0.5)

    body_el = driver.switch_to.active_element
    # 마크다운 → 줄 단위로 입력
    for line in body.split("\n"):
        body_el.send_keys(line)
        body_el.send_keys(Keys.RETURN)
        time.sleep(0.05)

    time.sleep(1)

    # 퍼블리시 버튼
    print("[Medium] 퍼블리시 버튼 클릭...")
    publish_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Publish')]")
    ))
    publish_btn.click()
    time.sleep(2)

    # 태그 입력
    try:
        tag_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder*='tag' i], input[placeholder*='topic' i]")
        ))
        for tag in tags[:5]:
            tag_input.send_keys(tag)
            time.sleep(0.5)
            tag_input.send_keys(Keys.RETURN)
            time.sleep(0.3)
    except Exception:
        print("[Medium] 태그 입력 실패, 스킵")

    # 최종 퍼블리시
    try:
        final_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Publish now')]")
        ))
        final_btn.click()
        time.sleep(3)
    except Exception:
        print("[Medium] 최종 퍼블리시 버튼 못 찾음, 수동으로 확인해주세요")

    url = driver.current_url
    print(f"[Medium] 완료: {url}")
    return url


def publish_to_medium(state: dict) -> dict:
    title = state.get("title", "")
    draft = state.get("draft", "")
    keywords = state.get("keywords", [])

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # 봇 감지 우회
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    try:
        driver.get("https://medium.com/m/signin")
        _wait_for_login(driver)
        url = _create_post(driver, title, draft, keywords)
        return {**state, "published_url": url}
    finally:
        input("\n[Medium] 확인 후 엔터를 누르면 브라우저가 닫힙니다...")
        driver.quit()
