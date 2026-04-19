#!/usr/bin/env python3
"""Timing consensus analysis — what do cycle/timing modules agree on?

Reads output.json and extracts current-cycle indicators from timing modules.
Derives a consensus theme (EXPANSIVE/CONTRACTIVE/TRANSITIONAL) and compares
to Grok's manual reference.

Writes timing_consensus.json to Engine/.
"""

import json
import os
import sys

ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(ENGINE, "output.json")
OUT_PATH = os.path.join(ENGINE, "timing_consensus.json")

# Timing modules and the fields that indicate current-cycle state
TIMING_MODULES = {
    "firdaria": {
        "fields": ["major_planet", "combined"],
        "extract": lambda d: d.get("major_planet", ""),
    },
    "vimshottari": {
        "fields": ["current_maha_dasha"],
        "extract": lambda d: d.get("current_maha_dasha", ""),
    },
    "profection": {
        "fields": ["house"],
        "extract": lambda d: str(d.get("house", "")),
    },
    "personal_year": {
        "fields": ["personal_year"],
        "extract": lambda d: str(d.get("personal_year", "")),
    },
    "biorhythm": {
        "fields": ["physical_level", "emotional_level", "intellectual_level"],
        "extract": lambda d: f"phys={d.get('physical_level','?')}, emot={d.get('emotional_level','?')}, intel={d.get('intellectual_level','?')}",
    },
    "steiner_cycles": {
        "fields": ["cycle_number"],
        "extract": lambda d: str(d.get("cycle_number", "")),
    },
    "yogini_dasha": {
        "fields": ["current_yogini", "current_yogini_planet"],
        "extract": lambda d: d.get("current_yogini", d.get("current_yogini_planet", "")),
    },
    "tarot_year": {
        "fields": ["card_number", "card_name"],
        "extract": lambda d: f"{d.get('card_number', '?')} ({d.get('card_name', '?')})",
    },
    "zodiacal_releasing": {
        "fields": ["l1_sign", "l1_planet"],
        "extract": lambda d: d.get("l1_sign", d.get("l1_planet", "")),
    },
    "dorothean_chronocrators": {
        "fields": ["current_l1", "current_l1_planet"],
        "extract": lambda d: d.get("current_l1", d.get("current_l1_planet", "")),
    },
    "solar_return": {
        "fields": ["sun_house"],
        "extract": lambda d: f"Sun in House {d.get('sun_house', '?')}",
    },
}

# Contractive indicators (Saturn, 7, houses 6/8/12, Rahu, etc.)
CONTRACTIVE_SIGNALS = {
    "Saturn", "Rahu", "8", "12", "6", "4",
    "Death", "Tower", "Hermit",
}

# Expansive indicators (Jupiter, Sun, 1, 5, 9, Venus, etc.)
EXPANSIVE_SIGNALS = {
    "Jupiter", "Sun", "Venus", "1", "5", "9", "10",
    "World", "Empress", "Star", "Wheel",
}


QUALITY_TO_SIGNAL = {
    "malefic": "CONTRACTIVE",
    "challenging": "CONTRACTIVE",
    "benefic": "EXPANSIVE",
    "mixed": "NEUTRAL",
    "neutral": "NEUTRAL",
}


def classify_signal(value: str, period_quality: str = None) -> str:
    """Classify a timing value as EXPANSIVE, CONTRACTIVE, or NEUTRAL.

    If period_quality is available (from module metadata), use it directly.
    Otherwise fall back to keyword matching.
    """
    if period_quality and period_quality in QUALITY_TO_SIGNAL:
        return QUALITY_TO_SIGNAL[period_quality]
    for sig in CONTRACTIVE_SIGNALS:
        if sig.lower() in value.lower():
            return "CONTRACTIVE"
    for sig in EXPANSIVE_SIGNALS:
        if sig.lower() in value.lower():
            return "EXPANSIVE"
    return "NEUTRAL"


def main():
    output = None
    with open(OUTPUT_PATH) as f:
        output = json.load(f)

    results = output.get("results", [])
    result_map = {r.get("id"): r for r in results}

    timing_readings = []
    contractive = 0
    expansive = 0
    neutral = 0

    for mod_id, config in TIMING_MODULES.items():
        mod = result_map.get(mod_id)
        if not mod:
            timing_readings.append({
                "module": mod_id,
                "status": "NOT_FOUND",
                "value": None,
                "signal": None,
            })
            continue

        data = mod.get("data", {})
        value = config["extract"](data)
        pq = data.get("period_quality")
        signal = classify_signal(str(value), pq)

        if signal == "CONTRACTIVE":
            contractive += 1
        elif signal == "EXPANSIVE":
            expansive += 1
        else:
            neutral += 1

        reading = {
            "module": mod_id,
            "status": "OK",
            "value": value,
            "signal": signal,
            "certainty": mod.get("certainty", "UNKNOWN"),
        }
        if pq:
            reading["period_quality"] = pq
        timing_readings.append(reading)

    total = contractive + expansive + neutral
    found = sum(1 for t in timing_readings if t["status"] == "OK")

    # Derive consensus
    if total == 0:
        verdict = "INSUFFICIENT_DATA"
        ratio = "0/0"
    else:
        c_ratio = contractive / total
        e_ratio = expansive / total
        if c_ratio >= 0.5:
            verdict = "CONTRACTIVE"
        elif e_ratio >= 0.5:
            verdict = "EXPANSIVE"
        elif abs(c_ratio - e_ratio) < 0.15:
            verdict = "TRANSITIONAL"
        else:
            verdict = "MIXED"
        ratio = f"{contractive}/{total}"

    # Grok reference
    grok_reference = {
        "verdict": "CONTRACTIVE",
        "ratio": "7/11",
        "source": "Grok manual timing analysis (batch 21b)",
        "note": "Mercury/Sun firdaria (intellectual focus) + Rahu vimshottari (disruption) + 6th house profection (service/health)",
    }

    delta = "MATCHES" if verdict == grok_reference["verdict"] else "DIFFERS"

    result = {
        "modules_checked": len(TIMING_MODULES),
        "modules_found": found,
        "contractive": contractive,
        "expansive": expansive,
        "neutral": neutral,
        "verdict": verdict,
        "ratio": ratio,
        "grok_reference": grok_reference,
        "grok_delta": delta,
        "readings": timing_readings,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Timing Consensus: {verdict} ({ratio})")
    print(f"  Contractive: {contractive}, Expansive: {expansive}, Neutral: {neutral}")
    print(f"  Grok reference: {grok_reference['verdict']} ({grok_reference['ratio']})")
    print(f"  Delta: {delta}")
    for t in timing_readings:
        if t["status"] == "OK":
            print(f"    {t['module']}: {t['value']} -> {t['signal']}")
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
