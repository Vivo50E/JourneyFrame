import json
import anthropic
from .utils import extract_json

SYSTEM_PROMPT = """你是一个智能行程补全助手。
输入是 Intent Parser 的 JSON 结果。
在其基础上补充天气、用户偏好、关系上下文、本地推荐要点。
只输出 JSON，不要任何额外解释。"""

INSTRUCTIONS = """在原有字段基础上，新增以下字段并输出完整 JSON：
{
  ...(原字段保留),
  "weather_context": "一句话天气描述，如：明天下午西雅图有小雨，适合室内+咖啡",
  "user_preferences": "假设性用户偏好：预算、风格、饮食、活动偏好",
  "relationship_context": "关系氛围提示，强调是朋友/情侣/家人的感受",
  "local_recommendation_context": "当地高层推荐要点，简短描述"
}"""


async def run(client: anthropic.AsyncAnthropic, intent: dict) -> dict:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{INSTRUCTIONS}\n\n输入 JSON：\n{json.dumps(intent, ensure_ascii=False, indent=2)}",
            }
        ],
    )
    text = response.content[0].text.strip()
    return extract_json(text)
