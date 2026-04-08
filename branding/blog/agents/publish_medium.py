import time
import pathlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def _wait_for_login(driver, timeout: int = 60):
    print(f"\n[Medium] 브라우저가 열렸습니다.")
    print(f"[Medium] {timeout}초 안에 Google 로그인을 완료해주세요...")
    # Medium 홈 피드가 뜰 때까지 대기
    for i in range(timeout):
        if "medium.com" in driver.current_url and "/m/signin" not in driver.current_url:
            print("[Medium] 로그인 감지됨!")
            return
        time.sleep(1)
    print("[Medium] 타임아웃 — 로그인 상태로 진행 시도")


def _create_post(driver, title: str, body: str, tags: list[str]) -> str:
    print("[Medium] 새 글 작성 페이지로 이동...")
    driver.get("https://medium.com/new-story")
    time.sleep(5)

    wait = WebDriverWait(driver, 30)
    print(f"[Medium] 현재 URL: {driver.current_url}")

    from selenium.webdriver.common.keys import Keys

    # 제목 입력
    title_el = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "h3[data-testid='editorTitleParagraph']")
    ))
    title_el.click()
    title_el.send_keys(title)
    time.sleep(0.5)

    # 본문 입력
    title_el.send_keys(Keys.RETURN)
    time.sleep(0.5)

    body_el = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "p[data-testid='editorParagraphText']")
    ))
    body_el.click()
    for line in body.split("\n"):
        body_el.send_keys(line)
        body_el.send_keys(Keys.RETURN)
        time.sleep(0.03)

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
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    try:
        print(f"[Medium] 현재 창: {driver.current_url}")
        url = _create_post(driver, title, draft, keywords)
        return {**state, "published_url": url}
    finally:
        pass  # 창 닫지 않음 — 사용자가 직접 확인
