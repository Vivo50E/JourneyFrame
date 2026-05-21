import json
import anthropic
from .utils import extract_json

SYSTEM_PROMPT = """You are a relationship-aware experiential trip planner.
Input is the full Context Enrichment JSON.
Generate 3 to 5 itinerary stops, each tailored to the vibe, relationship, mood, and weather.
Output strict JSON only — no extra explanation."""

INSTRUCTIONS = """Output format (strict JSON):
{
  "stops": [
    {
      "title": "stop name",
      "time": "specific time, e.g. 2:00 PM",
      "location": "venue name and brief address",
      "reason": "why this place fits the relationship and vibe",
      "duration": "estimated duration, e.g. 45 minutes",
      "emotional_purpose": "the feeling this stop creates"
    }
  ]
}

Requirements:
- Generate a connected timeline (3–5 stops)
- Be weather-aware (indoor/outdoor mix as appropriate)
- Each stop should have warmth and relationship resonance"""


async def run(client: anthropic.AsyncAnthropic, context: dict) -> dict:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{INSTRUCTIONS}\n\nInput JSON:\n{json.dumps(context, ensure_ascii=False, indent=2)}",
            }
        ],
    )
    text = response.content[0].text.strip()
    return extract_json(text)
