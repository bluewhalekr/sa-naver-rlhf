from pydantic_core import ValidationError as PydanticValidationError


# openai에서 structured output을 받았지만, json.loads를 통해 파싱하지 못하거나, 원하는 키가 없거나 다른 경우 발생
class GptAssistantResponseError(PydanticValidationError):
    pass


# 요청한 persona 또는 persona에 맞는 image_url이 DB에 없는 경우
class NoAvailablePersonaImageInfoError(Exception):
    pass
