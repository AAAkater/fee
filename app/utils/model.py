from datetime import datetime, timezone

from openai import OpenAI

from app.core.config import settings
from app.utils.logger import logger

model_client = OpenAI(
    api_key=settings.MODEL_API_KEY, base_url=settings.MODEL_BASE_URL
)


async def generate_model_response_stream():
    try:
        response = model_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant",
                },
                {"role": "user", "content": "Hello"},
            ],
            stream=True,
        )
        for chunk in response:
            if content := chunk.choices[0].delta.content:
                yield {
                    "data": {
                        "role": "assistant",
                        "content": content,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                }
    except Exception as e:
        logger.error(f"流式生成失败: {e}")
        yield {"data": "[ERROR] 服务异常"}
