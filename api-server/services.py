""" 크롤링한 데이터를 데이터베이스에 삽입하는 서비스 모듈 """

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
import random
import time
from typing import List
from loguru import logger
from tqdm.asyncio import tqdm
from sqlalchemy import select, func, update, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from crawling import crawl_image_urls_by_keyword
from db_config import (
    async_session_scope,
    db_manager,
    Keyword,
    ImageURL,
    KeywordImageMapping,
    ImageSet,
    ImageSetMapping,
    Question,
)
from question_generator import q_generator, GptResponse
from config import QUESTION_COUNT_BUFFER

# 전역 ThreadPoolExecutor 생성
thread_pool = ThreadPoolExecutor()


async def insert_keywords_and_images(
    session: AsyncSession, category: str, keywords: List[str], minimum_images: int = 100
):
    """
    주어진 키워드 리스트에 대해 이미지를 크롤링하고 데이터베이스에 삽입합니다.

    Args:
        session (AsyncSession): SQLAlchemy 비동기 세션 객체
        category (str): 카테고리 이름
        keywords (list): 키워드 리스트
        minimum_images (int): 최소 이미지 수

    Returns:
        dict: 키워드 이름을 키로, 키워드 객체를 값으로 갖는 딕셔너리
    """
    # category insert

    search_words = [category] + keywords
    for word in keywords:
        search_words.append(f"{category} {word}")
    logger.info(f"Inserting {len(keywords)} keywords and images for category '{category}'")
    # keyword insert
    for kw in tqdm(search_words):
        # 키워드 객체 생성 또는 조회
        stmt = select(Keyword).where(Keyword.keyword == kw)
        result = await session.execute(stmt)
        keyword_obj = result.scalar_one_or_none()
        if not keyword_obj:
            keyword_obj = Keyword(keyword=kw, category=category)
            session.add(keyword_obj)
            await session.flush()

        # 이미지 URL 크롤링
        image_urls = await crawl_image_urls_by_keyword(kw, minimum_images)

        # 이미지 URL 중복 제거
        unique_image_urls = set(image_urls)

        # 기존 URL 조회
        stmt = select(ImageURL.url).where(ImageURL.url.in_(unique_image_urls))
        result = await session.execute(stmt)
        existing_urls = set(row[0] for row in result)

        new_urls = [url for url in unique_image_urls if url not in existing_urls]

        for url in tqdm(new_urls):
            image_url_obj = ImageURL(url=url)
            session.add(image_url_obj)
            await session.flush()  # image_url_obj.id 사용하기 위해 flush

            mapping = KeywordImageMapping(keyword_id=keyword_obj.id, image_url_id=image_url_obj.id)
            session.add(mapping)

    await session.commit()
    logger.info(f"Inserted {len(keywords)} keywords and images")


async def create_unique_image_set(session: AsyncSession, category: str):
    """특정 카테고리에 대해 비동기적으로 이미지 세트를 생성하는 함수

    Args:
        session (AsyncSession): SQLAlchemy 비동기 세션 객체
        category (str): 카테고리 이름
    """
    logger.info(f"Creating unique image sets for category '{category}'")

    async with session.begin():
        # 1. 특정 카테고리에 해당하는 이미지 URL ID 조회
        image_url_query = (
            select(KeywordImageMapping.image_url_id).join(Keyword).where(Keyword.category == category).distinct()
        )
        result = await session.execute(image_url_query)
        image_url_ids = result.scalars().all()

        if not image_url_ids:
            logger.error(f"카테고리 '{category}'에 해당하는 이미지가 없습니다.")
            return

        total_images = len(image_url_ids)
        logger.info(f"총 이미지 수: {total_images}")

        # 2. 이미지 세트 생성
        created_sets = []
        remaining_images = set(image_url_ids)
        while remaining_images:
            if len(remaining_images) >= 3:
                possible_sizes = [1, 2, 3]
            elif len(remaining_images) == 2:
                possible_sizes = [1, 2]
            else:
                possible_sizes = [1]
            set_size = random.choice(possible_sizes)
            new_set = set(random.sample(list(remaining_images), set_size))
            created_sets.append(new_set)
            remaining_images -= new_set

        # 3. 데이터베이스에 이미지 세트 저장
        for image_set in created_sets:
            new_set = ImageSet()
            session.add(new_set)
            await session.flush()
            for image_id in image_set:
                mapping = ImageSetMapping(set_id=new_set.id, image_url_id=image_id)
                session.add(mapping)

        await session.commit()

    logger.info(f"총 {len(created_sets)}개의 이미지 세트가 생성되었습니다.")

    # 4. 세트 크기 분포 출력
    size_distribution = {1: 0, 2: 0, 3: 0}
    for s in created_sets:
        size_distribution[len(s)] += 1
    logger.info("세트 크기 분포:")
    for size, count in size_distribution.items():
        logger.info(f"{size}장 세트: {count}개")


