"""FastAPI application for crawling images"""

import sys
from fastapi import FastAPI, Request, BackgroundTasks, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN
from loguru import logger
from services import do_create_keywords_images, do_create_questions, do_get_questions
from db_config import db_manager
from models import KeywordsRequest

logger.remove()  # 기본 핸들러 제거
logger.add(sys.stderr, level="INFO")

app = FastAPI()
security = HTTPBearer()


def verify_user_token(token: str) -> bool:
    # TODO need to implement
    return token == "user1"


def verify_admin_token(token: str) -> bool:
    return token == "smartagent160321!!"


def verify_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user token
    Args:
        credentials (HTTPAuthorizationCredentials): FastAPI의 사용자 인증 정보
    returns:
        str: 사용자 토큰
    """
    token = credentials.credentials
    if not verify_user_token(token):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid token")
    return token  # 또는 토큰에서 추출한 사용자 정보를 반환할 수 있습니다.


def verify_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin token
    Args:
        credentials (HTTPAuthorizationCredentials): FastAPI의 사용자 인증 정보
    returns:
        str: 어드민 토큰
    """
    token = credentials.credentials
    if not verify_admin_token(token):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid token")
    return token


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


@app.get("/v1/questions")
async def get_questions(token: str = Depends(verify_user)):
    """Get questions"""
    result = await do_get_questions(token)
    return result


@app.on_event("startup")
async def startup_event():
    await db_manager.initialize_database()
