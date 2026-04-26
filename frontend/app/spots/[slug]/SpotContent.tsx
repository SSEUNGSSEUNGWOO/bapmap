"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useLang } from "@/lib/LanguageContext";

const GOOD_FOR_JA: Record<string, string> = {
  "Solo dining": "一人飯",
  "Groups": "グループ",
  "Date night": "デート",
  "Quick lunch": "ランチ",
  "Late night": "深夜営業",
  "Vegetarian-friendly": "ベジタリアン向け",
  "Budget-friendly": "リーズナブル",
  "Special occasion": "記念日・特別な日",
  "No reservations needed": "予約不要",
  "Reservation recommended": "予約推奨",
};

const markdownComponents = {
  h1: ({ children }: { children?: React.ReactNode }) => (
    <h1 className="font-display mb-4" style={{ fontSize: "1.5rem", color: "var(--ink)", letterSpacing: "-0.02em", lineHeight: 1.2 }}>{children}</h1>
  ),
  h2: ({ children }: { children?: React.ReactNode }) => (
    <h2 className="font-bold mt-10 mb-4 pl-4" style={{ fontSize: "1.05rem", color: "var(--ink)", borderLeft: "3px solid var(--orange)", letterSpacing: "-0.01em" }}>{children}</h2>
  ),
  h3: ({ children }: { children?: React.ReactNode }) => (
    <h3 className="font-bold mt-6 mb-2" style={{ fontSize: "0.95rem", color: "var(--ink)" }}>{children}</h3>
  ),
  p: ({ children }: { children?: React.ReactNode }) => (
    <p className="mb-6" style={{ fontSize: "1rem", lineHeight: "1.9", color: "var(--muted)" }}>{children}</p>
  ),
  strong: ({ children }: { children?: React.ReactNode }) => (
    <strong style={{ color: "var(--ink)", fontWeight: 600 }}>{children}</strong>
  ),
  ul: ({ children }: { children?: React.ReactNode }) => (
    <ul className="mb-6 space-y-1 pl-4" style={{ color: "var(--muted)", listStyleType: "disc" }}>{children}</ul>
  ),
  ol: ({ children }: { children?: React.ReactNode }) => (
    <ol className="mb-6 space-y-1 pl-4" style={{ color: "var(--muted)", listStyleType: "decimal" }}>{children}</ol>
  ),
  li: ({ children }: { children?: React.ReactNode }) => (
    <li style={{ fontSize: "1rem", lineHeight: "1.9" }}>{children}</li>
  ),
  hr: () => <div className="border-t border-[var(--border)] my-8" />,
  table: ({ children }: { children?: React.ReactNode }) => (
    <div className="overflow-x-auto mb-6 rounded-xl" style={{ border: "1px solid var(--border)" }}>
      <table className="w-full text-sm" style={{ borderCollapse: "collapse" }}>{children}</table>
    </div>
  ),
  th: ({ children }: { children?: React.ReactNode }) => (
    <th className="py-2 px-4 text-left text-xs font-bold tracking-wide uppercase" style={{ background: "var(--surface)", color: "var(--ink)", borderBottom: "1px solid var(--border)" }}>{children}</th>
  ),
  td: ({ children }: { children?: React.ReactNode }) => (
    <td className="py-2 px-4" style={{ borderBottom: "1px solid var(--border)", color: "var(--muted)" }}>{children}</td>
  ),
  a: ({ href, children }: { href?: string; children?: React.ReactNode }) => (
    <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: "var(--orange)", textDecoration: "underline" }}>{children}</a>
  ),
};

type Props = {
  content?: string;
  content_ja?: string;
  what_to_order?: string[];
  what_to_order_ja?: string[];
  good_for?: string[];
};

export default function SpotContent({ content, content_ja, what_to_order, what_to_order_ja, good_for }: Props) {
  const { lang } = useLang();
  const isJa = lang === "ja";
  const body = isJa && content_ja ? content_ja : content;
  const orderItems = isJa && what_to_order_ja?.length ? what_to_order_ja : what_to_order;

  return (
    <>
      {/* What to Order */}
      {Array.isArray(orderItems) && orderItems.length > 0 && (
        <div className="mb-8 p-5 rounded-2xl" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-3" style={{ color: "var(--orange)" }}>
            {isJa ? "おすすめメニュー" : "What to Order"}
          </p>
          <ul className="space-y-2">
            {orderItems.map((item: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm" style={{ color: "var(--ink)" }}>
                <span style={{ color: "var(--orange)", flexShrink: 0 }}>✦</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Good For */}
      {Array.isArray(good_for) && good_for.length > 0 && (
        <div className="mb-8">
          <p className="text-xs font-bold tracking-[0.2em] uppercase mb-3" style={{ color: "var(--orange)" }}>
            {isJa ? "こんな方に" : "Good For"}
          </p>
          <div className="flex flex-wrap gap-2">
            {good_for.map((tag: string, i: number) => (
              <span key={i} className="text-xs font-semibold px-3 py-1.5 rounded-full" style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--border)" }}>
                {isJa ? (GOOD_FOR_JA[tag] || tag) : tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 본문 */}
      {body ? (
        <div className="mb-10 prose-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
            {body}
          </ReactMarkdown>
        </div>
      ) : (
        <p className="mb-10" style={{ color: "var(--muted)" }}>Content coming soon.</p>
      )}
    </>
  );
}
