#!/usr/bin/env python3
"""Safe placeholder. No verified price provider is connected yet."""
import json
from pathlib import Path

path = Path(__file__).with_name("prices.json")
data = json.loads(path.read_text(encoding="utf-8"))
assert data["postal_code"] == "90552"
assert data["quantity_liters"] == 2000
print("Price source not configured; status:", data["status"])
# Do not overwrite verified prices or invent market data.
