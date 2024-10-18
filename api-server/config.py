import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_VERSION = "2024-08-01-preview"
AZURE_ENDPOINT = "https://cog-2zdwsmcbpa7va.openai.azure.com/"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USERNAME = "smartagent"
DB_PASSWORD = os.getenv("DB_PASSWORD", "noPassword")
CONNECT_STRING = f"postgresql+asyncpg://{USERNAME}:{DB_PASSWORD}@10.10.5.13:31655/smartagent"
