/**
 * Photon Spectrum HTTP client.
 *
 * Photon Spectrum uses project credentials to authenticate.
 * Inbound messages arrive as webhooks; outbound messages are sent via REST.
 *
 * Replace the base URL and endpoint paths below once you have confirmed
 * the exact Photon Spectrum API contract for your project.
 */

import axios from "axios";

const PHOTON_API_BASE = process.env.PHOTON_API_BASE ?? "https://api.photonspectrum.com";
const PROJECT_ID = process.env.PHOTON_PROJECT_ID ?? "";
const PROJECT_SECRET = process.env.PHOTON_PROJECT_SECRET ?? "";

function authHeaders() {
  const token = Buffer.from(`${PROJECT_ID}:${PROJECT_SECRET}`).toString("base64");
  return { Authorization: `Basic ${token}`, "Content-Type": "application/json" };
}

export interface PhotonInboundMessage {
  sender: string;       // phone number or handle
  text: string;
  conversationId?: string;
}

export interface OutboundTextMessage {
  type: "text";
  text: string;
}

export interface OutboundMediaMessage {
  type: "media";
  url: string;
  caption?: string;
}

export type OutboundMessage = OutboundTextMessage | OutboundMediaMessage;

/**
 * Send one or more messages to a recipient via Photon Spectrum.
 * Messages are delivered sequentially with a short delay to feel natural.
 */
export async function sendMessages(
  recipient: string,
  messages: OutboundMessage[],
  conversationId?: string
): Promise<void> {
  for (const msg of messages) {
    const body =
      msg.type === "text"
        ? { recipient, conversationId, type: "text", text: msg.text }
        : { recipient, conversationId, type: "media", url: msg.url, caption: msg.caption };

    await axios.post(`${PHOTON_API_BASE}/v1/messages/send`, body, {
      headers: authHeaders(),
    });

    // Natural typing delay between messages
    await new Promise((r) => setTimeout(r, 800));
  }
}
