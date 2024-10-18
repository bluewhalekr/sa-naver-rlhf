import os
from dotenv import load_dotenv

load_dotenv()

SCHEDULER_INTERVAL = 60 * 5  # 5 minutes
QUESTION_COUNT_BUFFER = 100

OPENAI_API_VERSION = "2024-08-01-preview"
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

USERNAME = "smartagent"
DB_PASSWORD = os.getenv("DB_PASSWORD", "noPassword")
CONNECT_STRING = f"postgresql+asyncpg://{USERNAME}:{DB_PASSWORD}@10.10.5.13:31655/smartagent"
