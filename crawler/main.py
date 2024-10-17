"""FastAPI application for crawling images"""

import sys
from typing import List
from fastapi import FastAPI, Request, BackgroundTasks
from loguru import logger
from pydantic import BaseModel
from services import insert_crawled_data
from db_schemas import initialize_database, reset_database

app = FastAPI()

logger.remove()  # 기본 핸들러 제거
logger.add(
    sys.stderr,
    level="INFO",
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


class KeywordsRequest(BaseModel):
    """request body for keywords"""

    category: str
    keywords: List[str]


@app.put("/v1/database/reset")
def reset_database_request():
    """reset database"""
    reset_database()


@app.post("/v1/keywords")
async def create_keywords(req: KeywordsRequest, background_tasks: BackgroundTasks):
    """Create keywords and crawl images"""
    # 백그라운드 태스크로 크롤링 및 데이터 삽입 작업 실행
    background_tasks.add_task(insert_crawled_data, req.category, req.keywords)
    return {"message": "Crawling and data insertion started in the background"}


@app.on_event("startup")
async def startup_event():
    initialize_database()
