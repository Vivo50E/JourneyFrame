import anthropic
from .utils import extract_json

SYSTEM_PROMPT = """You are a travel intent parser.
Extract structured intent from the user's message.
Output strict JSON only — no extra explanation."""

INSTRUCTIONS = """Output format (strict JSON):
{
  "location": "city/area, or 'unknown' if not mentioned",
  "occasion": "description of the occasion",
  "relationship": "relationship type, e.g. friend/couple/family",
  "vibe": "mood/atmosphere, e.g. cozy/energetic/romantic/relaxed",
  "time_window": "time window, e.g. tomorrow afternoon/this weekend morning",
  "constraints": "any constraints, e.g. rainy day/budget-friendly/vegetarian, or 'none'"
}"""


async def run(client: anthropic.AsyncAnthropic, user_message: str) -> dict:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"{INSTRUCTIONS}\n\nUser input: {user_message}"}],
    )
    text = response.content[0].text.strip()
    return extract_json(text)
