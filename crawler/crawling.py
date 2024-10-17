"""네이버 이미지 검색 결과를 크롤링하는 모듈"""

import time
import random
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


MAX_CRAWL_TRIALS = 5  # 최대 크롤링 시도 횟수
TARGET_URL_PREFIX = "https://search.pstatic.net/common/?src="


class CustomUserAgentSelector:
    """랜덤한 User-Agent를 선택하는 클래스"""

    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
        ]

    def random(self):
        """랜덤한 User-Agent를 반환"""
        return random.choice(self.user_agents)


def scroll_page(driver, scroll_pause_time=2.0, num_scrolls=5):
    """페이지를 스크롤하는 함수, 스크롤 페이징이 적용된 페이지에서 사용

    Args:
        driver (WebDriver): Selenium WebDriver 객체
        scroll_pause_time (float): 스크롤 후 대기 시간
        num_scrolls (int): 스크롤 횟수
    """
    for _ in range(num_scrolls):
        # 현재 스크롤 높이 가져오기
        last_height = driver.execute_script("return document.body.scrollHeight")

        # 랜덤한 거리만큼 스크롤 다운
        scroll_distance = random.randint(300, last_height)
        driver.execute_script(f"window.scrollTo(0, {scroll_distance});")

        # 대기
        time.sleep(scroll_pause_time)

        # 스크롤 후 새로운 높이
        new_height = driver.execute_script("return document.body.scrollHeight")

        # 더 이상 스크롤할 수 없으면 종료
        if new_height == last_height:
            break

        # 랜덤한 시간 동안 대기
        time.sleep(random.uniform(0.5, 2.5))


def crawl_image_urls_by_keyword(keyword, minimum_images=100):
    """키워드로 네이버 이미지 검색 결과를 크롤링하는 함수

    Args:
        keyword (str): 이미지 검색 키워드
        minimum_images (int): 최소 크롤링 이미지 수
    Returns:
        list: 이미지 URL 리스트
    """
    ua_selector = CustomUserAgentSelector()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent={ua_selector.random()}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    image_urls = []
    trials = 0
    try:
        url = f"https://search.naver.com/search.naver?where=image&query={keyword}"
        driver.get(url)

        # 페이지 로딩 대기
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "image_tile_bx")))

        while len(image_urls) < minimum_images and trials < MAX_CRAWL_TRIALS:
            # 스크롤 수행
            scroll_page(driver, scroll_pause_time=random.uniform(1.0, 3.0), num_scrolls=5)

            # 추가 대기 시간
            time.sleep(random.uniform(2, 4))

            soup = BeautifulSoup(driver.page_source, "html.parser")
            images = soup.select(".image_tile_bx img")
            image_urls = [
                img["src"] for img in images if "src" in img.attrs and img["src"].startswith(TARGET_URL_PREFIX)
            ]
            trials += 1
            logger.info(f"Crawling {keyword} image url: Trial {trials}: Found {len(image_urls)} images")
        return image_urls
    finally:
        driver.quit()
