import json
import anthropic
from .utils import extract_json

SYSTEM_PROMPT = """You are a travel poster prompt generator for gpt-image-2.
Given a trip itinerary JSON, generate ONE English prompt that will produce a beautiful travel guide poster.
Output strict JSON only, no extra explanation."""

INSTRUCTIONS = """Output format (strict JSON):
{
  "image_prompts": [
    {
      "stop_title": "Full Itinerary Poster",
      "prompt": "English poster prompt..."
    }
  ]
}

Requirements for the prompt:
- Design a single travel guide poster that captures the entire itinerary
- Style: modern travel editorial poster, clean layout, warm color palette, lifestyle photography collage feel
- Include: city name prominently, 3-4 location names as visual labels, time indicators (e.g. 2PM, 4PM), mood/weather atmosphere
- Render readable English text for location names and times — gpt-image-2 handles text well
- Add subtle map/route line connecting the stops
- Overall vibe should match the relationship and mood of the trip
- Example structure: "A stylish travel poster for [City], featuring [Stop1] at 2PM, [Stop2] at 4PM, [Stop3] at 6PM. Warm rainy-day mood, soft amber and teal color palette, editorial photography style with overlaid location labels and a subtle route line. Modern travel guide aesthetic."
"""


async def run(client: anthropic.AsyncAnthropic, itinerary: dict) -> dict:
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
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
