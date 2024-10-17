""" 크롤링한 데이터를 데이터베이스에 삽입하는 서비스 모듈 """

import itertools
import random
from typing import List, Dict
from loguru import logger
from sqlalchemy.orm import Session
from db_schemas import (
    Keyword,
    ImageURL,
    KeywordImageMapping,
    KeywordCombination,
    CombinationImageSet,
    CombinationImageMapping,
)
from crawling import crawl_image_urls_by_keyword
from db_config import session_scope, db_manager


def insert_keywords_and_images(session: Session, keywords: List[str], minimum_images: int = 100) -> dict:
    """
    주어진 키워드 리스트에 대해 이미지를 크롤링하고 데이터베이스에 삽입합니다.

    Args:
        session (Session): SQLAlchemy 세션 객체
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
            keyword_obj = Keyword(keyword=kw)
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


def insert_unique_image_combinations(session: Session, keyword_objects: Dict[str, Keyword]):
    """
    on working
    주어진 키워드 객체들로부터 유일한 이미지 조합을 생성하여 데이터베이스에 삽입합니다.
    각 키워드 조합에 대해 해당 키워드들의 이미지를 조합합니다.

    Args:
        session (Session): SQLAlchemy 세션 객체
        keyword_objects (Dict[str, Keyword]): 키워드 이름을 키로, 키워드 객체를 값으로 갖는 딕셔너리
    """
    total_combinations = 0
    combinations_count = {1: 0, 2: 0, 3: 0}

    # 각 키워드에 대한 이미지 URL 목록을 미리 가져옵니다
    keyword_images = {kw.id: get_keyword_images(session, kw.id) for kw in keyword_objects.values()}

    for r in range(1, 4):
        for combo in itertools.combinations(keyword_objects.values(), r):
            total_combinations += 1
            combinations_count[r] += 1

            kc = KeywordCombination(
                keyword1_id=combo[0].id,
                keyword2_id=combo[1].id if len(combo) > 1 else None,
                keyword3_id=combo[2].id if len(combo) > 2 else None,
            )
            session.add(kc)
            session.flush()

            # 각 키워드의 이미지 목록
            image_lists = [keyword_images[kw.id] for kw in combo]

            # 각 키워드에서 하나의 이미지를 선택하여 조합을 만듭니다
            for image_combo in itertools.product(*image_lists):
                cis = CombinationImageSet(combination_id=kc.id)
                session.add(cis)
                session.flush()

                for i, image in enumerate(image_combo, start=1):
                    cim = CombinationImageMapping(set_id=cis.id, image_url_id=image.id, keyword_order=i)
                    session.add(cim)

            if not image_lists or not all(image_lists):
                logger.warning(f"No images available for some keywords in combination {kc.id}")

    session.commit()

    # 로깅
    logger.info(f"Total keyword combinations created: {total_combinations}")
    for size, count in combinations_count.items():
        logger.info(f"Keyword combinations of size {size}: {count}")


def insert_crawled_data(keywords, minimum_images=100):
    """크롤링한 데이터를 데이터베이스에 삽입하는 함수

    Args:
        session_factory (sessionmaker): SQLAlchemy sessionmaker 객체
        keywords (list): 키워드 리스트
        minimum_images (int): 최소 이미지 수
    """
    session_factory = db_manager.get_session_factory()
    with session_scope(session_factory) as session:
        keyword_objects = insert_keywords_and_images(session, keywords, minimum_images)
        # insert_unique_image_combinations(session, keyword_objects)
