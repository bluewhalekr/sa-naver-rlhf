import os
import json
from typing import List, Optional

import openai
from pydantic import BaseModel

from config import AZURE_ENDPOINT, OPENAI_API_KEY, OPENAI_API_VERSION

GPT_MODEL = "gpt-4o"
GPT_INPUT_PRICE = 5 * 0.000001
GPT_OUTPUT_PRICE = 15 * 0.000001


def to_user_message(text: str, image_urls: Optional[List[str]] = None):
    user_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": text
            },
        ]
    }

    if image_urls:
        for image_url in image_urls:
            user_message["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": "high"
                }
            })

    return user_message


def to_system_message(text):
    system_message = {
        "role": "system",
        "content": text
    }

    return system_message


def to_assistant_message(text: str):
    assistant_message = {
        "role": "assistant",
        "content": text
    }

    return assistant_message


class UserQuestionsAboutImages(BaseModel):
    user_question1: str
    user_question2: str
    user_question3: str
    user_question4: str
    user_question5: str


class GptResponse(BaseModel):
    questions: List[str]
    total_price: float


class QuestionGenerator:
    question_types = ['형태', '연산', '공통점, 차이점', '추천', '형식화 (리스트, 표)', '난이도, 언어', '연관 짓기 (1)', '연관 짓기 (2)']
    one_images_question_types = ['형태', '연산', '추천', '형식화 (리스트, 표)', '난이도, 언어']

    def __init__(self):
        self.openai_client = openai.AzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            api_key=OPENAI_API_KEY,
            api_version=OPENAI_API_VERSION,
        )

    def generate(self, image_urls: List[str]) -> GptResponse:
        instruction_path = os.path.join("prompts", "question_generation_instruction.md")
        with open(instruction_path, "r") as f:
            instruction_prompt = f.read()

        user_prompt = "다음 이미지(들)에 대해서 사용자가 할 만한 질문들을 생성해주세요. 부탁드립니다."

        instruction_message = to_system_message(instruction_prompt)
        user_command_message = to_user_message(user_prompt, image_urls)

        response = self.openai_client.beta.chat.completions.parse(
            model=GPT_MODEL,
            messages=[
                instruction_message,
                user_command_message
            ],
            response_format=UserQuestionsAboutImages
        )

        response_content = response.choices[0].message.content
        input_price = GPT_INPUT_PRICE * response.usage.prompt_tokens
        output_price = GPT_OUTPUT_PRICE * response.usage.completion_tokens

        return GptResponse(
            questions=list(json.loads(response_content).values()),
            total_price=input_price + output_price
        )
