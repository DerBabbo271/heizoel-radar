#!/usr/bin/env python3
"""Inspect HeizOel24 XML structure without publishing or guessing prices."""
import json
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

data = json.loads(Path("prices.json").read_text(encoding="utf-8"))
assert data["postal_code"] == "90552" and data["quantity_liters"] == 2000
params = urllib.parse.urlencode({
    "zipCode": "90552", "litre": 2000,
    "unloadingpoints": 1, "oilgrade": "standard",
})
url = "https://www.heizoel24.de/DailyPriceXml.ashx?" + params
request = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (compatible; PersonalHeatingOilMonitor/1.0)",
    "Accept": "application/xml, text/xml, */*",
})
try:
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read(120000)
        print("HTTP status:", response.status)
        print("Content type:", response.headers.get("Content-Type", "unknown"))
        print("Body length:", len(body))
    root = ET.fromstring(body)
    print("XML root tag:", root.tag)
    print("XML elements (tag, text length, text preview):")
    for el in root.iter():
        val = (el.text or "").strip()
        # Diagnostic only: reveal compact values to identify units and fields.
        # Do not dump full XML or any attributes that could contain tokens.
        print(" -", el.tag, "|", len(val), "|", val[:90])
except (urllib.error.URLError, ET.ParseError, ValueError) as exc:
    print("Provider response error:", type(exc).__name__, str(exc)[:180])
    raise SystemExit(1)
print("Diagnostic only. No prices published; quantity, taxes and delivery still require verification.")
