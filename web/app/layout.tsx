import type { Metadata } from "next";
import { Playfair_Display, Source_Sans_3 } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import Header from "@/components/Header";

const playfair = Playfair_Display({ subsets: ["latin"], variable: "--font-playfair", weight: ["400","500","600","700","800","900"] });
const sourceSans = Source_Sans_3({ subsets: ["latin"], variable: "--font-source", weight: ["300","400","600"] });

export const metadata: Metadata = {
  title: "Bapmap — Eat where Koreans actually eat",
  description: "Local Korean restaurant guide for travelers. Real spots, honest picks.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${playfair.variable} ${sourceSans.variable}`}>
      <body>
        <Script src="https://www.googletagmanager.com/gtag/js?id=G-ND1BLDXFQL" strategy="afterInteractive" />
        <Script id="google-analytics" strategy="afterInteractive">{`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'G-ND1BLDXFQL');
        `}</Script>
        <Header />
        <main>{children}</main>
        <footer style={{ borderTop: "1px solid var(--border)", marginTop: "6rem", padding: "2rem 1rem", textAlign: "center", fontSize: "0.8rem", color: "var(--muted)" }}>
          © 2026 Bapmap · Korean Food, Mapped for You
        </footer>
      </body>
    </html>
  );
}
