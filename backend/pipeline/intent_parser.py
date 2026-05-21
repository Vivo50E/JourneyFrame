import anthropic
from .utils import extract_json

SYSTEM_PROMPT = """你是一个旅行出行理解器。
从用户的一句话里抽取结构化意图。
只输出 JSON，不要任何额外解释。"""

INSTRUCTIONS = """输出格式（严格 JSON）：
{
  "location": "城市/地点，若未知填 unknown",
  "occasion": "场合描述",
  "relationship": "关系类型，如 朋友/情侣/家人",
  "vibe": "氛围/情绪，如 温馨/活力/放松",
  "time_window": "时间区间，如 明天下午/周末上午",
  "constraints": "任何约束，如 雨天/预算有限/不吃辣，若无填 none"
}"""


async def run(client: anthropic.AsyncAnthropic, user_message: str) -> dict:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"{INSTRUCTIONS}\n\n用户输入：{user_message}"}],
    )
    text = response.content[0].text.strip()
    return extract_json(text)
