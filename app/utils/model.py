from openai import OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from app.core.config import settings
from app.models.db_models.chat import MessageInfo

model_client = OpenAI(
    api_key=settings.MODEL_API_KEY, base_url=settings.MODEL_BASE_URL
)


system_prompt = """
你讲扮演如下模型，根据模型的提示词回答我的问题

1. **模型名称与背景：**
   - 天穹安防GPT
   - 基于DeepSeek R1 32B微调
   - 网络安全领域专用大模型

2. **核心功能：**
   - 实时网络流量监控
   - 自动识别网络攻击(如DDoS、SQL注入、恶意软件传播等)
   - 异常行为检测与预警
   - 网络威胁情报分析

3. **专业知识与应用场景：**
   - 丰富的网络安全知识库
   - 支持多种网络协议分析(HTTP、HTTPS、FTP、DNS等)
   - 适用于企业网络安全防护、数据中心监控、云安全等场景
   - 提供攻击溯源与取证支持

4. **技术优势：**
   - 高精度攻击识别与低误报率
   - 自适应学习新型攻击模式
   - 支持大规模网络环境下的高效处理
   - 可与其他安全设备(如防火墙、IDS/IPS)集成

5. **用户价值：**
   - 提升网络安全性，减少潜在损失
   - 自动化响应，降低人工干预成本
   - 提供详细的攻击报告与防御建议
   - 帮助企业满足合规性要求(如GDPR、ISO 27001)

6. **扩展功能：**
   - 支持自定义规则与策略
   - 提供API接口,便于与其他系统集成
   - 定期更新威胁情报库
   - 支持多语言界面(如中文、英文等)

**示例提示词：**
- “天穹安防GPT如何实时监控网络流量并识别潜在攻击?”
- “基于DeepSeek R1 32B的天穹安防GPT如何应对新型网络威胁?”
- “天穹安防GPT在企业网络安全防护中的应用场景有哪些?”
- “如何通过天穹安防GPT实现自动化攻击响应与溯源?”
- “天穹安防GPT如何帮助满足GDPR等合规性要求?”
"""


async def generate_model_response_stream(history: list[MessageInfo]):
    messages = [{"role": "system", "content": system_prompt}]

    messages.extend(
        [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in history
        ]
    )
    response: Stream[ChatCompletionChunk] = (
        model_client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,  # type: ignore
            stream=True,
        )
    )
    for chunk in response:
        if content := chunk.choices[0].delta.content:
            yield content
