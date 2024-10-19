"""데이터베이스 설정"""

import json
from contextlib import asynccontextmanager
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, UniqueConstraint, Float, ARRAY
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import CONNECT_STRING

Base = declarative_base()


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(Float)
    expires_at = Column(Float)
    user_id = Column(String)
    scopes = Column(ARRAY(String))


class Keyword(Base):
    """키워드 테이블"""

    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True)
    keyword = Column(String, unique=True, nullable=False)
    category = Column(String, unique=False, nullable=False)


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
    image_set_mappings = relationship("ImageSetMapping", back_populates="image_set")


class ImageSetMapping(Base):
    """이미지 세트 매핑 테이블"""

    __tablename__ = "image_set_mapping"
    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey("image_sets.id"), nullable=False)
    image_url_id = Column(Integer, ForeignKey("image_urls.id"), nullable=False)
    image_set = relationship("ImageSet", back_populates="image_set_mappings")
    image_url = relationship("ImageURL")
    __table_args__ = (UniqueConstraint("set_id", "image_url_id"),)


class Question(Base):
    """질문 테이블"""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    image_set_id = Column(Integer, ForeignKey("image_sets.id"), nullable=False)
    questions = Column(JSON, nullable=False)  # List of questions stored as JSON
    cost = Column(Float, nullable=True)
    image_set = relationship("ImageSet")
    created_dt = Column(Float, nullable=False)
    updated_dt = Column(Float, nullable=False)
    used_by = Column(String, nullable=True)

    def __repr__(self):
        return f"<Question(id={self.id}, image_set_id={self.image_set_id}, questions={self.questions})>"


class AsyncDatabaseManager:
    """비동기 데이터베이스 관리 클래스"""

    def __init__(self, connect_string):
        self.engine = create_async_engine(
            connect_string,
            echo=False,
            json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
            json_deserializer=lambda obj: json.loads(obj),
            connect_args={"command_timeout": 60, "server_settings": {"client_encoding": "utf8"}},
        )
        self.SessionFactory = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    def get_engine(self):
        return self.engine

    def get_session_factory(self):
        return self.SessionFactory

    async def initialize_database(self):
        """데이터베이스 스키마 비동기 초기화"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self.engine.dispose()


@asynccontextmanager
async def async_session_scope(session_factory):
    """비동기 트랜잭션 범위를 제공하는 컨텍스트 매니저"""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


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


db_manager = AsyncDatabaseManager(CONNECT_STRING)
