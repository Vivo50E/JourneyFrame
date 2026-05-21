import json
import anthropic
from .utils import extract_json

SYSTEM_PROMPT = """You are an intelligent trip context enricher.
Input is the Intent Parser JSON result.
Enrich it with weather context, user preferences, relationship tone, and local recommendation notes.
Output strict JSON only — no extra explanation."""

INSTRUCTIONS = """Add the following fields to the existing JSON and output the complete object:
{
  ...(all original fields retained),
  "weather_context": "one-line weather description, e.g. 'Light rain expected in Seattle tomorrow afternoon — great for indoor-outdoor mix'",
  "user_preferences": "assumed user preferences: budget style, dietary, activity type",
  "relationship_context": "emotional tone for this relationship type, e.g. 'warm and nostalgic for reuniting friends'",
  "local_recommendation_context": "key local character notes for this city/area"
}"""


async def run(client: anthropic.AsyncAnthropic, intent: dict) -> dict:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{INSTRUCTIONS}\n\nInput JSON:\n{json.dumps(intent, ensure_ascii=False, indent=2)}",
            }
        ],
    )
    text = response.content[0].text.strip()
    return extract_json(text)
