import json
import anthropic
from .utils import extract_json


SYSTEM_PROMPT = """你是一个旅行海报图像提示词生成器。
根据行程 JSON，生成一条能让 AI 图像模型生成旅行攻略海报的英文 prompt。
只输出 JSON，不要额外解释。"""

INSTRUCTIONS = """输出格式（严格 JSON）：
{
  "poster_prompt": "英文 prompt..."
}

要求：
- 描述一张旅游攻略海报风格的图片
- 包含城市名、几个地点名、时间线概念、照片拼贴感
- 风格：travel guide poster, collage layout, warm colors, editorial photography style
- 提到具体的地点名（英文）和氛围词
- 不要让 AI 渲染大量文字，重点在视觉构图和氛围"""


async def run(client: anthropic.AsyncAnthropic, itinerary: dict, context: dict) -> str:
    combined = {
        "location": context.get("location", ""),
        "vibe": context.get("vibe", ""),
        "stops": [s.get("title", "") + " - " + s.get("location", "") for s in itinerary.get("stops", [])],
    }

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"{INSTRUCTIONS}\n\n行程摘要：\n{json.dumps(combined, ensure_ascii=False)}",
        }],
    )
    result = extract_json(response.content[0].text.strip())
    return result.get("poster_prompt", "")
