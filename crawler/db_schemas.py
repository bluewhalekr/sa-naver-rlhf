""" initialize database schema """

from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from db_config import db_manager


Base = declarative_base()


class Keyword(Base):
    """키워드 테이블"""

    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    keyword = Column(String, unique=True, nullable=False)


class ImageURL(Base):
    """이미지 URL 테이블"""

    __tablename__ = "image_urls"

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)


class KeywordImageMapping(Base):
    """키워드-이미지 매핑 테이블"""

    __tablename__ = "keyword_image_mapping"

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    image_url_id = Column(Integer, ForeignKey("image_urls.id"), nullable=False)

    keyword = relationship("Keyword")
    image_url = relationship("ImageURL")

    __table_args__ = (UniqueConstraint("keyword_id", "image_url_id"),)


class KeywordCombination(Base):
    """키워드 조합 테이블"""

    __tablename__ = "keyword_combinations"

    id = Column(Integer, primary_key=True)
    keyword1_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    keyword2_id = Column(Integer, ForeignKey("keywords.id"))
    keyword3_id = Column(Integer, ForeignKey("keywords.id"))

    keyword1 = relationship("Keyword", foreign_keys=[keyword1_id])
    keyword2 = relationship("Keyword", foreign_keys=[keyword2_id])
    keyword3 = relationship("Keyword", foreign_keys=[keyword3_id])

    __table_args__ = (
        CheckConstraint(
            "(keyword2_id IS NULL AND keyword3_id IS NULL) OR "
            "(keyword2_id IS NOT NULL AND keyword3_id IS NULL) OR "
            "(keyword2_id IS NOT NULL AND keyword3_id IS NOT NULL)"
        ),
        UniqueConstraint("keyword1_id", "keyword2_id", "keyword3_id"),
    )


class CombinationImageSet(Base):
    """조합 이미지 세트 테이블"""

    __tablename__ = "combination_image_sets"

    id = Column(Integer, primary_key=True)
    combination_id = Column(Integer, ForeignKey("keyword_combinations.id"), nullable=False)

    combination = relationship("KeywordCombination")


class CombinationImageMapping(Base):
    """조합 이미지 매핑 테이블"""

    __tablename__ = "combination_image_mapping"

    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey("combination_image_sets.id"), nullable=False)
    image_url_id = Column(Integer, ForeignKey("image_urls.id"), nullable=False)
    keyword_order = Column(Integer, CheckConstraint("keyword_order BETWEEN 1 AND 3"), nullable=False)

    image_set = relationship("CombinationImageSet")
    image_url = relationship("ImageURL")

    __table_args__ = (UniqueConstraint("set_id", "keyword_order"),)


class Question(Base):
    """질문 테이블"""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    combination_set_id = Column(Integer, ForeignKey("combination_image_sets.id"), nullable=False)
    question = Column(String, nullable=False)
    question_type = Column(String(20), nullable=False)

    combination_set = relationship("CombinationImageSet")

    __table_args__ = (
        CheckConstraint(
            "question_type IN ('SINGLE_IMAGE', 'MULTIPLE_IMAGES', 'FIRST_IMAGE', 'SECOND_IMAGE', 'THIRD_IMAGE')"
        ),
    )


def initialize_database():
    """데이터베이스 스키마 초기화"""
    engine = db_manager.get_engine()
    Base.metadata.create_all(engine)
