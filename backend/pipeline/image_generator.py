import openai


async def run(api_key: str, image_prompts: list[str]) -> list[str]:
    """Generate images for the first 1-2 stops, return base64 strings."""
    if not image_prompts:
        return []

    client = openai.AsyncOpenAI(api_key=api_key)
    results = []

    # Only generate for the first 2 stops to keep latency reasonable
    for prompt in image_prompts[:2]:
        try:
            response = await client.images.generate(
                model="gpt-image-2",
                prompt=prompt,
                n=1,
                size="1024x1024",
            )
            b64 = response.data[0].b64_json
            if b64:
                results.append(b64)
        except Exception as exc:
            print(f"[image_generator] Skipping image: {exc}")

    return results
