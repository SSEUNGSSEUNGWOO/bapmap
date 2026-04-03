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
    system: `You are a search query optimizer for Bapmap, a Korean food and culture guide.
Extract from the user query:
1. "query": clean search query in English (max 20 words)
2. "region": area in Korea if mentioned (e.g. "Gangnam", "Hongdae", "Itaewon", "Seongsu") — null if not
3. "category": food type if clearly mentioned (e.g. "Ramen", "Korean BBQ", "Cafe") — null if not
4. "intent": "food" if looking for restaurants, "culture" if asking about K-pop/drama/areas, "both" otherwise
Return JSON only.`,
    messages: [{ role: "user", content: raw }],
  });
  try {
    return JSON.parse((res.content[0] as { text: string }).text);
  } catch {
    return { query: raw, region: null, category: null, intent: "both" };
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

// 3. Hybrid search (spots)
async function searchSpots(query: string, embedding: number[], region: string | null, category: string | null) {
  const { data } = await sb.rpc("hybrid_search_spots", {
    query_text: query,
    query_embedding: embedding,
    match_count: 6,
    filter_region: region,
    filter_category: category,
  });
  return data || [];
}

// 4. Guide search (area + K-culture)
async function searchGuides(embedding: number[], count: number = 3) {
  const { data } = await sb.rpc("search_guides", {
    query_embedding: embedding,
    match_threshold: 0.3,
    match_count: count,
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

        // 2. Embed once, search in parallel
        const embedding = await embedQuery(rewritten.query);
        const [spots, guides] = await Promise.all([
          rewritten.intent !== "culture"
            ? searchSpots(rewritten.query, embedding, rewritten.region, rewritten.category)
            : Promise.resolve([]),
          rewritten.intent !== "food"
            ? searchGuides(embedding, 2)
            : Promise.resolve([]),
        ]);

        const published = spots.filter((s: Record<string, unknown>) => s.status === "업로드완료");
        const comingSoon = spots.filter((s: Record<string, unknown>) => s.status !== "업로드완료").slice(0, 2);
        const filteredSpots = [...published, ...comingSoon].slice(0, 5);
        send({ type: "spots", data: filteredSpots });

        // 3. Build context
        const spotsContext = filteredSpots.map((s: Record<string, unknown>) => {
          const name = (s.english_name || s.name) as string;
          const slug = name.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
          if (s.status === "업로드완료") {
            const memo = String(s.memo || "").slice(0, 200);
            return `[SPOT] ${name} — ${s.category} · ${s.region || s.city} · ★${s.rating} · ${s.price_level} · 🚇${s.subway}\nLink: /spots/${slug}${memo ? `\nWhy: ${memo}` : ""}`;
          }
          return `[SPOT - coming soon] ${name} (${s.category} · ${s.region || s.city})`;
        }).join("\n\n");

        // sources 수집 후 전송
        const allSources = Array.from(new Set(
          guides.flatMap((g: Record<string, unknown>) => (g.sources as string[]) || [])
        ));
        if (allSources.length > 0) send({ type: "sources", data: allSources });

        const guidesContext = guides.map((g: Record<string, unknown>) =>
          `[GUIDE - ${g.type === "kculture" ? "K-culture" : "Area Guide"}] ${g.title}\n${String(g.content || "").slice(0, 300)}`
        ).join("\n\n");

        const context = [spotsContext, guidesContext].filter(Boolean).join("\n\n---\n\n");

        if (!context.trim()) {
          send({ type: "done" });
          controller.close();
          return;
        }

        // 4. Stream answer
        const msgStream = anthropic.messages.stream({
          model: "claude-haiku-4-5-20251001",
          max_tokens: 450,
          system: `You are Bapmap's guide for English-speaking tourists in Korea — covering food, K-pop, K-drama, and local culture.

You have two types of context:
- [SPOT]: real restaurants/cafes personally visited and verified by Bapmap. Always recommend these with markdown links: [Name](/spots/slug)
- [GUIDE]: area and K-culture background info to enrich your answer

Rules:
- Use GUIDE context to give cultural/area context
- Use SPOT context for actual restaurant recommendations
- For every spot you recommend, include a specific reason WHY — what makes it worth going (a signature dish, the vibe, the price, a local secret, the location relevance). Never just name-drop a place without explaining it.
- Never make up places or spots not in the context
- Coming soon spots: mention as "📍 [Name] — on Bapmap soon"
- Friendly, specific, like a tip from a Korean local. 150-220 words.`,
          messages: [{ role: "user", content: `Query: ${query}\n\n${context}` }],
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
