""" 크롤링한 데이터를 데이터베이스에 삽입하는 서비스 모듈 """

from typing import List
from loguru import logger
from sqlalchemy.orm import Session
from db_schemas import Keyword, ImageURL, KeywordImageMapping
from crawling import crawl_image_urls_by_keyword
from db_config import session_scope, db_manager


def insert_keywords_and_images(session: Session, category: str, keywords: List[str], minimum_images: int = 100) -> dict:
    """
    주어진 키워드 리스트에 대해 이미지를 크롤링하고 데이터베이스에 삽입합니다.

    Args:
        session (Session): SQLAlchemy 세션 객체
        category (str): 카테고리 이름
        keywords (list): 키워드 리스트
        minimum_images (int): 최소 이미지 수

    Returns:
        dict: 키워드 이름을 키로, 키워드 객체를 값으로 갖는 딕셔너리
    """
    keyword_objects = {}

    for kw in keywords:
        # 키워드 객체 생성 또는 조회
        keyword_obj = session.query(Keyword).filter_by(keyword=kw).first()
        if not keyword_obj:
            keyword_obj = Keyword(keyword=kw, category=category)
            session.add(keyword_obj)
            session.flush()
        keyword_objects[kw] = keyword_obj

        # 이미지 URL 크롤링
        image_urls = crawl_image_urls_by_keyword(kw, minimum_images)

        for url in image_urls:
            # 이미지 URL 객체 생성 또는 조회
            image_url_obj = session.query(ImageURL).filter_by(url=url).first()
            if not image_url_obj:
                image_url_obj = ImageURL(url=url)
                session.add(image_url_obj)
                session.flush()

            # KeywordImageMapping 생성
            mapping = KeywordImageMapping(keyword_id=keyword_obj.id, image_url_id=image_url_obj.id)
            session.add(mapping)

    session.commit()
    logger.info(f"Inserted {len(keywords)} keywords and images")
    return keyword_objects


def get_keyword_images(session: Session, keyword_id: int) -> List[ImageURL]:
    """특정 키워드에 대한 모든 이미지 URL을 가져옵니다."""
    return session.query(ImageURL).join(KeywordImageMapping).filter(KeywordImageMapping.keyword_id == keyword_id).all()


def insert_crawled_data(category: str, keywords: List, minimum_images=100):
    """크롤링한 데이터를 데이터베이스에 삽입하는 함수

    Args:
        category (str): 카테고리 이름
        keywords (list): 키워드 리스트
        minimum_images (int): 최소 이미지 수
    """
    session_factory = db_manager.get_session_factory()
    with session_scope(session_factory) as session:
        keyword_objects = insert_keywords_and_images(session, category, keywords, minimum_images)
        for keyword, image_urls in keyword_objects.items():
            logger.info(f"Inserted {len(image_urls)} images for keyword {keyword}")
