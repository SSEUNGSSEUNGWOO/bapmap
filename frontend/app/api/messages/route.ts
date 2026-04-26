import { supabase } from "@/lib/supabase";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const { message, email } = await req.json();
  if (!message || typeof message !== "string" || message.trim().length < 3) {
    return NextResponse.json({ error: "Too short" }, { status: 400 });
  }
  if (message.length > 500) {
    return NextResponse.json({ error: "Too long" }, { status: 400 });
  }
  if (email && (typeof email !== "string" || email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))) {
    return NextResponse.json({ error: "Invalid email" }, { status: 400 });
  }
  await supabase.from("messages").insert({
    message: message.trim(),
    email: email || null,
  });
  return NextResponse.json({ ok: true });
}
