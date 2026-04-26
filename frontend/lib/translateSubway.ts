export function translateSubway(text: string): string {
  if (!text) return text;
  return text
    .replace(/(\d+)\s*min walk/gi, "徒歩$1分")
    .replace(/\bStation\b/g, "駅")
    .replace(/,\s*/g, "、");
}

export function translateHours(text: string): string {
  if (!text) return text;
  return text
    .replace(/\bMonday\b/g, "月曜日")
    .replace(/\bTuesday\b/g, "火曜日")
    .replace(/\bWednesday\b/g, "水曜日")
    .replace(/\bThursday\b/g, "木曜日")
    .replace(/\bFriday\b/g, "金曜日")
    .replace(/\bSaturday\b/g, "土曜日")
    .replace(/\bSunday\b/g, "日曜日")
    .replace(/\bClosed\b/g, "定休日")
    .replace(/(\d{1,2}:\d{2})\s*AM/g, "午前$1")
    .replace(/(\d{1,2}:\d{2})\s*PM/g, "午後$1")
    .replace(/:\s/g, "：");
}
