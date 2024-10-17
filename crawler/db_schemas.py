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
    category = Column(String, unique=True, nullable=False)


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


class ImageSet(Base):
    """이미지 세트 테이블"""

    __tablename__ = "image_sets"
    id = Column(Integer, primary_key=True)


class ImageSetMapping(Base):
    """이미지 세트 매핑 테이블"""

    __tablename__ = "image_set_mapping"
    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey("image_sets.id"), nullable=False)
    image_url_id = Column(Integer, ForeignKey("image_urls.id"), nullable=False)
    order = Column(Integer, CheckConstraint("order BETWEEN 1 AND 3"), nullable=False)
    image_set = relationship("ImageSet")
    image_url = relationship("ImageURL")
    __table_args__ = (UniqueConstraint("set_id", "order"),)


class Question(Base):
    """질문 테이블"""

    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    image_set_id = Column(Integer, ForeignKey("image_sets.id"), nullable=False)
    question = Column(String, nullable=False)
    question_type = Column(String(20), nullable=False)
    image_set = relationship("ImageSet")
    __table_args__ = (
        CheckConstraint(
            "question_type IN ('SINGLE_IMAGE', 'MULTIPLE_IMAGES', 'FIRST_IMAGE', 'SECOND_IMAGE', 'THIRD_IMAGE')"
        ),
    )


def reset_database():
    """데이터베이스 초기화: 모든 테이블 삭제 후 재생성"""
    engine = db_manager.get_engine()

    # 모든 테이블 삭제
    Base.metadata.drop_all(engine)
    print("All existing tables have been dropped.")

    # 새 테이블 생성
    Base.metadata.create_all(engine)
    print("New tables have been created.")


def initialize_database():
    """데이터베이스 스키마 초기화"""
    engine = db_manager.get_engine()
    Base.metadata.create_all(engine)
