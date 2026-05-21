import asyncio
import logging
import os

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
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

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("journeyframe")

app = FastAPI(title="JourneyFrame Backend")

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
USE_ROCKETRIDE = bool(os.environ.get("ROCKETRIDE_APIKEY", "").strip())


class WebhookPayload(BaseModel):
    sender: str
    text: str
    conversation_id: str | None = None


async def run_rocketride_pipeline(text: str) -> dict:
    """Run the full pipeline via RocketRide SDK."""
    from rocketride_runner import run
    return await run(text)


async def run_direct_pipeline(text: str) -> dict:
    """Run the full pipeline with direct Claude API calls (fallback)."""
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    log.info("[1/6] Intent Parser")
    intent = await intent_parser.run(client, text)
    log.info("Intent: %s", intent)

    log.info("[2/6] Context Enricher")
    context = await context_enricher.run(client, intent)

    log.info("[3/6] Itinerary Planner")
    itinerary = await itinerary_planner.run(client, context)

    log.info("[4+5/6] Narrator & Image Prompt Generator (parallel)")
    narrator_result, image_result = await asyncio.gather(
        experience_narrator.run(client, itinerary),
        image_prompt_generator.run(client, itinerary),
    )

    log.info("[6/6] Response Composer")
    return await response_composer.run(client, narrator_result, image_result)


@app.post("/webhook")
async def webhook(payload: WebhookPayload):
    log.info("Received message from %s: %s", payload.sender, payload.text)

    try:
        if USE_ROCKETRIDE:
            log.info("[RocketRide] Running pipeline via RocketRide SDK")
            final = await run_rocketride_pipeline(payload.text)
        else:
            log.info("[Direct] Running pipeline with direct Claude API calls")
            final = await run_direct_pipeline(payload.text)

        # Stage 7 — Image Generation (always runs if OpenAI key available)
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
    return {
        "status": "ok",
        "mode": "rocketride" if USE_ROCKETRIDE else "direct",
    }
