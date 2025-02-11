"""FastAPI application for crawling images"""

import sys

from fastapi import BackgroundTasks, Depends, FastAPI, Request, HTTPException
from loguru import logger
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from auth import verify_admin_user, verify_user
from db_config import db_manager
from errors import GptAssistantResponseError, NoAvailablePersonaImageInfoError
from models import KeywordsRequest, AuthRequest, ImageQuestionsRequest, PromptSetRequest
from services import (
    do_create_batch_questions,
    do_create_keywords_images,
    do_get_questions,
    do_get_questions_v2,
    do_auth_user,
    do_get_persona_image_infos,
    generate_and_get_image_questions,
)

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
    req: KeywordsRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_admin_user),
):
    """Create keywords and crawl images"""
    # 백그라운드 태스크로 크롤링 및 데이터 삽입 작업 실행
    background_tasks.add_task(do_create_keywords_images, req.category, req.keywords)
    return {"message": "Crawling and data insertion started in the background"}


@app.post("/v1/questions")
async def create_questions(
    background_tasks: BackgroundTasks, token: str = Depends(verify_admin_user)
):
    """Create questions"""
    # background_tasks.add_task(do_create_questions)
    return {"message": "create_questionsstarted in the background"}


@app.post("/v1/batch/questions")
async def create_batch_questions(
    background_tasks: BackgroundTasks, token: str = Depends(verify_admin_user)
):
    """Create questions"""
    background_tasks.add_task(do_create_batch_questions)
    return {"message": "create_questionsstarted in the background"}


@app.get("/v1/questions")
async def get_questions(image_count: int = 0, token: str = Depends(verify_user)):
    """Get questions"""
    result = await do_get_questions(image_count, token)
    return result


@app.get("/v2/questions")
async def get_questions_v2(token: str = Depends(verify_user)):
    """Get questions"""
    result = await do_get_questions_v2(token)
    return result


@app.post("/v3/auth")
async def auth_user(req: AuthRequest):
    """Authenticate user"""
    result = await do_auth_user(req.user_id, req.token)
    return result


@app.get("/v3/persona-image-infos")
async def get_persona_image_infos(user_id: str):
    """Get persona image infos"""
    try:
        result = await do_get_persona_image_infos(user_id)
    except NoAvailablePersonaImageInfoError as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NoAvailablePersonaImageInfoError: {e}"
        )
    return result


@app.post("/v3/image-questions")
async def generate_image_questions(req: ImageQuestionsRequest):
    """Generate image questions"""
    try:
        result = await generate_and_get_image_questions(
            req.user_id,
            req.persona,
            req.choices,
            req.prompt
        )
    except GptAssistantResponseError as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GPT Assistant response error: {e}"
        )
    return result


@app.on_event("startup")
async def startup_event():
    await db_manager.initialize_database()
