import { supabase } from "@/lib/supabase";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const { message } = await req.json();
  if (!message || message.trim().length < 3) {
    return NextResponse.json({ error: "Too short" }, { status: 400 });
  }
  await supabase.from("messages").insert({ message: message.trim() });
  return NextResponse.json({ ok: true });
}
