#!/usr/bin/env python3
"""Quick validation: ensure all 50-subject cities resolve via geocoder."""
import sys
sys.path.insert(0, ".")

from sirr_core.natal_chart import geocode

# All cities from HANDOFF_GEOCODING_BRIDGE.md
TEST_CITIES = [
    ("Braunau, Austria", 48.2567, 13.0333, 1.0),
    ("Gori, Georgia", 41.9826, 44.1132, 3.0),
    ("Shaoshan, China", 27.9152, 112.4937, 8.0),
    ("Predappio, Italy", 44.1019, 11.9819, 1.0),
    ("Mecca, Saudi Arabia", 21.3891, 39.8579, 3.0),
    ("Florence, Italy", 43.7696, 11.2558, 1.0),
    ("Trier, Germany", 49.7490, 6.6371, 1.0),
    ("Rocken, Germany", 51.2500, 12.1167, 1.0),
    ("Kesswil, Switzerland", 47.5960, 9.3167, 1.0),
    ("Freiberg, Czech Republic", 49.8528, 18.3467, 1.0),
    ("Edmonton, Canada", 53.5461, -113.4938, -7.0),
    ("Vienna, Austria", 48.2082, 16.3738, 1.0),
    ("New York, USA", 40.7128, -74.0060, -5.0),
    ("Brooklyn, USA", 40.6782, -73.9442, -5.0),
    ("Paris, France", 48.8566, 2.3522, 1.0),
    ("Tikrit, Iraq", 34.6137, 43.6789, 3.0),
    ("Balkh, Afghanistan", 36.7581, 66.8981, 4.5),
    ("Malmesbury, England", 51.5858, -2.0990, 0.0),
    ("Schonhausen, Germany", 52.6333, 12.0000, 1.0),
    ("Koboko, Uganda", 3.4141, 30.9603, 3.0),
    ("Qasr Abu Hadi, Libya", 31.1706, 16.5892, 2.0),
    ("Mangyongdae, Korea", 39.0050, 125.7289, 9.0),
    ("Valparaiso, Chile", -33.0472, -71.6127, -4.0),
    ("Khentii, Mongolia", 48.0000, 109.5000, 8.0),
    ("Pella, Macedon", 40.7617, 22.5217, 2.0),
    ("Sighisoara, Romania", 46.2197, 24.7956, 2.0),
    ("Shahrisabz, Uzbekistan", 39.0517, 66.8303, 5.0),
    ("Rheydt, Germany", 51.1622, 6.4456, 1.0),
    ("Munich, Germany", 48.1351, 11.5820, 1.0),
    ("Merkheuli, Georgia", 42.3833, 41.7833, 3.0),
    ("Leamington Spa, England", 52.2852, -1.5201, 0.0),
    ("Pokrovskoye, Russia", 57.7833, 64.1333, 5.0),
    ("Riyadh, Saudi Arabia", 24.7136, 46.6753, 3.0),
    ("Samarra, Iraq", 34.1959, 43.8750, 3.0),
    ("Damascus, Syria", 33.5138, 36.2765, 2.0),
    ("Pozarevac, Serbia", 44.6225, 21.1869, 1.0),
    ("Kutama, Zimbabwe", -17.3167, 30.1500, 2.0),
    ("Ferrol, Spain", 43.4840, -8.2328, 0.0),
    ("Ulyanovsk, Russia", 54.3142, 48.4031, 4.0),
    ("Antium, Rome", 41.4480, 12.6700, 1.0),
    ("Nyirbator, Hungary", 47.8369, 22.1294, 1.0),
    ("Ajaccio, Corsica", 41.9192, 8.7386, 1.0),
]

passed = 0
failed = 0

for city, exp_lat, exp_lng, exp_tz in TEST_CITIES:
    result = geocode(city)
    if result is None:
        print(f"FAIL: {city} → None (not found)")
        failed += 1
    elif abs(result.utc_offset - exp_tz) > 0.01:
        print(f"FAIL: {city} → tz={result.utc_offset}, expected={exp_tz}")
        failed += 1
    else:
        passed += 1

print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed out of {len(TEST_CITIES)}")
if failed == 0:
    print("✅ ALL CITIES RESOLVED SUCCESSFULLY")
else:
    print("❌ SOME CITIES FAILED")
