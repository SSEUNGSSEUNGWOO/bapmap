import { NextRequest } from "next/server";
import Anthropic from "@anthropic-ai/sdk";

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

export async function POST(req: NextRequest) {
  const { messages, spotsContext } = await req.json();
  if (!messages?.length) return new Response("No messages", { status: 400 });

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: object) => {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
      };

      try {
        const msgStream = anthropic.messages.stream({
          model: "claude-haiku-4-5-20251001",
          max_tokens: 400,
          system: `You are Bapmap's food guide for English-speaking tourists in Korea.
${spotsContext ? `\nContext from the current search:\n${spotsContext}\n` : ""}
Rules:
- ONLY answer questions about: Korean food, restaurants, cafes, travel in Korea, neighborhoods, K-culture (K-pop, K-drama) in relation to food/places, or spots in the context above.
- If the question is unrelated to Korean food or travel (e.g. coding, politics, math, general knowledge), respond with exactly: "I'm only here to help with food and travel in Korea 🍜"
- If asked about a specific spot, reference it by name with a markdown link: [Name](/spots/slug)
- Be friendly, specific, concise. Max 150 words.
- If you don't know something, say so honestly.`,
          messages,
        });

        for await (const chunk of msgStream) {
          if (chunk.type === "content_block_delta" && chunk.delta.type === "text_delta") {
            send({ type: "text", text: chunk.delta.text });
          }
        }
        send({ type: "done" });
      } catch (e) {
        send({ type: "error", text: String(e) });
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
