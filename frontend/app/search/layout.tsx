import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Search | Bapmap",
  description: "Search Korean restaurants and food spots on Bapmap.",
  robots: {
    index: false,
    follow: true,
  },
  alternates: {
    canonical: "https://bapmap.com/search",
  },
};

export default function SearchLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
