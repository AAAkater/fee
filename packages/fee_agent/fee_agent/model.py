from llama_index.llms.deepseek import DeepSeek

from fee_agent.config import settings

ds_model = DeepSeek(
    model=settings.llm.model_name,
    api_key=settings.llm.model_api_key,
)
