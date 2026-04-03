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

async function rewriteQuery(raw: string) {
  const res = await anthropic.messages.create({
    model: "claude-haiku-4-5-20251001",
    max_tokens: 120,
    system: `Extract from the user query:
1. "query": clean search query in English (max 15 words)
2. "region": area in Korea if mentioned — null if not
3. "category": food type if mentioned — null if not
4. "needs_spots": true if the user is asking for place/restaurant recommendations, false if it's a general question about food, culture, or Korea (e.g. "what is tteokbokki", "how spicy is buldak", "is Monday busy")
Return JSON only.`,
    messages: [{ role: "user", content: raw }],
  });
  try {
    return JSON.parse((res.content[0] as { text: string }).text);
  } catch {
    return { query: raw, region: null, category: null, needs_spots: true };
  }
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
        // 1. Rewrite query
        const rewritten = await rewriteQuery(userQuery);

        // 2. Embed
        const embRes = await openai.embeddings.create({
          model: "text-embedding-3-small",
          input: rewritten.query.replace(/\n/g, " "),
        });
        const embedding = embRes.data[0].embedding;

        // 3. Search in parallel
        const [spotsRes, guidesRes] = await Promise.all([
          sb.rpc("hybrid_search_spots", {
            query_text: rewritten.query,
            query_embedding: embedding,
            match_count: 5,
            filter_region: rewritten.region || null,
            filter_category: rewritten.category || null,
          }),
          sb.rpc("search_guides", {
            query_embedding: embedding,
            match_threshold: 0.3,
            match_count: 2,
          }),
        ]);

        const spots = spotsRes.data || [];
        const guides = guidesRes.data || [];

        // Send spot cards only when user is asking for recommendations
        if (rewritten.needs_spots !== false) {
          const published = spots.filter((s: Record<string, unknown>) => s.status === "업로드완료");
          const comingSoon = spots.filter((s: Record<string, unknown>) => s.status !== "업로드완료").slice(0, 2);
          const toShow = [...published, ...comingSoon].slice(0, 5);
          if (toShow.length > 0) send({ type: "spots", data: toShow });
        }

        // 4. Build context
        const spotsContext = spots.slice(0, 5).map((s: Record<string, unknown>) => {
          const name = (s.english_name || s.name) as string;
          const slug = name.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
          const memo = String(s.memo || "").slice(0, 200);
          if (s.status === "업로드완료") {
            return `[SPOT] ${name} — ${s.category} · ${s.region || s.city} · ★${s.rating} · ${s.price_level}\nLink: /spots/${slug}${memo ? `\nWhy: ${memo}` : ""}`;
          }
          return `[SPOT - coming soon] ${name} (${s.category} · ${s.region || s.city})`;
        }).join("\n\n");

        const guidesContext = guides.map((g: Record<string, unknown>) =>
          `[GUIDE] ${g.title}\n${String(g.content || "").slice(0, 300)}`
        ).join("\n\n");

        const context = [spotsContext, guidesContext].filter(Boolean).join("\n\n---\n\n");

        // 5. Stream answer with full conversation history
        const msgStream = anthropic.messages.stream({
          model: "claude-haiku-4-5-20251001",
          max_tokens: 300,
          system: `You are Bapmap's food guide for English-speaking tourists in Korea.
${context ? `\nRelevant context:\n${context}\n` : ""}
Rules:
- ONLY answer questions about Korean food, restaurants, travel in Korea, neighborhoods, K-culture related to food/places.
- If unrelated (coding, politics, math, etc.), respond: "I'm only here to help with food and travel in Korea 🍜"
- For every spot you mention, explain WHY — a specific dish, vibe, price, or what makes it stand out.
- Reference spots with markdown links: [Name](/spots/slug)
- Friendly, specific, concise. Max 180 words.`,
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
