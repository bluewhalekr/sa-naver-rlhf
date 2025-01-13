import json

from prompts.question_generation_instruction_v2 import PERSONA_SYSTEM_PROMPT, PERSONA_USER_PROMPT, \
    IMAGE_KEYWORD_SYSTEM_PROMPT, IMAGE_KEYWORD_USER_PROMPT, IMAGE_QUERY_SYSTEM_PROMPT, IMAGE_QUERY_USER_PROMPT
from prompts.question_generation_output_formats import ImageKeywordSets, UserQueries, Persona
from gpt_assistant import GptBatchAssistant, to_user_message, to_system_message


class QuestionGenerator:
    def __init__(self):
        self.assistant = GptBatchAssistant()

    def make_personas(self, n: int = 1000):
        """
        Make the personas
        """
        system_message = to_system_message(PERSONA_SYSTEM_PROMPT)
        user_message = to_user_message(PERSONA_USER_PROMPT)

        messages = [system_message, user_message]
        batch_messages = [messages for _ in range(n)]

        persona_results = self.assistant.batch_chat(batch_messages, response_format=Persona)

        personas = []
        total_price = 0
        for persona_result in persona_results:
            content = persona_result.contents[0]
            if content:
                persona = json.loads(content)['persona']
            else:
                persona = None
            personas.append(persona)
            total_price += persona_result.prices.input_price + persona_result.prices.output_price
        return personas

    def make_image_keywords(self, personas: list):
        """
        Make the image queries
        """
        batch_messages = []
        for persona in personas:
            system_message = to_system_message(IMAGE_KEYWORD_SYSTEM_PROMPT)
            user_message = to_user_message(IMAGE_KEYWORD_USER_PROMPT.format(persona=persona))

            messages = [system_message, user_message]
            batch_messages.append(messages)

        keyword_results = self.assistant.batch_chat(batch_messages, response_format=ImageKeywordSets)

        keyword_sets = []
        total_price = 0
        for keyword_result in keyword_results:
            if content := keyword_result.contents[0]:
                keyword_set = list(json.loads(content).values())
            else:
                keyword_set = None
            keyword_sets.append(keyword_set)
            total_price += keyword_result.prices.input_price + keyword_result.prices.output_price
        return keyword_results



