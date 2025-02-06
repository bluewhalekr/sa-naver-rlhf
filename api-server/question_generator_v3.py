import json
import random
from typing import List

from gpt_assistant import GptBatchAssistant, to_user_message
from prompts.v3 import PERSONA_USER_PROMPT, PersonaAndSearchKeywords, \
    PERSONA_DESCRIPTION_USER_PROMPT, IMAGES_GUIDE_PROMPT, IMAGE_TAG_PROMPT, \
    SM_TYPE_QUESTION_GEN_USER_PROMPT, MS_TYPE_QUESTION_GEN_USER_PROMPT, MM_1_TYPE_QUESTION_GEN_USER_PROMPT, \
    MM_2_TYPE_QUESTION_GEN_USER_PROMPT, ImageQueries

GPT_MODEL = "gpt-4o"
GPT_INPUT_PRICE = 2.5 * 0.000001
GPT_OUTPUT_PRICE = 10 * 0.000001


class PersonaGenerator:
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

            user_message = to_user_message(PERSONA_USER_PROMPT.format(age=age, sex=sex))
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


class QuestionGenerator:
    def __init__(self):
        self.assistant = GptBatchAssistant()

    def get_instruction_prompt(self, question_type: str):
        if question_type == "SM":
            return SM_TYPE_QUESTION_GEN_USER_PROMPT
        elif question_type == "MS":
            return MS_TYPE_QUESTION_GEN_USER_PROMPT
        elif question_type == "MM-1":
            return MM_1_TYPE_QUESTION_GEN_USER_PROMPT
        elif question_type == "MM-2":
            return MM_2_TYPE_QUESTION_GEN_USER_PROMPT
        else:
            raise ValueError(f"Invalid question type: {question_type}")

    async def execute(self, persona: str, image_infos: List, question_type: str):
        user_messages = []

        persona_prompt = PERSONA_DESCRIPTION_USER_PROMPT
        if '{persona}' in persona_prompt:
            persona_prompt = persona_prompt.format(persona=persona)

        user_message = to_user_message(persona_prompt)
        user_messages.append(user_message)

        user_message = to_user_message(IMAGES_GUIDE_PROMPT)
        user_messages.append(user_message)

        for image_idx, image_info in enumerate(image_infos, start=1):
            image_prompt = IMAGE_TAG_PROMPT.format(idx=image_idx, keyword=image_info.keyword)
            image_message = to_user_message(image_prompt, [image_info.image_url])
            user_messages.append(image_message)

        instruction_prompt = self.get_instruction_prompt(question_type)
        user_message = to_user_message(instruction_prompt)
        user_messages.append(user_message)

        response = self.assistant.structured_chat(user_messages, response_format=ImageQueries)
        return response.json()
