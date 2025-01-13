from typing import List

from pydantic import BaseModel, Field


class Persona(BaseModel):
    persona: str


class ImageKeywordSet(BaseModel):
    user_query_intent_about_image: str
    keywords_about_query_image: List[str]


class ImageKeywordSets(BaseModel):
    image_keyword_set1: ImageKeywordSet
    image_keyword_set2: ImageKeywordSet
    image_keyword_set3: ImageKeywordSet
    image_keyword_set4: ImageKeywordSet
    image_keyword_set5: ImageKeywordSet
    image_keyword_set6: ImageKeywordSet
    image_keyword_set7: ImageKeywordSet
    image_keyword_set8: ImageKeywordSet
    image_keyword_set9: ImageKeywordSet
    image_keyword_set10: ImageKeywordSet


class UserQuery(BaseModel):
    image_index_choices: List[int]
    user_query: str


class UserQueries(BaseModel):
    user_query1: UserQuery
    user_query2: UserQuery
    user_query3: UserQuery
    user_query4: UserQuery
    user_query5: UserQuery
