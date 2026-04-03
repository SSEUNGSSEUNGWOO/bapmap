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

const PLACE_KEYWORDS = /where|recommend|best|good|eat|try|go|restaurant|cafe|bar|place|spot|food|near|around|in \w+dong|in \w+gu/i;

function needsSpots(query: string): boolean {
  return PLACE_KEYWORDS.test(query);
}

export async function POST(req: NextRequest) {
  const { messages } = await req.json();
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
        // 1. Embed raw query (no rewrite — saves one Anthropic call)
        const embRes = await openai.embeddings.create({
          model: "text-embedding-3-small",
          input: userQuery.replace(/\n/g, " "),
        });
        const embedding = embRes.data[0].embedding;

        // 2. Search in parallel
        const [spotsRes, guidesRes] = await Promise.all([
          sb.rpc("hybrid_search_spots", {
            query_text: userQuery,
            query_embedding: embedding,
            match_count: 5,
            filter_region: null,
            filter_category: null,
          }),
          sb.rpc("search_guides", {
            query_embedding: embedding,
            match_threshold: 0.3,
            match_count: 2,
          }),
        ]);

        const spots = spotsRes.data || [];
        const guides = guidesRes.data || [];

        // 3. Send spot cards only for place-seeking queries
        if (needsSpots(userQuery)) {
          const published = spots.filter((s: Record<string, unknown>) => s.status === "업로드완료");
          const comingSoon = spots.filter((s: Record<string, unknown>) => s.status !== "업로드완료").slice(0, 2);
          const toShow = [...published, ...comingSoon].slice(0, 5);
          if (toShow.length > 0) send({ type: "spots", data: toShow });
        }

        // 4. Build context (trimmed to reduce input tokens)
        const spotsContext = spots.map((s: Record<string, unknown>) => {
          const name = (s.english_name || s.name) as string;
          const slug = name.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
          const memo = String(s.memo || "").slice(0, 150);
          if (s.status === "업로드완료") {
            return `[SPOT] ${name} — ${s.category} · ${s.region || s.city} · ★${s.rating}\nLink: /spots/${slug}${memo ? `\nWhy: ${memo}` : ""}`;
          }
          return `[SPOT] ${name} (coming soon · ${s.category} · ${s.region || s.city})`;
        }).join("\n\n");

        const guidesContext = guides.map((g: Record<string, unknown>) =>
          `[GUIDE] ${g.title}\n${String(g.content || "").slice(0, 200)}`
        ).join("\n\n");

        const context = [spotsContext, guidesContext].filter(Boolean).join("\n\n---\n\n");

        // 5. Stream answer
        const msgStream = anthropic.messages.stream({
          model: "claude-sonnet-4-6",
          max_tokens: 250,
          system: `You are Bapmap's food guide for English-speaking tourists in Korea.
${context ? `\nContext:\n${context}\n` : ""}
Rules:
- ONLY answer questions about Korean food, restaurants, travel in Korea, neighborhoods, K-culture related to food/places.
- If unrelated (coding, politics, math, etc.), respond: "I'm only here to help with food and travel in Korea 🍜"
- For every spot you mention, explain WHY — a specific dish, vibe, or what makes it stand out.
- Reference spots with markdown links: [Name](/spots/slug)
- Concise. Max 150 words.`,
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
