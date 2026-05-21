import anthropic


async def run(
    _client: anthropic.AsyncAnthropic,
    narrator_output: dict,
    image_prompts_output: dict,
) -> dict:
    messages = [
        {"type": "text", "text": msg}
        for msg in narrator_output.get("messages", [])
    ]

    # Invite user to generate images as the last message
    messages.append({
        "type": "text",
        "text": "Want me to generate travel scene images for this journey? Just reply \"generate images\" ✨",
    })

    image_prompts = [
        item["prompt"]
        for item in image_prompts_output.get("image_prompts", [])
    ]

    return {
        "messages": messages,
        "image_prompts": image_prompts,
    }
