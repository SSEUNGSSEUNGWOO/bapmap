"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

type Lang = "en" | "ja";
const LanguageContext = createContext<{ lang: Lang; setLang: (l: Lang) => void }>({
  lang: "en",
  setLang: () => {},
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const isJaPath = pathname?.startsWith("/ja");
  const [lang, setLangState] = useState<Lang>(isJaPath ? "ja" : "en");

  useEffect(() => {
    if (pathname?.startsWith("/ja")) {
      setLangState("ja");
    } else {
      const saved = localStorage.getItem("bapmap_lang") as Lang | null;
      if (saved === "en") setLangState("en");
      else setLangState("en");
    }
  }, [pathname]);

  const setLang = (l: Lang) => {
    setLangState(l);
    localStorage.setItem("bapmap_lang", l);
    if (l === "ja" && !pathname?.startsWith("/ja")) {
      router.push(`/ja${pathname}`);
    } else if (l === "en" && pathname?.startsWith("/ja")) {
      router.push(pathname.replace(/^\/ja/, "") || "/");
    }
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLang() {
  const ctx = useContext(LanguageContext);
  const p = (path: string) => ctx.lang === "ja" ? `/ja${path}` : path;
  return { ...ctx, p };
}
