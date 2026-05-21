import "dotenv/config";
import express, { Request, Response } from "express";
import axios from "axios";
import { sendMessages, OutboundMessage, PhotonInboundMessage } from "./photon";

const PORT = parseInt(process.env.PORT ?? "3000", 10);
const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

const app = express();
app.use(express.json());

/**
 * Health check — also used by Photon Spectrum to verify the webhook is alive.
 */
app.get("/health", (_req: Request, res: Response) => {
  res.json({ status: "ok", service: "journeyframe-spectrum" });
});

/**
 * Photon Spectrum webhook — receives inbound iMessage events.
 *
 * Expected payload from Photon:
 * {
 *   "sender": "+12065551234",
 *   "text": "...",
 *   "conversationId": "abc123"   (optional)
 * }
 */
app.post("/photon/webhook", async (req: Request, res: Response) => {
  // Acknowledge immediately so Photon doesn't time out
  res.status(200).json({ received: true });

  const body = req.body as PhotonInboundMessage;
  const { sender, text, conversationId } = body;

  if (!sender || !text) {
    console.warn("[spectrum] Ignoring malformed inbound message:", body);
    return;
  }

  console.log(`[spectrum] ← iMessage from ${sender}: "${text}"`);

  let pipelineResult: {
    messages: Array<{ type: string; text: string }>;
    image_prompts?: string[];
    image_urls?: string[];
  };

  try {
    const { data } = await axios.post(`${BACKEND_URL}/webhook`, {
      sender,
      text,
      conversation_id: conversationId,
    });
    pipelineResult = data;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("[spectrum] Backend error:", message);
    await sendMessages(sender, [
      { type: "text", text: "Sorry, I ran into an issue planning your journey. Try again in a moment! 🙏" },
    ], conversationId);
    return;
  }

  // Build outbound message sequence
  const outbound: OutboundMessage[] = [];

  for (const msg of pipelineResult.messages ?? []) {
    outbound.push({ type: "text", text: msg.text });
  }

  // If backend returned image URLs, send them as media; otherwise send prompts as text
  if (pipelineResult.image_urls?.length) {
    for (const url of pipelineResult.image_urls) {
      outbound.push({ type: "media", url });
    }
  } else if (pipelineResult.image_prompts?.length) {
    const promptPreview = pipelineResult.image_prompts
      .slice(0, 3)
      .map((p, i) => `🖼 Scene ${i + 1}: ${p}`)
      .join("\n\n");
    outbound.push({
      type: "text",
      text: `Here are the cinematic scenes I imagined for your journey:\n\n${promptPreview}`,
    });
  }

  console.log(`[spectrum] → Sending ${outbound.length} messages to ${sender}`);
  await sendMessages(sender, outbound, conversationId);
  console.log(`[spectrum] ✓ Delivered to ${sender}`);
});

app.listen(PORT, () => {
  console.log(`[spectrum] JourneyFrame Spectrum gateway listening on :${PORT}`);
  console.log(`[spectrum] Photon webhook endpoint: POST /photon/webhook`);
  console.log(`[spectrum] Backend: ${BACKEND_URL}`);
});
