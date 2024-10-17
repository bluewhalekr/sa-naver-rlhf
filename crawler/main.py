"""FastAPI application for crawling images"""

from typing import List
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from services import insert_crawled_data
from db_schemas import initialize_database

app = FastAPI()


class KeywordsRequest(BaseModel):
    """request body for keywords"""

    category: str
    keywords: List[str]


@app.post("/v1/keywords")
async def create_keywords(req: KeywordsRequest, background_tasks: BackgroundTasks):
    """Create keywords and crawl images"""
    # 백그라운드 태스크로 크롤링 및 데이터 삽입 작업 실행
    background_tasks.add_task(insert_crawled_data, req.category, req.keywords)
    return {"message": "Crawling and data insertion started in the background"}


@app.on_event("startup")
async def startup_event():
    initialize_database()
