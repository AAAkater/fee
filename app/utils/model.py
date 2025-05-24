from openai import OpenAI

from app.core.config import settings

model_client = OpenAI(
    api_key=settings.MODEL_API_KEY, base_url=settings.MODEL_BASE_URL
)
