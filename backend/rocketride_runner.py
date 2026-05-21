"""
RocketRide pipeline runner for JourneyFrame.
Uses the pre-built .pipe file in the rocketride/ directory.
"""

import json
import os
import pathlib
import re
from typing import Any

PIPELINE_FILE = pathlib.Path(__file__).parent.parent / "rocketride" / "journeyframe.pipe"


def _inject_api_key(pipe_path: pathlib.Path, anthropic_key: str) -> str:
    """Return the pipeline JSON with Anthropic key env vars substituted."""
    text = pipe_path.read_text()
    text = text.replace("${ANTHROPIC_API_KEY}", anthropic_key)
    text = text.replace("${ROCKETRIDE_ANTHROPIC_KEY}", anthropic_key)
    return text


async def run(user_message: str) -> dict[str, Any]:
    """Run the JourneyFrame pipeline via RocketRide SDK."""
    from rocketride.client import RocketRideClient
    from rocketride.schema import Question

    uri = os.environ.get("ROCKETRIDE_URI", "http://localhost:5565")
    apikey = os.environ.get("ROCKETRIDE_APIKEY", "local")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

    # Build pipeline config with API key injected
    pipe_json = _inject_api_key(PIPELINE_FILE, anthropic_key)
    pipeline_config = json.loads(pipe_json)

    async with RocketRideClient(uri=uri, auth=apikey) as client:
        # Start the pipeline from config object
        response = await client.use(pipeline=pipeline_config)
        token = response["token"]

        # Build and send question
        question = Question()
        question.addQuestion(user_message)

        result = await client.chat(token=token, question=question)

        # Debug: log the result structure
        import logging
        logging.getLogger("journeyframe").info("RocketRide result keys: %s", list(result.keys()) if isinstance(result, dict) else type(result))
        logging.getLogger("journeyframe").info("RocketRide result: %s", str(result)[:500])

        # Extract answer text — try different possible structures
        if isinstance(result, dict):
            if "data" in result and "answer" in result["data"]:
                answer = result["data"]["answer"].getText()
            elif "answers" in result:
                answers = result["answers"]
                answer = answers[0] if answers else ""
            elif "answer" in result:
                answer = result["answer"]
                if hasattr(answer, "getText"):
                    answer = answer.getText()
            else:
                answer = str(result)
        else:
            answer = str(result)

        return _parse_agent_response(answer)


def _parse_agent_response(text: str) -> dict:
    """Extract and parse the final JSON from the agent's answer."""
    text = text.strip()

    if "```" in text:
        for part in text.split("```"):
            part = part.strip().lstrip("json").strip()
            try:
                return json.loads(part)
            except json.JSONDecodeError:
                continue

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"messages": [{"type": "text", "text": text}], "image_prompts": []}
