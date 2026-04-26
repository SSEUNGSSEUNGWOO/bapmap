"use client";

type Message = {
  id: string;
  message: string;
  reply: string;
};

export default function MessageTicker({ messages }: { messages: Message[] }) {
  if (!messages || messages.length === 0) return null;

  // 충분한 길이를 위해 3번 반복
  const items = [...messages, ...messages, ...messages];

  return (
    <div
      className="w-full overflow-hidden border-b border-t"
      style={{
        background: "var(--ink)",
        borderColor: "rgba(255,255,255,0.08)",
        height: "44px",
      }}
    >
      <div
        className="flex items-center h-full whitespace-nowrap"
        style={{
          animation: "ticker 60s linear infinite",
          willChange: "transform",
        }}
      >
        {items.map((msg, i) => (
          <span key={i} className="inline-flex items-center gap-3 px-8">
            <span className="text-xs" style={{ color: "rgba(255,255,255,0.5)" }}>
              "{msg.message}"
            </span>
            {msg.reply && (
              <>
                <span style={{ color: "var(--orange)", fontSize: "10px" }}>→</span>
                <span className="text-xs font-semibold" style={{ color: "rgba(255,255,255,0.85)" }}>
                  {msg.reply}
                </span>
              </>
            )}
            <span style={{ color: "rgba(255,255,255,0.15)", margin: "0 8px" }}>✦</span>
          </span>
        ))}
      </div>

      <style>{`
        @keyframes ticker {
          0% { transform: translateX(0); }
          100% { transform: translateX(-33.333%); }
        }
      `}</style>
    </div>
  );
}
