""" 크롤링한 데이터를 데이터베이스에 삽입하는 서비스 모듈 """

import random
from typing import List
from loguru import logger
from tqdm import tqdm
from sqlalchemy import select
from sqlalchemy.orm import Session
from db_schemas import Keyword, ImageURL, KeywordImageMapping, ImageSet, ImageSetMapping
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
        image_urls = crawl_image_urls_by_keyword(category, kw, minimum_images)

        # 이미지 URL 중복 제거
        unique_image_urls = set(image_urls)
        existing_urls = set(
            url for url, in session.query(ImageURL.url).filter(ImageURL.url.in_(unique_image_urls)).all()
        )
        new_urls = [url for url in unique_image_urls if url not in existing_urls]

        for url in tqdm(new_urls):
            image_url_obj = ImageURL(url=url)
            session.add(image_url_obj)
            session.flush()  # image_url_obj.id 사용하기 위해 flush
            mapping = KeywordImageMapping(keyword_id=keyword_obj.id, image_url_id=image_url_obj.id)
            session.add(mapping)

    session.commit()
    logger.info(f"Inserted {len(keywords)} keywords and images")
    return keyword_objects


def create_unique_image_set(session: Session, category: str):
    """특정 카테고리에 대해 이미지 세트를 생성하는 함수

    Args:
        session (Session): SQLAlchemy 세션 객체
        category (str): 카테고리 이름
    """
    logger.info(f"Creating unique image sets for category '{category}'")
    # 1. 특정 카테고리에 해당하는 이미지 URL ID 조회
    image_url_query = (
        select(KeywordImageMapping.image_url_id).join(Keyword).where(Keyword.category == category).distinct()
    )
    image_url_ids = session.scalars(image_url_query).all()

    if not image_url_ids:
        logger.error(f"카테고리 '{category}'에 해당하는 이미지가 없습니다.")
        return

    total_images = len(image_url_ids)
    logger.info(f"총 이미지 수: {total_images}")

    # 2. 이미지 세트 생성
    created_sets = []
    remaining_images = set(image_url_ids)

    while remaining_images:
        # 남은 이미지 수에 따라 가능한 세트 크기 결정
        if len(remaining_images) >= 3:
            possible_sizes = [1, 2, 3]
        elif len(remaining_images) == 2:
            possible_sizes = [1, 2]
        else:
            possible_sizes = [1]

        set_size = random.choice(possible_sizes)

        # 선택된 크기의 세트 생성
        new_set = set(random.sample(list(remaining_images), set_size))
        created_sets.append(new_set)
        remaining_images -= new_set

    # 3. 데이터베이스에 이미지 세트 저장
    for image_set in created_sets:
        new_set = ImageSet()
        session.add(new_set)
        session.flush()

        for image_id in image_set:
            mapping = ImageSetMapping(set_id=new_set.id, image_url_id=image_id)
            session.add(mapping)

    session.commit()
    logger.info(f"총 {len(created_sets)}개의 이미지 세트가 생성되었습니다.")

    # 4. 세트 크기 분포 출력
    size_distribution = {1: 0, 2: 0, 3: 0}
    for s in created_sets:
        size_distribution[len(s)] += 1

    logger.info("세트 크기 분포:")
    for size, count in size_distribution.items():
        logger.info(f"{size}장 세트: {count}개")


def insert_crawled_data(category: str, keywords: List, minimum_images=100):
    """크롤링한 데이터를 데이터베이스에 삽입하는 함수

    Args:
        category (str): 카테고리 이름
        keywords (list): 키워드 리스트
        minimum_images (int): 최소 이미지 수
    """
    session_factory = db_manager.get_session_factory()
    with session_scope(session_factory) as session:
        insert_keywords_and_images(session, category, keywords, minimum_images)
        create_unique_image_set(session, category)
