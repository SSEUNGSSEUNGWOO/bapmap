import { NextResponse } from "next/server";
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

export async function POST(req: Request) {
  const secret = req.headers.get("x-notify-secret");
  if (!secret || secret !== process.env.NOTIFY_SECRET) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { email, message, reply } = await req.json();

  if (!email || !reply) {
    return NextResponse.json({ error: "Missing fields" }, { status: 400 });
  }

  const safeMessage = escapeHtml(String(message));
  const safeReply = escapeHtml(String(reply));

  await resend.emails.send({
    from: "Bapmap <hello@bapmap.com>",
    to: email,
    subject: "Your question was answered on Bapmap ✦",
    html: `
      <div style="font-family: Georgia, serif; max-width: 520px; margin: 0 auto; padding: 40px 24px; color: #1a1a1a;">
        <p style="font-size: 11px; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: #f5a623; margin-bottom: 32px;">Bapmap</p>

        <p style="font-size: 18px; font-weight: 700; margin-bottom: 24px; line-height: 1.3;">
          Your question just went live on the site.
        </p>

        <div style="border-left: 3px solid #f5a623; padding-left: 16px; margin-bottom: 12px;">
          <p style="font-size: 13px; color: #888; margin: 0 0 6px 0;">You asked:</p>
          <p style="font-size: 15px; font-style: italic; margin: 0; color: #444;">"${safeMessage}"</p>
        </div>

        <div style="border-left: 3px solid #1a1a1a; padding-left: 16px; margin-bottom: 32px;">
          <p style="font-size: 13px; color: #888; margin: 0 0 6px 0;">Bapmap says:</p>
          <p style="font-size: 15px; font-weight: 600; margin: 0;">${safeReply}</p>
        </div>

        <a href="https://bapmap.com" style="display: inline-block; background: #f5a623; color: #fff; text-decoration: none; padding: 12px 24px; border-radius: 999px; font-size: 13px; font-weight: 700;">
          See it on Bapmap →
        </a>

        <p style="font-size: 11px; color: #bbb; margin-top: 40px;">
          You're getting this because you left a question on bapmap.com
        </p>
      </div>
    `,
  });

  return NextResponse.json({ ok: true });
}
