Build an MVP for a hackathon project called **JourneyFrame**.

## Product Concept

JourneyFrame is an AI-powered conversational trip planner that creates personalized real-world outing plans through iMessage.

The user texts the AI something like:

> “My friend Sarah is visiting Seattle tomorrow. Plan a cozy rainy-day afternoon for us.”

The AI should:
1. Understand the user request.
2. Consider relationship context, mood, location, weather, budget, time, and preferences.
3. Generate a structured outing itinerary.
4. Generate image prompts for each major stop.
5. Return the plan conversationally through Photon Spectrum.
6. Optionally send generated scene images back to the user through iMessage.

This is NOT a generic travel planner. It is a **relationship-aware experiential journey agent**.

## Hackathon Requirements

This project MUST deeply use:

### RocketRide
Use RocketRide as the core AI workflow orchestration layer.

RocketRide should power at least one real multi-step AI pipeline, not just a simple LLM call.

Required RocketRide pipeline:

1. Intent Parser
   - Extract city/location
   - Extract occasion
   - Extract relationship type
   - Extract vibe/mood
   - Extract time window
   - Extract constraints

2. Context Enrichment
   - Add weather context
   - Add user preference context
   - Add friend/relationship context
   - Add local recommendation context

3. Itinerary Planner
   - Generate 3–5 stops
   - Each stop has time, location, reason, estimated duration, and emotional purpose

4. Experience Narrator
   - Turn itinerary into warm conversational messages

5. Image Prompt Generator
   - Generate one image prompt per major stop
   - Prompts should be cinematic, location-aware, and emotionally aligned

6. Final Response Composer
   - Compose messages suitable for iMessage delivery

### Photon Spectrum
Use Photon Spectrum as the required conversational delivery layer.

Photon must:
- Receive inbound iMessage messages
- Forward the message to the backend webhook
- Send AI-generated replies back to the user
- Support multi-message response flow
- Ideally support image delivery if available

Photon is not optional and should not be superficial. The product experience must happen through iMessage.

## MVP Scope

Build the following:

### 1. Photon Spectrum Node.js Layer

Create `/spectrum` directory.

Responsibilities:
- Initialize Photon Spectrum client
- Listen for incoming iMessage messages
- POST incoming messages to FastAPI backend at `/webhook`
- Receive backend response
- Send one or more messages back through iMessage
- If image URLs are returned, send them as media if supported; otherwise send links

Files:
- `spectrum/index.ts`
- `spectrum/package.json`
- `spectrum/.env.example`

Use environment variables:

```env
PHOTON_PROJECT_ID=
PHOTON_PROJECT_SECRET=
BACKEND_URL=http://localhost:8000