from pydantic import BaseModel
from typing import List, Optional, Literal


class ImageUrlInfo(BaseModel):
    keyword: str
    image_url: str


class ImageQuestion(BaseModel):
    text: str
    image_infos: List[ImageUrlInfo] = []


# ----------------- API 모델 -----------------
class AuthRequestData(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    status: str


class ImageUrlInfosRequestData(BaseModel):
    username: str


class ImageUrlInfosResponse(BaseModel):
    persona: str
    image_infos: List[ImageUrlInfo]


class ImageQuestionsRequestData(BaseModel):
    username: str
    choices: List[ImageUrlInfo]
    question_type: str


class QuestionWithImageKeywords(BaseModel):
    question: str
    image_keywords: List[str] = []


class ImageQuestionsResponse(BaseModel):
    questions: List[QuestionWithImageKeywords]


# 프롬프트 적용 요청 API 모델
class PromptRequest(BaseModel):
    question_type: Literal["SM", "MS", "MM"]
    prompt: str


# 프롬프트 적용 응답 API 모델
class PromptResponse(BaseModel):
    status: str