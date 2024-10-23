"""FastAPI application for crawling images"""

import sys
from fastapi import FastAPI, Request, BackgroundTasks, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN
from loguru import logger
from services import do_create_keywords_images, do_create_questions, do_get_questions, do_create_batch_questions
from db_config import db_manager
from config import SCHEDULER_INTERVAL
from models import KeywordsRequest
from auth import verify_user, verify_admin_user

logger.remove()  # 기본 핸들러 제거
logger.add(sys.stderr, level="INFO")

app = FastAPI()


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


@app.post("/v1/keywords")
async def create_keywords_images(
    req: KeywordsRequest, background_tasks: BackgroundTasks, token: str = Depends(verify_admin_user)
):
    """Create keywords and crawl images"""
    # 백그라운드 태스크로 크롤링 및 데이터 삽입 작업 실행
    background_tasks.add_task(do_create_keywords_images, req.category, req.keywords)
    return {"message": "Crawling and data insertion started in the background"}


@app.post("/v1/questions")
async def create_questions(background_tasks: BackgroundTasks, token: str = Depends(verify_admin_user)):
    """Create questions"""
    background_tasks.add_task(do_create_questions)
    return {"message": "create_questionsstarted in the background"}


@app.post("/v1/batch/questions")
async def create_batch_questions(background_tasks: BackgroundTasks, token: str = Depends(verify_admin_user)):
    """Create questions"""
    background_tasks.add_task(do_create_batch_questions)
    return {"message": "create_questionsstarted in the background"}


@app.get("/v1/questions")
async def get_questions(image_count: int = 0, token: str = Depends(verify_user)):
    """Get questions"""
    result = await do_get_questions(image_count, token)
    return result


@app.on_event("startup")
async def startup_event():
    await db_manager.initialize_database()
