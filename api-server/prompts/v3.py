""" Prompts for Question Generation(v3) """

from typing import List, Optional

from pydantic import BaseModel

# --- PERSONA GENERATOR --- #
PERSONA_USER_PROMPT = """
페르소나 하나 만들어줘. 나이는 {age}, 성별은 {sex}, 국가는 대한민국 여야해.
그 후에 이 사람이 이미지 검색할 만한 키워드 6개 만들어줘
""".rstrip().lstrip()


# GPT Structure Output Models들은 GPT 응답 성능에 반영되기 때문에 한글 키 사용
class Persona(BaseModel):
    나이: int
    성별: str
    국가: str
    직업: str
    관심사_및_취미: str
    취향: str
    목적: str


class PersonaAndSearchKeywords(BaseModel):
    페르소나: Persona
    이미지_검색_키워드_6개: List[str]


# --- QUESTION GENERATOR --- #
PERSONA_DESCRIPTION_USER_PROMPT = """다음은 내가 만든 페르소나야.
```json
{persona}
```
"""
IMAGES_GUIDE_PROMPT = """이 사람이 검색할 만한 이미지 검색어, 이미지는 아래와 같아."""
IMAGE_TAG_PROMPT = """{idx}. 이미지 검색어: {keyword}"""

SM_TYPE_QUESTION_GEN_USER_PROMPT = """
이 사람이 GPT를 이용한다면 이 이미지들에 대해 무슨 질문을 할지 10개 턴으로 구성해줘.

# 조건
1. 첫번째 턴에 무조건 이미지 하나 첨부해줘.
2. 그리고 아무 나머지 턴에 이미지를 첨부해줘.
3. 이미 첨부한 이미지는 중복해서 첨부하면 안 돼.
4. 추천받은 이미지는 남는 것 없이 모두 첨부해야해.
""".lstrip().rstrip()

MS_TYPE_QUESTION_GEN_USER_PROMPT = """
이 사람이 GPT를 이용한다면 이 이미지들에 대해 무슨 질문을 할지 10개 턴으로 구성해줘.

# 조건
1. 첫번째 턴에 이미지 모두 첨부해줘.
2. 추천받은 이미지는 남는 것 없이 모두 첨부해야해.
3. 이후 턴에는 이미지 첨부하지 말아줘.
""".lstrip().rstrip()

MM_1_TYPE_QUESTION_GEN_USER_PROMPT = """
이 사람이 GPT를 이용한다면 이 이미지들에 대해 무슨 질문을 할지 10개 턴으로 구성해줘.

# 조건
1. 첫번째 턴에 무조건 이미지 하나 첨부해줘.
2. 그리고 다른 하나의 턴에 나머지 이미지 2장 첨부해줘.
3. 이미 첨부한 이미지는 중복해서 첨부하면 안 돼.
""".lstrip().rstrip()

MM_2_TYPE_QUESTION_GEN_USER_PROMPT = """
이 사람이 GPT를 이용한다면 이 이미지들에 대해 무슨 질문을 할지 10개 턴으로 구성해줘.

# 조건
1. 첫번째 턴에 무조건 이미지 2~3장 첨부해줘.
2. 그리고 다른 하나의 턴에 나머지 이미지 1~2장 첨부해줘.
3. 이미 첨부한 이미지는 중복해서 첨부하면 안 돼.
""".lstrip().rstrip()


class ImageQuery(BaseModel):
    사용자_질문: str
    첨부할_이미지의_검색어: List[str]


class ImageQueries(BaseModel):
    첫번째_턴: ImageQuery
    두번째_턴: ImageQuery
    세번째_턴: ImageQuery
    네번째_턴: ImageQuery
    다섯번째_턴: ImageQuery
    여섯번째_턴: ImageQuery
    일곱번째_턴: ImageQuery
    여덟번째_턴: ImageQuery
    아홉번째_턴: ImageQuery
    열번째_턴: ImageQuery