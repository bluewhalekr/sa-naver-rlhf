import json
import random
from typing import List, Optional

from pydantic import BaseModel

from gpt_assistant import GptBatchAssistant, to_user_message

GPT_MODEL = "gpt-4o"
GPT_INPUT_PRICE = 2.5 * 0.000001
GPT_OUTPUT_PRICE = 10 * 0.000001


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


class PersonaGenerator:
    persona_user_prompt = """
    페르소나 하나 만들어줘. 나이는 {age}, 성별은 {sex}, 국가는 대한민국 여야해.
    그 후에 이 사람이 이미지 검색할 만한 키워드 6개 만들어줘
    """.rstrip().lstrip()

    class Persona(BaseModel):
        persona: str

    def __init__(self):
        self.assistant = GptBatchAssistant()

    def execute(self, n: int = 1000):
        age_range_domain = range(15, 65)
        sex_domain = ["남성", "여성"]

        batch_messages = []
        for _ in range(n):
            # 편향된 데이터 생성을 막기 위해 나이와 성별을 랜덤하게 미리 지정
            age = random.choice(age_range_domain)
            sex = random.choice(sex_domain)

            user_message = to_user_message(self.persona_user_prompt.format(age=age, sex=sex))
            messages = [user_message]
            batch_messages.append(messages)

        results = self.assistant.batch_chat(batch_messages, response_format=PersonaAndSearchKeywords)

        persona_keywords_sets = []
        for result in results:
            if content := result.contents[0]:
                json_content = json.loads(content)
                json_content["가격"] = result.prices.input_price + result.prices.output_price
                persona_keywords_sets.append(json_content)

        return persona_keywords_sets


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


class QuestionGenerator:
    def __init__(self):
        self.assistant = GptBatchAssistant()

    def get_instruction_prompt(self, question_type: str):
        if question_type == "SM":
            return """
            이 사람이 GPT를 이용한다면 이 이미지들에 대해 무슨 질문을 할지 10개 턴으로 구성해줘.

            # 조건
            1. 첫번째 턴에 무조건 이미지 하나 첨부해줘.
            2. 그리고 아무 나머지 턴에 이미지를 첨부해줘.
            3. 이미 첨부한 이미지는 중복해서 첨부하면 안 돼.
            4. 추천받은 이미지는 남는 것 없이 모두 첨부해야해.
            """.lstrip().rstrip()
        elif question_type == "MS":
            return """
            이 사람이 GPT를 이용한다면 이 이미지들에 대해 무슨 질문을 할지 10개 턴으로 구성해줘.

            # 조건
            1. 첫번째 턴에 이미지 모두 첨부해줘.
            2. 추천받은 이미지는 남는 것 없이 모두 첨부해야해.
            3. 이후 턴에는 이미지 첨부하지 말아줘.
            """.lstrip().rstrip()
        elif question_type == "MM-1":
            return """
            이 사람이 GPT를 이용한다면 이 이미지들에 대해 무슨 질문을 할지 10개 턴으로 구성해줘.

            # 조건
            1. 첫번째 턴에 무조건 이미지 하나 첨부해줘.
            2. 그리고 다른 하나의 턴에 나머지 이미지 2장 첨부해줘.
            3. 이미 첨부한 이미지는 중복해서 첨부하면 안 돼.
            """.lstrip().rstrip()
        elif question_type == "MM-2":
            return """
            이 사람이 GPT를 이용한다면 이 이미지들에 대해 무슨 질문을 할지 10개 턴으로 구성해줘.

            # 조건
            1. 첫번째 턴에 무조건 이미지 2~3장 첨부해줘.
            2. 그리고 다른 하나의 턴에 나머지 이미지 1~2장 첨부해줘.
            3. 이미 첨부한 이미지는 중복해서 첨부하면 안 돼.
            """.lstrip().rstrip()
        else:
            raise ValueError(f"Invalid question type: {question_type}")

    async def execute(self, persona: str, image_infos: List, question_type: str):
        user_messages = []

        persona_prompt = """다음은 내가 만든 페르소나야.
        ```json
        {persona}
        ```
        """
        if '{persona}' in persona_prompt:
            persona_prompt = persona_prompt.format(persona=persona)

        user_message = to_user_message(persona_prompt)
        user_messages.append(user_message)

        images_prompt = """이 사람이 검색할 만한 이미지 검색어, 이미지는 아래와 같아."""
        user_message = to_user_message(images_prompt)
        user_messages.append(user_message)

        image_prompt_format = "{idx}. 이미지 검색어: {keyword}"
        for image_idx, image_info in enumerate(image_infos, start=1):
            image_prompt = image_prompt_format.format(idx=image_idx, keyword=image_info.keyword)
            image_message = to_user_message(image_prompt, [image_info.image_url])
            user_messages.append(image_message)

        instruction_prompt = self.get_instruction_prompt(question_type)
        user_message = to_user_message(instruction_prompt)
        user_messages.append(user_message)

        response = self.assistant.structured_chat(user_messages, response_format=ImageQueries)
        return response.json()
