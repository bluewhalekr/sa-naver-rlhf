from pydantic import BaseModel
from typing import List, Optional, Literal


class ImageUrlInfo(BaseModel):
    keyword: str
    image_url: str


class ImageQuestion(BaseModel):
    question: str
    image_infos: List[ImageUrlInfo] = []


# ----------------- API 모델 -----------------
class AuthRequestData(BaseModel):
    user_id: str
    token: str


class AuthResponse(BaseModel):
    status: str


class ImageUrlInfosRequestData(BaseModel):
    user_id: str


class ImageUrlInfosResponse(BaseModel):
    persona: str
    image_infos: List[ImageUrlInfo]


class ImageQuestionsRequestData(BaseModel):
    user_id: str
    persona: str
    choices: List[ImageUrlInfo]
    prompt: str


class ImageQuestionsResponse(BaseModel):
    questions: List[ImageQuestion]


# 프롬프트 get 응답 API 모델
class PromptGetResponse(BaseModel):
    prompt: str


# 프롬프트 set 요청 API 모델
class PromptSetRequest(BaseModel):
    prompt: str


# 프롬프트 set 응답 API 모델
class PromptSetResponse(BaseModel):
    status: str
