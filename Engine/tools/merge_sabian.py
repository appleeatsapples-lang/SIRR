#!/usr/bin/env python3
"""Merge 4 Sabian Symbol chunks into constants.json"""
import json, glob

base = "/Users/moatq/Desktop/sirr_new_systems/expansion/gemini_extractions"
chunks = sorted(glob.glob(f"{base}/sabian_chunk*.json"))

merged = {}
for path in chunks:
    with open(path) as f:
        data = json.load(f)
    print(f"  {path.split('/')[-1]}: {len(data)} entries")
    merged.update(data)

print(f"\nTotal unique entries: {len(merged)}")

# Verify all 360
signs = ["ARI","TAU","GEM","CAN","LEO","VIR","LIB","SCO","SAG","CAP","AQU","PIS"]
for sign in signs:
    count = sum(1 for k in merged if k.startswith(sign+"-"))
    status = "✅" if count == 30 else f"❌ ({count})"
    print(f"  {sign}: {count} {status}")

# Golden fixture: LIB-1
lib1 = merged["LIB-1"]
assert "butterfly" in lib1["symbol"].lower(), f"LIB-1 FAILED: {lib1['symbol'][:50]}"
print(f"\n✅ LIB-1 golden fixture: butterfly confirmed")

# Load and update constants.json
cpath = "/Users/moatq/Desktop/sirr_new_systems/constants.json"
with open(cpath) as f:
    constants = json.load(f)

constants["sabian"] = {
    "version": "rudhyar-v2-gemini-360",
    "source": "Dane Rudhyar, An Astrological Mandala (1973). Extracted via Gemini, verified against LIB-1.",
    "symbols": merged
}

with open(cpath, "w") as f:
    json.dump(constants, f, ensure_ascii=False, indent=2)

print(f"\n✅ constants.json updated: {len(merged)} Sabian Symbols integrated")
