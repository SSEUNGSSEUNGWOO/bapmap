import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About | Bapmap",
  description: "About Bapmap — a Korean restaurant guide built by a local who actually eats out a lot.",
  alternates: {
    canonical: "https://bapmap.com/about",
  },
};

export default function AboutLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
