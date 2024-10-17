"""FastAPI application for crawling images"""

from typing import List
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from services import insert_crawled_data

app = FastAPI()


class KeywordsRequest(BaseModel):
    """request body for keywords"""

    keywords: List[str]


@app.post("/v1/keywords")
async def create_keywords(keywords_request: KeywordsRequest, background_tasks: BackgroundTasks):
    """Create keywords and crawl images"""
    # 백그라운드 태스크로 크롤링 및 데이터 삽입 작업 실행
    background_tasks.add_task(insert_crawled_data, keywords_request.keywords)
    return {"message": "Crawling and data insertion started in the background"}
