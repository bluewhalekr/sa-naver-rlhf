from typing import List
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
