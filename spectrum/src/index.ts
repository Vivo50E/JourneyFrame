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
  "正在理解你的需求，马上开始规划 🧠",
  "在分析天气、氛围和关系上下文... ☁️",
  "已经有几个不错的想法了，正在细化行程 ✨",
  "快好了！正在帮你把每一站都写得有温度 💬",
  "最后一步，在为你生成专属场景图... 🖼️",
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
        await space.send("收到！让我帮你规划这次出行 🗺️");
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
          await space.send("这是我为你想象的场景画面 🎨");
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
          await space.send(`这是我为你想象的场景：\n\n${preview}`);
        }

        console.log(`[spectrum] ✓ Replied to ${sender}`);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        console.error("[spectrum] Error:", msg);
        await space.send("哎，规划途中出了点问题，再试一次吧 🙏");
      }
    });
  }
}

main().catch((err) => {
  console.error("[spectrum] Fatal:", err);
  // Restart after 3 seconds instead of dying
  setTimeout(() => main().catch(console.error), 3000);
});
