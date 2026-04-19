# Engine/data/

Static data tables used by the SIRR engine. These are **not** compute modules — they are reference tables loaded at runtime by modules and analysis tools.

## Files

| File | Source | Description |
|------|--------|-------------|
| `gemini_mapping_tables.json` | Gemini Round 2 | 6 cross-tradition mapping tables: elemental (28 rows), planetary (34 rows), modality (10 rows), lineage_rubric (65 modules with derivedness scores), number_archetypes (1-12), compatibility_matrix (9x9 Hisab al-Nim) |

## Gemini Mapping Tables

### 1. `elemental_mapping` (28 rows)
Maps system-specific elements (Chinese 五行, Western Fire/Earth/Air/Water, Islamic نار/تراب/هواء/ماء, Vedic tattwa, Tibetan, Japanese) to unified SIRR element buckets.

### 2. `planetary_mapping` (34 rows)
Cross-tradition planetary correspondences: Western, Vedic, Chinese, Islamic, Babylonian, Mahabote, Human Design, Gene Keys, and timing systems (Firdaria, planetary hours).

### 3. `modality_mapping` (10 rows)
Qualitative modes: Cardinal/Fixed/Mutable, Active/Receptive, Expansive/Contractive, Generative/Destructive, Neutral.

### 4. `lineage_rubric` (65 modules)
Module derivedness scoring. Each entry has:
- `derivedness` (0.0–1.0): how much the module depends on upstream output vs. raw profile input
- `parent`: upstream module or input source
- `independence_group`: which SYSTEM_TO_GROUP category

**Used by `synthesis.py`**: modules with `derivedness > 0.7` get excluded from convergence vote counting to prevent inflated agreement from correlated outputs.

### 5. `number_archetypes` (keys 1-12)
Universal number meanings across Western, Islamic, Vedic, and Chinese traditions.

### 6. `compatibility_matrix` (9x9)
Hisab al-Nim planetary compatibility. Values: 1 = harmonious, -1 = inharmonious, 0 = neutral. Planets: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu.