async def do_create_keywords_images(category: str, keywords: List, minimum_images=100):
    """키워드를 입력받아서 네이버 검색에서 이미지를 크롤링하고 데이터베이스에 삽입하는 함수

    Args:
        category (str): 카테고리 이름
        keywords (list): 키워드 리스수
        minimum_images (int): 최소 이미지 수
    """
    session_factory = db_manager.get_session_factory()
    async with async_session_scope(session_factory) as session:
        await insert_keywords_and_images(session, category, keywords, minimum_images)
        await create_unique_image_set(session, category)


async def async_question_generate(urls: List[str]) -> GptResponse:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_pool, q_generator.generate, urls)


async def do_create_questions(batch_size: int = 5):
    logger.info(f"Starting do_create_questions with batch size {batch_size}")
    session_factory = db_manager.get_session_factory()
    try:
        async with async_session_scope(session_factory) as session:
            try:
                target_image_sets = await fetch_unmapped_image_sets(session, batch_size)
                logger.info(f"Fetched {len(target_image_sets)} unmapped image sets")

                for image_set in target_image_sets:
                    try:
                        logger.info(f"Generating questions for {len(image_set['urls'])} images")
                        questions = await async_question_generate(image_set["urls"])
                        new_question = Question(
                            image_set_id=image_set["image_set"],
                            questions=questions.questions,
                            cost=questions.total_price,
                            created_dt=time.time(),
                        )
                        logger.info(f"Generated questions for image set {image_set['image_set']}: {questions}")
                        session.add(new_question)
                    except Exception as e:  # pylint: disable=broad-except
                        logger.error(f"Error processing image set {image_set['image_set']}: {str(e)}")
                        # TODO: 이미지 세트의 처리를 건너뛰고 다음으로 진행
                        continue

                await session.commit()
                logger.success(f"Successfully created questions for {len(target_image_sets)} image sets")

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred: {str(e)}")
                await session.rollback()
                raise

    except Exception as e:
        logger.error(f"Unexpected error in do_create_questions: {str(e)}")
        raise


async def fetch_unmapped_image_sets(session: AsyncSession, batch_size: int):
    try:
        async with session.begin():
            logger.info("fetch_unmapped_image_sets")
            used_image_set_count = select(func.count(Question.image_set_id.distinct()))
            total_image_set_count = select(func.count(ImageSet.id))

            used_count = await session.scalar(used_image_set_count)
            total_count = await session.scalar(total_image_set_count)

            logger.info(f"Used ImageSets: {used_count}, Total ImageSets: {total_count}")

            if total_count - used_count < batch_size:
                logger.warning("Warning: Very few unmapped ImageSets available")

            used_image_set_ids = select(Question.image_set_id).distinct()

            unmapped_image_sets = (
                select(ImageSet.id)
                .where(~ImageSet.id.in_(used_image_set_ids))
                .order_by(func.random())
                .limit(batch_size)
            )

            result = await session.execute(unmapped_image_sets)
            image_set_ids = result.scalars().all()
            logger.info(f"Found {len(image_set_ids)} unmapped ImageSets")

            # 3. 관계 데이터 별도 로딩
            if image_set_ids:
                image_sets_with_mappings = (
                    select(ImageSet)
                    .options(selectinload(ImageSet.image_set_mappings).selectinload(ImageSetMapping.image_url))
                    .where(ImageSet.id.in_(image_set_ids))
                )

                logger.info("Loading related data...")
                result = await session.execute(image_sets_with_mappings)
                image_sets = result.scalars().all()

                image_sets_with_urls = [
                    {
                        "image_set": image_set.id,
                        "urls": [mapping.image_url.url for mapping in image_set.image_set_mappings],
                    }
                    for image_set in image_sets
                ]

                return image_sets_with_urls
            return []
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise


