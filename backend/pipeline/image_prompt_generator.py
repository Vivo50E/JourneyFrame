import json
import anthropic
from .utils import extract_json

SYSTEM_PROMPT = """你是一个场景图像提示生成器。
输入是行程 JSON。
为每个主要 stop 生成一条 cinematic 风格的英文图像 prompt。
只输出 JSON，不要任何额外解释。"""

INSTRUCTIONS = """输出格式（严格 JSON）：
{
  "image_prompts": [
    {
      "stop_title": "行程点名称",
      "prompt": "English cinematic image prompt..."
    }
  ]
}

要求：
- Prompt 必须用英文（用于图像生成模型）
- 包含：地点感、情绪、天气、光线、人物关系
- 风格：cinematic, warm tones, photorealistic
- 示例："Two friends sitting by a misty Seattle coffee shop window, soft rain outside, warm amber lighting, intimate conversation, cinematic composition, 35mm film look"
- 为每个 stop 生成一条"""


async def run(client: anthropic.AsyncAnthropic, itinerary: dict) -> dict:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
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
