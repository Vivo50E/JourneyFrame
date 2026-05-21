import json
import anthropic
from .utils import extract_json


SYSTEM_PROMPT = """You are a travel poster image prompt generator.
Given an itinerary JSON, generate one English prompt that will produce a cinematic travel poster.
Output strict JSON only — no extra explanation."""

INSTRUCTIONS = """Output format (strict JSON):
{
  "poster_prompt": "English prompt..."
}

Requirements:
- Describe a travel guide poster style image
- Include the city name, 3–4 location names as visual labels, timeline concept, collage feel
- Style: modern travel editorial poster, warm color palette, subtle route line connecting stops
- Reference specific venue names and atmosphere words
- Avoid rendering heavy text — focus on visual composition and mood"""


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
            "content": f"{INSTRUCTIONS}\n\nItinerary summary:\n{json.dumps(combined, ensure_ascii=False)}",
        }],
    )
    result = extract_json(response.content[0].text.strip())
    return result.get("poster_prompt", "")
