import { NextRequest } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";
import { createClient } from "@supabase/supabase-js";

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const sb = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

async function ragSearch(query: string): Promise<string> {
  try {
    const embRes = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: query.replace(/\n/g, " "),
    });
    const embedding = embRes.data[0].embedding;

    const [spotsRes, guidesRes] = await Promise.all([
      sb.rpc("hybrid_search_spots", {
        query_text: query,
        query_embedding: embedding,
        match_count: 4,
        filter_region: null,
        filter_category: null,
      }),
      sb.rpc("search_guides", {
        query_embedding: embedding,
        match_threshold: 0.3,
        match_count: 2,
      }),
    ]);

    const spots = (spotsRes.data || [])
      .filter((s: Record<string, unknown>) => s.status === "업로드완료")
      .map((s: Record<string, unknown>) => {
        const name = (s.english_name || s.name) as string;
        const slug = name.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
        const memo = String(s.memo || "").slice(0, 200);
        return `[SPOT] ${name} — ${s.category} · ${s.region || s.city} · ★${s.rating}\nLink: /spots/${slug}${memo ? `\nWhy: ${memo}` : ""}`;
      })
      .join("\n\n");

    const guides = (guidesRes.data || [])
      .map((g: Record<string, unknown>) =>
        `[GUIDE] ${g.title}\n${String(g.content || "").slice(0, 300)}`
      )
      .join("\n\n");

    return [spots, guides].filter(Boolean).join("\n\n---\n\n");
  } catch {
    return "";
  }
}

export async function POST(req: NextRequest) {
  const { messages, spotsContext } = await req.json();
  if (!messages?.length) return new Response("No messages", { status: 400 });

  const lastUserMessage = [...messages].reverse().find((m: { role: string }) => m.role === "user");
  const userQuery = lastUserMessage?.content || "";

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: object) => {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
      };

      try {
        const ragContext = await ragSearch(userQuery);
        const fullContext = [spotsContext, ragContext].filter(Boolean).join("\n\n---\n\n");

        const msgStream = anthropic.messages.stream({
          model: "claude-haiku-4-5-20251001",
          max_tokens: 400,
          system: `You are Bapmap's food guide for English-speaking tourists in Korea.
${fullContext ? `\nRelevant context:\n${fullContext}\n` : ""}
Rules:
- ONLY answer questions about: Korean food, restaurants, cafes, travel in Korea, neighborhoods, K-culture (K-pop, K-drama) in relation to food/places.
- If the question is unrelated to Korean food or travel (e.g. coding, politics, math, general knowledge), respond with exactly: "I'm only here to help with food and travel in Korea 🍜"
- If recommending a spot from context, always explain WHY — a specific dish, the vibe, the price, what makes it stand out.
- Reference spots with markdown links: [Name](/spots/slug)
- Be friendly, specific, concise. Max 200 words.
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
