from config import AUTH_API_URL, TEST_MODE
from logger import logger
from models import AuthRequestData, AuthResponse
from services.module import ApiClient

MOCK_AUTH_RESPONSE = {
    "status": "success",
}


def request_authenticate(username: str, token: str) -> AuthResponse:
    logger.info(f"{username.rjust(12)}| request_authenticate")

    if TEST_MODE:
        json_response = MOCK_AUTH_RESPONSE

    else:
        api_client = ApiClient()

        req_data = AuthRequestData(username=username, token=token)
        json_response = api_client.post(AUTH_API_URL, data=req_data.dict())

    return AuthResponse(**json_response)


def authenticate(username, token) -> bool:
    response = request_authenticate(username, token)

    if response.status == "success":
        return True

    return False
