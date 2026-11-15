// Scriptable – Heizöl-Radar, rechteckiges Sperrbildschirm-Widget
const URL = "https://raw.githubusercontent.com/DerBabbo271/heizoel-radar/main/prices.json";
const LINK = "https://www.heizoel24.de/heizoelpreise/bayern/nuernberger-land/roethenbach-90552";
const w = new ListWidget();
w.url = LINK;
w.setPadding(3, 7, 3, 7);
const title = w.addText("🛢 HEIZÖL · 90552");
title.font = Font.boldSystemFont(11);
let data = null;
try {
  const req = new Request(URL);
  req.timeoutInterval = 12;
  data = await req.loadJSON();
} catch (err) {
  console.log("Abruf fehlgeschlagen: " + err);
}
const good = data && data.status === "ok" &&
  data.postal_code === "90552" &&
  data.quantity_liters === 2000 &&
  typeof data.price_per_100_liters_eur === "number" &&
  Number.isFinite(data.price_per_100_liters_eur) &&
  data.price_per_100_liters_eur > 0 &&
  typeof data.total_price_eur === "number" &&
  Number.isFinite(data.total_price_eur) &&
  data.total_price_eur > 0 &&
  typeof data.source_url === "string" &&
  data.source_url.startsWith("https://") &&
  typeof data.checked_at === "string" &&
  Number.isFinite(Date.parse(data.checked_at)) &&
  Date.parse(data.checked_at) <= Date.now() + 300000 &&
  Date.now() - Date.parse(data.checked_at) < 36 * 3600000;
const euro = n => n.toLocaleString("de-DE", {style:"currency", currency:"EUR"});
const price = w.addText(good ? euro(data.price_per_100_liters_eur) + "/100 L" : "Preis nicht verfügbar");
price.font = Font.boldSystemFont(13);
const detail = w.addText(good ? "2.000 L · " + euro(data.total_price_eur) : "2.000 L · Datenquelle fehlt");
detail.font = Font.systemFont(10);
if (good && typeof data.change_day_eur === "number" && Number.isFinite(data.change_day_eur)) {
  const trend = w.addText((data.change_day_eur < 0 ? "↓ " : data.change_day_eur > 0 ? "↑ " : "→ ") + euro(Math.abs(data.change_day_eur)) + "/100 L");
  trend.font = Font.systemFont(9);
}
if (good) w.url = data.source_url;
w.refreshAfterDate = new Date(Date.now() + 60 * 60 * 1000);
if (config.runsInWidget) Script.setWidget(w);
else await w.presentAccessoryRectangular();
Script.complete();
