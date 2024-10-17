"""데이터베이스 설정"""

import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

USERNAME = "smartagent"
DB_PASSWORD = os.getenv("DB_PASSWORD", "noPassword")
CONNECT_STRING = f"postgresql://{USERNAME}:{DB_PASSWORD}@10.10.5.13:31655/smartagent"


class DatabaseManager:
    """데이터베이스 관리 클래스"""

    def __init__(self):
        self.engine = create_engine(CONNECT_STRING)
        self.SessionFactory = sessionmaker(bind=self.engine)

    def get_engine(self):
        return self.engine

    def get_session_factory(self):
        return self.SessionFactory


@contextmanager
def session_scope(session_factory):
    """Provide a transactional scope around a series of operations."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:  # pylint: disable=broad-except
        session.rollback()
        raise
    finally:
        session.close()


db_manager = DatabaseManager()
