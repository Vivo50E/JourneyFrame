import json
import anthropic
from .utils import extract_json

SYSTEM_PROMPT = """你是一个关系型体验规划师。
输入是 Context Enrichment 的完整 JSON。
生成 3 到 5 个行程点，每个点要贴合氛围、关系、情绪、天气。
只输出 JSON，不要任何额外解释。"""

INSTRUCTIONS = """输出格式（严格 JSON）：
{
  "stops": [
    {
      "title": "行程点名称",
      "time": "具体时间，如 下午 2:00",
      "location": "地点名称和大概地址",
      "reason": "为什么选择这里，结合关系和氛围",
      "duration": "预计停留时长，如 45 分钟",
      "emotional_purpose": "这个行程点的情感意义"
    }
  ]
}

要求：
- 生成连贯时间线（3-5 个 stop）
- 考虑天气（室内/遮雨/舒适环境）
- 每个 stop 都要有温度感和关系感"""


async def run(client: anthropic.AsyncAnthropic, context: dict) -> dict:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{INSTRUCTIONS}\n\n输入 JSON：\n{json.dumps(context, ensure_ascii=False, indent=2)}",
            }
        ],
    )
    text = response.content[0].text.strip()
    return extract_json(text)
