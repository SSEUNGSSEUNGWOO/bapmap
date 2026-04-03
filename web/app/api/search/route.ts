import { NextRequest } from "next/server";
import OpenAI from "openai";
import Anthropic from "@anthropic-ai/sdk";
import { createClient } from "@supabase/supabase-js";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const sb = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

// 1. Query Rewriting
async function rewriteQuery(raw: string) {
  const res = await anthropic.messages.create({
    model: "claude-haiku-4-5-20251001",
    max_tokens: 150,
    system: `You are a search query optimizer for Bapmap, a Korean restaurant guide.
Extract from the user query:
1. "query": clean search query in English (max 20 words)
2. "region": area in Korea if mentioned (e.g. "Gangnam", "Hongdae", "Itaewon", "Seongsu") — null if not
3. "category": food type if clearly mentioned (e.g. "Ramen", "Korean BBQ", "Cafe") — null if not
Return JSON only.`,
    messages: [{ role: "user", content: raw }],
  });
  try {
    return JSON.parse((res.content[0] as { text: string }).text);
  } catch {
    return { query: raw, region: null, category: null };
  }
}

// 2. Embed query
async function embedQuery(text: string) {
  const res = await openai.embeddings.create({
    model: "text-embedding-3-small",
    input: text.replace(/\n/g, " "),
  });
  return res.data[0].embedding;
}

// 3. Hybrid search
async function hybridSearch(query: string, embedding: number[], region: string | null, category: string | null) {
  const { data } = await sb.rpc("hybrid_search_spots", {
    query_text: query,
    query_embedding: embedding,
    match_count: 8,
    filter_region: region,
    filter_category: category,
  });
  return data || [];
}

export async function POST(req: NextRequest) {
  const { query } = await req.json();
  if (!query?.trim()) return new Response("No query", { status: 400 });

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: object) => {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
      };

      try {
        // 1. Rewrite
        const rewritten = await rewriteQuery(query);
        send({ type: "rewrite", data: rewritten });

        // 2. Embed + Search
        const embedding = await embedQuery(rewritten.query);
        const spots = await hybridSearch(rewritten.query, embedding, rewritten.region, rewritten.category);
        send({ type: "spots", data: spots.slice(0, 5) });

        if (!spots.length) {
          send({ type: "done", text: "No matching spots found. Try browsing /spots" });
          controller.close();
          return;
        }

        // 3. Stream answer
        const context = spots.slice(0, 5).map((s: Record<string, unknown>) => {
          const name = (s.english_name || s.name) as string;
          const slug = name.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
          if (s.status === "업로드완료") {
            return `[${name}] ${s.category} · ${s.region || s.city} · ★${s.rating} · ${s.price_level} · 🚇${s.subway}\nLink: /spots/${slug}\n${String(s.content || "").slice(0, 200)}`;
          }
          return `[${name}] — coming soon (${s.category} · ${s.region || s.city})`;
        }).join("\n\n");

        const msgStream = anthropic.messages.stream({
          model: "claude-haiku-4-5-20251001",
          max_tokens: 400,
          system: `You are Bapmap's food concierge helping English-speaking tourists find the best places to eat in Korea.
- Recommend only from retrieved spots. Never make up places.
- Published spots: give specific details (what to order, vibe, subway, price). Always link the restaurant name as markdown: [Restaurant Name](/spots/slug)
- Coming soon spots: mention as "📍 [Name] — on Bapmap soon"
- Direct and friendly. Like a tip from a Korean friend. 150-200 words.`,
          messages: [{ role: "user", content: `Query: ${query}\n\nSpots:\n${context}` }],
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
