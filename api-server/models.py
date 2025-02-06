from typing import List, Optional

from pydantic import BaseModel


class KeywordsRequest(BaseModel):
    """request body for keywords"""

    category: str
    keywords: List[str]


class ImageInfo(BaseModel):
    keyword: str
    image_url: str


class ImageSetResponse(BaseModel):
    image_infos: List[ImageInfo]
    questions: List[str]


class Intent(BaseModel):
    id: Optional[int] = None
    intent: Optional[str] = None
    persona_id: Optional[int] = None
    used_by: Optional[int] = None

    class Config:
        from_attributes = True


class KeywordImageURLSet(BaseModel):
    id: Optional[int] = None
    keyword: Optional[str] = None
    image_url: Optional[str] = None
    intent_id: Optional[int] = None

    class Config:
        from_attributes = True


class Persona(BaseModel):
    id: Optional[int] = None
    persona: Optional[str] = None

    class Config:
        from_attributes = True


class Query(BaseModel):
    id: Optional[int] = None
    query: Optional[str] = None
    keyword_image_url_set_ids: Optional[List[int]] = None
    intent_id: Optional[int] = None

    class Config:
        from_attributes = True


class AuthRequest(BaseModel):
    user_id: str
    token: str

    class Config:
        from_attributes = True


class ImageQuestionsRequest(BaseModel):
    user_id: str
    persona: str
    choices: List[ImageInfo]
    question_type: str

    class Config:
        from_attributes = True
