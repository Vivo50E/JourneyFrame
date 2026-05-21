import json
import anthropic
from .utils import extract_json

SYSTEM_PROMPT = """你是一个旅程叙事作家。
输入是行程 JSON。
把行程写成温暖、自然、像朋友在 iMessage 里发给你的消息。
只输出 JSON，不要任何额外解释。"""

INSTRUCTIONS = """输出格式（严格 JSON）：
{
  "messages": [
    "第一条消息内容（介绍整体行程或开场）",
    "第二条消息（介绍第一两个 stop）",
    "第三条消息（介绍后续 stop）",
    "第四条消息（结尾，温馨收尾或邀请）"
  ]
}

要求：
- 用第一/第二人称，像朋友说话
- 轻松、情感化、有关系感
- 分 2-4 条消息，每条严格不超过 60 字
- 可用 emoji 增加温度感
- JSON 字符串内不要有换行符"""


async def run(client: anthropic.AsyncAnthropic, itinerary: dict) -> dict:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{INSTRUCTIONS}\n\n行程 JSON：\n{json.dumps(itinerary, ensure_ascii=False, indent=2)}",
            }
        ],
    )
    text = response.content[0].text.strip()
    return extract_json(text)