async def do_get_questions(image_count: int, token: str = "kb"):
    session_factory = db_manager.get_session_factory()
    try:
        async with async_session_scope(session_factory) as session:
            try:
                result = await get_unused_image_set_info(session, image_count, token)
                logger.info(result)
                if result:
                    return result
                return {"message": "No unused image set available"}

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred: {str(e)}")
                await session.rollback()
                raise

    except Exception as e:
        logger.error(f"Unexpected error in do_get_questions: {str(e)}")
        raise


async def get_unused_image_set_info(session: AsyncSession, image_count: int = 0, token: str = "kb"):
    """사용되지 않은 이미지 세트 정보를 반환하는 함수

    Args:
        session (AsyncSession): SQLAlchemy 비동기 세션 객체
        image_count (int): 이미지 수
        token (str): 사용자 토큰

    Returns:
        dict: 이미지 세트 정보
    """
    async with session.begin():
        try:
            # 1. used_by가 없는 Question 레코드 하나를 무작위로 선택
            if image_count not in [0, 1, 2, 3]:
                raise ValueError("image_count must be 1, 2, or 3, 0")

            if image_count == 0:
                image_count = random.choice([1, 2, 3])
            # 서브쿼리: 각 이미지 세트의 이미지 수 계산

            image_count_subq = (
                select(ImageSetMapping.set_id, func.count().label("image_count"))
                .group_by(ImageSetMapping.set_id)
                .subquery()
            )

            subquery = (
                select(Question.id)
                .join(image_count_subq, Question.image_set_id == image_count_subq.c.set_id)
                .where(and_(Question.used_by == None, image_count_subq.c.image_count == image_count))
                .order_by(func.random())
                .limit(1)
                .scalar_subquery()
            )

            # 선택된 question을 업데이트하고 반환
            update_stmt = (
                update(Question)
                .where(Question.id == subquery)
                .values(used_by=token, updated_dt=time.time())
                .returning(Question)
            )
            result = await session.execute(update_stmt)
            unused_question = result.scalar_one_or_none()

            if not unused_question:
                # TODO 질문 생성 트리거 요청
                return None

            # 2. 선택된 Question의 image_set_id를 사용하여 관련 이미지와 키워드 조회
            image_info_query = (
                select(Keyword.keyword, ImageURL.url)
                .select_from(ImageSetMapping)
                .join(ImageSet, ImageSet.id == ImageSetMapping.set_id)
                .join(ImageURL, ImageURL.id == ImageSetMapping.image_url_id)
                .join(KeywordImageMapping, KeywordImageMapping.image_url_id == ImageURL.id)
                .join(Keyword, Keyword.id == KeywordImageMapping.keyword_id)
                .where(ImageSet.id == unused_question.image_set_id)
            )

            result = await session.execute(image_info_query)
            image_info_result = result.fetchall()

            # 3. 결과를 요청된 형식으로 구성
            image_info = [{"keyword": row.keyword, "image_url": row.url} for row in image_info_result]
            questions = unused_question.questions
            result = {"image_info": image_info, "questions": questions}

            return result
        except SQLAlchemyError as e:
            await session.rollback()
            raise e


def get_keyword_from_file(file_path: str):
    # JSON 파일 읽기
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    all_keywords = []
    for category in ["1", "2", "3"]:
        if category in data:
            all_keywords.extend(data[category])

    return {"category": data["query"], "keywords": all_keywords}


async def do_create_batch_questions():
    """
    Question 테이블을 확인하고 필요한 경우 질문을 생성하는 함수
      - QUESTION_COUNT_BUFFER 이하로 남아있을 경우 질문 생성
    """
    session_factory = db_manager.get_session_factory()
    async with async_session_scope(session_factory) as session:
        # used_by가 비어있는 질문의 수를 카운트
        query = select(func.count()).select_from(Question).where(Question.used_by.is_(None))
        result = await session.execute(query)
        unused_count = result.scalar()

        if unused_count <= QUESTION_COUNT_BUFFER:
            logger.warning(f"Creating questions! Current unused count: {unused_count}")
            await do_create_questions()
        else:
            print(f"Skipping question creation! Current unused count: {unused_count}. Good!")
