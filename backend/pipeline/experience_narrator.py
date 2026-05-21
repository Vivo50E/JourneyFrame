import json
import anthropic
from .utils import extract_json

SYSTEM_PROMPT = """You are an experiential journey narrator.
Input is an itinerary JSON.
Write warm, natural iMessage-style messages describing the plan — like a friend texting you.
Output strict JSON only — no extra explanation."""

INSTRUCTIONS = """Output format (strict JSON):
{
  "messages": [
    "First message (introduce the overall plan or open warmly)",
    "Second message (cover the first one or two stops)",
    "Third message (cover the remaining stops)",
    "Fourth message (warm close or invitation)"
  ]
}

Requirements:
- Use first/second person, friendly tone
- Warm, emotional, relationship-aware
- 2–4 messages total, each strictly under 160 characters
- Emojis welcome for warmth
- No newline characters inside JSON strings"""


async def run(client: anthropic.AsyncAnthropic, itinerary: dict) -> dict:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{INSTRUCTIONS}\n\nItinerary JSON:\n{json.dumps(itinerary, ensure_ascii=False, indent=2)}",
            }
        ],
    )
    text = response.content[0].text.strip()
    return extract_json(text)
