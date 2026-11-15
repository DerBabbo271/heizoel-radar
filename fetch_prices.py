#!/usr/bin/env python3
"""Diagnose the unofficial HeizOel24 endpoint without publishing unverified prices."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

data = json.loads(Path("prices.json").read_text(encoding="utf-8"))
assert data["postal_code"] == "90552" and data["quantity_liters"] == 2000

params = urllib.parse.urlencode({
    "zipCode": "90552",
    "litre": 2000,
    "unloadingpoints": 1,
    "oilgrade": "standard",
})
url = "https://www.heizoel24.de/DailyPriceXml.ashx?" + params
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (compatible; PersonalHeatingOilMonitor/1.0)",
    "Accept": "application/json, application/xml, text/xml, */*",
})
try:
    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read(120000).decode("utf-8", errors="replace")
        print("HTTP status:", response.status)
        print("Content type:", response.headers.get("Content-Type", "unknown"))
        print("Body length:", len(body))
        try:
            parsed = json.loads(body)
            print("JSON root keys:", sorted(parsed.keys()) if isinstance(parsed, dict) else type(parsed).__name__)
            if isinstance(parsed, dict) and isinstance(parsed.get("result"), dict):
                print("Result keys:", sorted(parsed["result"].keys()))
        except ValueError:
            print("Response is not JSON; no price accepted.")
except urllib.error.HTTPError as exc:
    print("Provider HTTP error:", exc.code)
    raise SystemExit(1)
except Exception as exc:
    print("Provider connection failed:", type(exc).__name__, str(exc)[:160])
    raise SystemExit(1)

print("Diagnostic only. No price published until response structure, units, taxes and delivery charges are verified.")
