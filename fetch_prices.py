#!/usr/bin/env python3
"""Daily HeizOel24 standard heating oil quote for 90552 / 2000 L.
Unofficial XML endpoint; fail closed and retain previous observation.
"""
import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

ZIP = "90552"
LITERS = 2000
FILE = Path("prices.json")
HISTORY = Path("history.json")
query = urllib.parse.urlencode({"zipCode": ZIP, "litre": LITERS, "unloadingpoints": 1, "oilgrade": "standard"})
url = "https://www.heizoel24.de/DailyPriceXml.ashx?" + query
req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0", "Accept":"application/xml"})
with urllib.request.urlopen(req, timeout=25) as res:
    if res.status != 200:
        raise RuntimeError(f"HTTP {res.status}")
    root = ET.fromstring(res.read(120000))
if root.tag != "result" or root.findtext("plz") != ZIP:
    raise ValueError("Unexpected postal code or XML root")
if root.findtext("taxRate") != "19":
    raise ValueError("Unexpected tax rate")
delivery = next((e for e in root.findall("./deliveries/delivery")
                 if e.get("unloadingPoints") == "1" and e.get("litre") == str(LITERS)), None)
if delivery is None:
    raise ValueError("Matching delivery not found")
matches = [e for e in delivery.findall("price") if e.get("oilGrade") == "Heizöl Standard Schwefelarm"]
if len(matches) != 1:
    raise ValueError("Standard oil price missing or ambiguous")
node = matches[0]
order_url = node.get("orderLink", "")
if not order_url.startswith("https://www.heizoel24.de/"):
    raise ValueError("Missing official offer URL")
try:
    price = Decimal((node.text or "").strip().replace(",", "."))
except InvalidOperation as exc:
    raise ValueError("Invalid price") from exc
if not Decimal("20") < price < Decimal("500"):
    raise ValueError("Price outside conservative sanity bounds")
now = datetime.now(timezone.utc)
history = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
history = [h for h in history if h.get("date") != now.date().isoformat()]
previous = [h for h in history if h.get("date", "") < now.date().isoformat()]
prev = max(previous, key=lambda h: h["date"]) if previous else None
change = (price - Decimal(str(prev["price_per_100_liters_eur"]))) if prev else None
history.append({"date": now.date().isoformat(), "price_per_100_liters_eur": float(price)})
history = sorted(history, key=lambda h: h["date"])[-120:]
total = (price * Decimal(LITERS) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
out = {
    "schema_version": 1, "postal_code": ZIP, "quantity_liters": LITERS,
    "product": "Heizöl Standard Schwefelarm", "currency": "EUR",
    "status": "ok", "price_per_100_liters_eur": float(price),
    "total_price_eur": float(total),
    "change_day_eur": float(change) if change is not None else None,
    "source_url": order_url, "checked_at": now.isoformat(),
    "price_basis": "HeizOel24 displayed consumer offer, EUR per 100 L; verify checkout for any special delivery conditions",
    "note": "Indicative offer; confirm final price and delivery conditions before ordering."
}
FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Verified standard offer for {ZIP}, {LITERS} L: {price} EUR/100L; total {total} EUR")
