import asyncio
import logging
import os

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pipeline import (
    context_enricher,
    experience_narrator,
    image_generator,
    image_prompt_generator,
    intent_parser,
    itinerary_planner,
    response_composer,
)

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("journeyframe")

app = FastAPI(title="JourneyFrame Backend")

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


class WebhookPayload(BaseModel):
    sender: str
    text: str
    conversation_id: str | None = None


@app.post("/webhook")
async def webhook(payload: WebhookPayload):
    log.info("Received message from %s: %s", payload.sender, payload.text)

    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    try:
        # Stage 1 — Intent Parser (RocketRide: prompt → llm_anthropic)
        log.info("[1/6] Intent Parser")
        intent = await intent_parser.run(client, payload.text)
        log.info("Intent: %s", intent)

        # Stage 2 — Context Enrichment (RocketRide: prompt → llm_anthropic)
        log.info("[2/6] Context Enricher")
        context = await context_enricher.run(client, intent)

        # Stage 3 — Itinerary Planner (RocketRide: prompt → llm_anthropic)
        log.info("[3/6] Itinerary Planner")
        itinerary = await itinerary_planner.run(client, context)

        # Stages 4 & 5 run concurrently — Narrator + Image Prompt Generator
        log.info("[4+5/6] Narrator & Image Prompt Generator (parallel)")
        narrator_result, image_result = await asyncio.gather(
            experience_narrator.run(client, itinerary),
            image_prompt_generator.run(client, itinerary),
        )

        # Stage 6 — Final Response Composer
        log.info("[6/6] Response Composer")
        final = await response_composer.run(client, narrator_result, image_result)

        # Stage 7 — Image Generation (gpt-image-1, parallel to response)
        if OPENAI_API_KEY:
            prompts = final.get("image_prompts", [])
            log.info("[7] Generating %d image(s) with gpt-image-2", min(len(prompts), 2))
            image_b64_list = await image_generator.run(OPENAI_API_KEY, prompts)
            final["image_b64"] = image_b64_list
            log.info("[7] Generated %d image(s)", len(image_b64_list))

        log.info("Pipeline complete. Messages: %d", len(final.get("messages", [])))
        return JSONResponse(content=final)

    except Exception as exc:
        log.exception("Pipeline error")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
def health():
    return {"status": "ok"}
