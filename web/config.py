import os
import sys

from dotenv import load_dotenv

load_dotenv()


WEB_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(WEB_ROOT)

ICON_PATH = 'assets/AIMMO-시그니처 로고_바이올렛+블랙.png'  # os.path.join(ASSET_ROOT, "AIMMO-시그니처 로고_바이올렛+블랙.png")
ICON_PATH = os.path.abspath(ICON_PATH)

BASE_API_URL = "https://task1.smart-agent.bluewhale.kr"
AUTH_API_URL = f"{BASE_API_URL}/v2/auth"
IMAGE_URL_API_URL = f"{BASE_API_URL}/v2/image-urls"
QUESTION_API_URL = f"{BASE_API_URL}/v2/questions"

BTN_WAITING_TIME = 10
