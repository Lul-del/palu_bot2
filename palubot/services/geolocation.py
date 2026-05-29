from math import asin, cos, radians, sin, sqrt


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


def find_nearest_centers(lat: float, lon: float) -> list[dict]:
    centers = [
        {"name": "Centre de Santé Akpakpa", "lat": 6.366, "lon": 2.445, "phone": "+229 01 90 00 00 01"},
        {"name": "Hôpital de Zone Suru-Léré", "lat": 6.370, "lon": 2.409, "phone": "+229 01 90 00 00 02"},
        {"name": "CNHU-HKM", "lat": 6.365, "lon": 2.431, "phone": "+229 01 90 00 00 03"},
    ]

    enriched = []
    for c in centers:
        dist = _haversine_km(lat, lon, c["lat"], c["lon"])
        enriched.append({**c, "distance_km": round(dist, 2)})

    return sorted(enriched, key=lambda x: x["distance_km"])[:3]
