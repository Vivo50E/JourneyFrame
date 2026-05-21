import "dotenv/config";
import axios from "axios";
import { Spectrum, attachment } from "spectrum-ts";
import { imessage } from "spectrum-ts/providers/imessage";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";
const PROJECT_ID = process.env.PHOTON_PROJECT_ID ?? "";
const PROJECT_SECRET = process.env.PHOTON_PROJECT_SECRET ?? "";

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Warm messages sent while AI is thinking (one per ~8s)
const THINKING_MESSAGES = [
  "Understanding your request, starting to plan now 🧠",
  "Analyzing weather, vibe, and relationship context... ☁️",
  "Got some great ideas, refining your itinerary ✨",
  "Almost there! Writing each stop with warmth 💬",
  "Final step — generating your travel poster... 🖼️",
];

async function sendThinkingMessages(
  reply: (text: string) => Promise<unknown>,
  signal: { done: boolean }
) {
  for (const msg of THINKING_MESSAGES) {
    if (signal.done) break;
    await delay(8000);
    if (!signal.done) await reply(msg);
  }
}

async function main() {
  console.log("[spectrum] Connecting to Photon Spectrum...");

  const app = await Spectrum({
    projectId: PROJECT_ID,
    projectSecret: PROJECT_SECRET,
    providers: [imessage.config()],
  });

  console.log("[spectrum] Connected. Listening for iMessages...");

  for await (const [space, message] of app.messages) {
    if (message.content.type !== "text") continue;

    const text = message.content.text;
    const senderRaw = message.sender as any;
    const sender: string =
      senderRaw?.id ?? senderRaw?.handle ?? senderRaw?.address ?? String(senderRaw ?? "unknown");
    console.log(`[spectrum] ← iMessage from ${sender}: "${text}"`);

    await space.responding(async () => {
      try {
        // Immediate acknowledgment
        await space.send("Got it! Let me plan your outing 🗺️");
        await delay(600);

        const signal = { done: false };

        // Warm messages in parallel with backend call
        const thinkingTask = sendThinkingMessages(
          (t) => space.send(t),
          signal
        );

        const backendTask = axios.post(`${BACKEND_URL}/webhook`, {
          sender,
          text,
          conversation_id: sender,
        });

        const { data } = await backendTask;
        signal.done = true;
        await thinkingTask;

        await delay(400);

        // Send itinerary messages
        for (const msg of data.messages ?? []) {
          await space.send(msg.text);
          await delay(900);
        }

        // Send generated images
        console.log(`[spectrum] image_b64 count: ${data.image_b64?.length ?? 0}, size: ${data.image_b64?.[0]?.length ?? 0} chars`);
        if (data.image_b64?.length) {
          await space.send("Here's the travel poster I imagined for your journey 🎨");
          await delay(500);
          for (const b64 of data.image_b64 as string[]) {
            const buf = Buffer.from(b64, "base64");
            await space.send(attachment(buf, { mimeType: "image/png", name: "journey-scene.png" }));
            await delay(600);
          }
        } else if (data.image_prompts?.length) {
          const preview = (data.image_prompts as string[])
            .slice(0, 2)
            .map((p: string, i: number) => `🖼 Scene ${i + 1}: ${p}`)
            .join("\n\n");
          await space.send(`Here's the scene I imagined for your journey:\n\n${preview}`);
        }

        console.log(`[spectrum] ✓ Replied to ${sender}`);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        console.error("[spectrum] Error:", msg);
        await space.send("Something went wrong while planning — please try again 🙏");
      }
    });
  }
}

main().catch((err) => {
  console.error("[spectrum] Fatal:", err);
  // Restart after 3 seconds instead of dying
  setTimeout(() => main().catch(console.error), 3000);
});
