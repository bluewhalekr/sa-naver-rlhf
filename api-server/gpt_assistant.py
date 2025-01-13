import openai
from openai.types import CompletionUsage
import json
import time
from tempfile import TemporaryDirectory
from typing import List, Optional

import openai
from openai.types import CompletionUsage
from pydantic import BaseModel

from config import AZURE_ENDPOINT, OPENAI_API_KEY, OPENAI_API_VERSION

GPT_MODEL = "gpt-4o"
GPT_INPUT_PRICE = 1.25 * 0.000001
GPT_OUTPUT_PRICE = 10 * 0.000001

GPT_BATCH_MODEL = "gpt-4o-batch"
GPT_BATCH_INPUT_PRICE = 1.25 * 0.000001
GPT_BATCH_OUTPUT_PRICE = 10 * 0.000001


class AssistantPrice(BaseModel):
    input_price: float
    output_price: float


class AssistantResponse(BaseModel):
    contents: list
    prices: AssistantPrice


def to_user_message(text: str, image_urls: Optional[List[str]] = None):
    contents = []

    text_content = {
        "type": "text",
        "text": text
    }
    contents.append(text_content)

    if image_urls:
        for image_url in image_urls:
            image_url_content = {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
            contents.append(image_url_content)

    user_message = {"role": "user", "content": contents}

    return user_message


def to_system_message(text: str):
    return {"role": "system", "content": text}


class GptAssistant:
    def __init__(self):
        self.openai_client = openai.AzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            api_key=OPENAI_API_KEY,
            api_version=OPENAI_API_VERSION,
        )

    @staticmethod
    def get_usage_price(usage: CompletionUsage):
        input_price = GPT_INPUT_PRICE * usage.prompt_tokens
        output_price = GPT_OUTPUT_PRICE * usage.completion_tokens

        return AssistantPrice(
            input_price=input_price,
            output_price=output_price,
        )

    def chat(self, messages, n=1, temperature=1.0):
        result = self.openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
            temperature=temperature,
            n=n,
        )

        assistant_price = self.get_usage_price(result.usage)
        response_contents = [choice.message.content for choice in result.choices]

        return AssistantResponse(
            contents=response_contents,
            prices=assistant_price,
        )

    def structured_chat(self, messages, response_format, n=1, temperature=1.0):
        result = self.openai_client.beta.chat.completions.parse(
            model=GPT_MODEL,
            messages=messages,
            response_format=response_format,
            temperature=temperature,
            n=n,
        )

        assistant_price = self.get_usage_price(result.usage)
        response_contents = [
            json.loads(choice.message.content) for choice in result.choices
        ]

        return AssistantResponse(
            contents=response_contents,
            prices=assistant_price,
        )


class GptBatchAssistant(GptAssistant):
    def messages_to_batch_req_line(self, custom_id: str, messages: list, response_format: Optional[BaseModel]):
        req_line = {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/chat/completions",
            "body": {
                "model": GPT_BATCH_MODEL,
                "messages": messages
            }
        }
        if response_format:
            schema = response_format.model_json_schema()
            if defs := schema.get("$defs"):
                for key, value in defs.items():
                    defs[key]["additionalProperties"] = False

            schema["additionalProperties"] = False

            req_line["body"]["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "schema": schema,
                    "name": response_format.__name__,
                    "strict": True,
                },
            }

        req_line = json.dumps(req_line, ensure_ascii=False)

        return req_line

    def file_create(self, req_lines):
        with TemporaryDirectory() as tmpdir:
            file_path = f"{tmpdir}/batch_requests.jsonl"
            with open(file_path, "wb") as tmp:
                for req_line in req_lines:
                    tmp.write(req_line.encode())
                    tmp.write(b"\n")

            with open(file_path, "rb") as tmp:
                file = self.openai_client.files.create(
                    file=tmp,
                    purpose="batch"
                )

        file_id = file.id
        status = "pending"
        while status.lower() != "processed":
            time.sleep(2)
            status = self.openai_client.files.retrieve(file_id).status
            print(f"File Creating - File Id: {file_id},  Status: {status}", flush=True, end="\r")

        print(f"File Created - File Id: {file_id},  Status: {status}")

        return file

    def batch_create(self, file_id):
        batch_response = self.openai_client.batches.create(
            input_file_id=file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )

        batch_id = batch_response.id
        status = "validating"
        while status not in ("completed", "failed", "canceled"):
            time.sleep(10)
            batch_response = self.openai_client.batches.retrieve(batch_id)
            status = batch_response.status
            print(f"Batch Creating - Batch Id: {batch_id},  Status: {status}", flush=True, end="\r")

        if batch_response.status == "failed":
            for error in batch_response.errors.data:
                raise Exception(f"Error code {error.code} Message {error.message}")

        print(f"Batch Created - Batch Id: {batch_id},  Status: {status}")
        return batch_response

    def get_batch_output_file(self, batch_response):
        output_file_id = batch_response.output_file_id
        output_file_response = self.openai_client.files.content(output_file_id)

        return output_file_response

    def file_to_responses(self, file_response):
        raw_responses = file_response.text.strip().split('\n')
        json_responses = []
        for raw_response in raw_responses:
            json_response = json.loads(raw_response)
            json_responses.append(json_response)

        json_responses.sort(key=lambda x: int(x['custom_id']))

        assistant_responses = []
        for json_response in json_responses:
            response = json_response.get('response')
            if response and response['body']['choices']:

                contents = [
                    choice['message']['content'] if choice['finish_reason'] == 'stop' else None
                    for choice in response['body']['choices']
                ]
                usage = CompletionUsage(**response['body']['usage'])

                assistant_response = AssistantResponse(
                    contents=contents,
                    prices=self.get_usage_price(usage),
                )
                assistant_responses.append(assistant_response)

            else:
                assistant_responses.append(None)

        return assistant_responses

    def batch_chat(self, batch_messages, response_format=None):
        req_lines = []
        for i, messages in enumerate(batch_messages, start=1):
            req_line = self.messages_to_batch_req_line(str(i), messages, response_format)
            req_lines.append(req_line)

        request_file = self.file_create(req_lines)
        batch_response = self.batch_create(request_file.id)
        output_file_response = self.get_batch_output_file(batch_response)
        assistant_responses = self.file_to_responses(output_file_response)

        return assistant_responses
