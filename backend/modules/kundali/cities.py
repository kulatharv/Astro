import logging
import requests
from typing import Optional, Tuple, Dict, List, Any

logger = logging.getLogger(__name__)

CITIES: Dict[str, Dict[str, float]] = {
    # ── Maharashtra ──
    "Pune": {"lat": 18.5204, "lon": 73.8567, "timezone": 5.5, "elevation": 560.0},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "timezone": 5.5, "elevation": 14.0},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882, "timezone": 5.5, "elevation": 310.0},
    "Nashik": {"lat": 20.0059, "lon": 73.7897, "timezone": 5.5, "elevation": 584.0},
    "Aurangabad": {"lat": 19.8762, "lon": 75.3433, "timezone": 5.5, "elevation": 568.0},
    "Chhatrapati Sambhajinagar": {"lat": 19.8762, "lon": 75.3433, "timezone": 5.5, "elevation": 568.0},
    "Solapur": {"lat": 17.6868, "lon": 75.9064, "timezone": 5.5, "elevation": 458.0},
    "Kolhapur": {"lat": 16.7050, "lon": 74.2433, "timezone": 5.5, "elevation": 569.0},
    "Amravati": {"lat": 20.9374, "lon": 77.7796, "timezone": 5.5, "elevation": 343.0},
    "Nanded": {"lat": 19.1383, "lon": 77.3210, "timezone": 5.5, "elevation": 362.0},
    "Thane": {"lat": 19.2183, "lon": 72.9781, "timezone": 5.5, "elevation": 7.0},
    "Navi Mumbai": {"lat": 19.0330, "lon": 73.0297, "timezone": 5.5, "elevation": 9.0},

    # ── Delhi / NCR ──
    "Delhi": {"lat": 28.6139, "lon": 77.2090, "timezone": 5.5, "elevation": 216.0},
    "New Delhi": {"lat": 28.6139, "lon": 77.2090, "timezone": 5.5, "elevation": 216.0},
    "Noida": {"lat": 28.5355, "lon": 77.3910, "timezone": 5.5, "elevation": 200.0},
    "Gurgaon": {"lat": 28.4595, "lon": 77.0266, "timezone": 5.5, "elevation": 219.0},
    "Gurugram": {"lat": 28.4595, "lon": 77.0266, "timezone": 5.5, "elevation": 219.0},
    "Faridabad": {"lat": 28.4089, "lon": 77.3178, "timezone": 5.5, "elevation": 209.0},
    "Ghaziabad": {"lat": 28.6692, "lon": 77.4538, "timezone": 5.5, "elevation": 213.0},

    # ── Karnataka ──
    "Bangalore": {"lat": 12.9716, "lon": 77.5946, "timezone": 5.5, "elevation": 920.0},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "timezone": 5.5, "elevation": 920.0},
    "Mysore": {"lat": 12.2958, "lon": 76.6394, "timezone": 5.5, "elevation": 763.0},
    "Mysuru": {"lat": 12.2958, "lon": 76.6394, "timezone": 5.5, "elevation": 763.0},
    "Hubli": {"lat": 15.3647, "lon": 75.1240, "timezone": 5.5, "elevation": 671.0},
    "Mangalore": {"lat": 12.9141, "lon": 74.8560, "timezone": 5.5, "elevation": 22.0},
    "Belgaum": {"lat": 15.8497, "lon": 74.4977, "timezone": 5.5, "elevation": 762.0},
    "Gulbarga": {"lat": 17.3297, "lon": 76.8343, "timezone": 5.5, "elevation": 454.0},

    # ── Tamil Nadu ──
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "timezone": 5.5, "elevation": 6.0},
    "Madras": {"lat": 13.0827, "lon": 80.2707, "timezone": 5.5, "elevation": 6.0},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558, "timezone": 5.5, "elevation": 411.0},
    "Madurai": {"lat": 9.9252, "lon": 78.1198, "timezone": 5.5, "elevation": 136.0},
    "Salem": {"lat": 11.6643, "lon": 78.1460, "timezone": 5.5, "elevation": 278.0},
    "Trichy": {"lat": 10.7905, "lon": 78.7047, "timezone": 5.5, "elevation": 88.0},
    "Tirunelveli": {"lat": 8.7139, "lon": 77.7567, "timezone": 5.5, "elevation": 47.0},
    "Vellore": {"lat": 12.9165, "lon": 79.1325, "timezone": 5.5, "elevation": 216.0},

    # ── Andhra Pradesh / Telangana ──
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "timezone": 5.5, "elevation": 542.0},
    "Secunderabad": {"lat": 17.4399, "lon": 78.4983, "timezone": 5.5, "elevation": 542.0},
    "Visakhapatnam": {"lat": 17.6868, "lon": 83.2185, "timezone": 5.5, "elevation": 45.0},
    "Vijayawada": {"lat": 16.5062, "lon": 80.6480, "timezone": 5.5, "elevation": 23.0},
    "Tirupati": {"lat": 13.6288, "lon": 79.4192, "timezone": 5.5, "elevation": 161.0},
    "Warangal": {"lat": 17.9784, "lon": 79.5941, "timezone": 5.5, "elevation": 302.0},
    "Guntur": {"lat": 16.3067, "lon": 80.4365, "timezone": 5.5, "elevation": 33.0},
    "Nellore": {"lat": 14.4426, "lon": 79.9865, "timezone": 5.5, "elevation": 18.0},

    # ── Gujarat ──
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714, "timezone": 5.5, "elevation": 53.0},
    "Surat": {"lat": 21.1702, "lon": 72.8311, "timezone": 5.5, "elevation": 13.0},
    "Vadodara": {"lat": 22.3072, "lon": 73.1812, "timezone": 5.5, "elevation": 39.0},
    "Rajkot": {"lat": 22.3039, "lon": 70.8022, "timezone": 5.5, "elevation": 128.0},
    "Bhavnagar": {"lat": 21.7645, "lon": 72.1519, "timezone": 5.5, "elevation": 24.0},
    "Jamnagar": {"lat": 22.4707, "lon": 70.0577, "timezone": 5.5, "elevation": 20.0},
    "Gandhinagar": {"lat": 23.2156, "lon": 72.6369, "timezone": 5.5, "elevation": 81.0},

    # ── Rajasthan ──
    "Jaipur": {"lat": 26.9124, "lon": 75.7873, "timezone": 5.5, "elevation": 431.0},
    "Jodhpur": {"lat": 26.2389, "lon": 73.0243, "timezone": 5.5, "elevation": 231.0},
    "Udaipur": {"lat": 24.5854, "lon": 73.7125, "timezone": 5.5, "elevation": 598.0},
    "Kota": {"lat": 25.2138, "lon": 75.8648, "timezone": 5.5, "elevation": 271.0},
    "Ajmer": {"lat": 26.4499, "lon": 74.6399, "timezone": 5.5, "elevation": 486.0},
    "Bikaner": {"lat": 28.0229, "lon": 73.3119, "timezone": 5.5, "elevation": 242.0},

    # ── Uttar Pradesh / Uttarakhand ──
    "Lucknow": {"lat": 26.8467, "lon": 80.9462, "timezone": 5.5, "elevation": 123.0},
    "Varanasi": {"lat": 25.3176, "lon": 82.9739, "timezone": 5.5, "elevation": 81.0},
    "Kanpur": {"lat": 26.4499, "lon": 80.3319, "timezone": 5.5, "elevation": 126.0},
    "Agra": {"lat": 27.1767, "lon": 78.0081, "timezone": 5.5, "elevation": 171.0},
    "Prayagraj": {"lat": 25.4358, "lon": 81.8463, "timezone": 5.5, "elevation": 98.0},
    "Allahabad": {"lat": 25.4358, "lon": 81.8463, "timezone": 5.5, "elevation": 98.0},
    "Meerut": {"lat": 28.9845, "lon": 77.7064, "timezone": 5.5, "elevation": 219.0},
    "Ayodhya": {"lat": 26.7922, "lon": 82.1998, "timezone": 5.5, "elevation": 102.0},
    "Haridwar": {"lat": 29.9457, "lon": 78.1642, "timezone": 5.5, "elevation": 314.0},
    "Dehradun": {"lat": 30.3165, "lon": 78.0322, "timezone": 5.5, "elevation": 640.0},
    "Rishikesh": {"lat": 30.0869, "lon": 78.2676, "timezone": 5.5, "elevation": 372.0},

    # ── Madhya Pradesh ──
    "Bhopal": {"lat": 23.2599, "lon": 77.4126, "timezone": 5.5, "elevation": 527.0},
    "Indore": {"lat": 22.7196, "lon": 75.8577, "timezone": 5.5, "elevation": 553.0},
    "Gwalior": {"lat": 26.2183, "lon": 78.1828, "timezone": 5.5, "elevation": 212.0},
    "Jabalpur": {"lat": 23.1815, "lon": 79.9864, "timezone": 5.5, "elevation": 411.0},
    "Ujjain": {"lat": 23.1765, "lon": 75.7885, "timezone": 5.5, "elevation": 494.0},

    # ── West Bengal / East ──
    "Kolkata": {"lat": 22.5726, "lon": 88.3639, "timezone": 5.5, "elevation": 9.0},
    "Calcutta": {"lat": 22.5726, "lon": 88.3639, "timezone": 5.5, "elevation": 9.0},
    "Patna": {"lat": 25.5941, "lon": 85.1376, "timezone": 5.5, "elevation": 53.0},
    "Bhubaneswar": {"lat": 20.2961, "lon": 85.8245, "timezone": 5.5, "elevation": 45.0},
    "Cuttack": {"lat": 20.4625, "lon": 85.8830, "timezone": 5.5, "elevation": 36.0},
    "Ranchi": {"lat": 23.3441, "lon": 85.3096, "timezone": 5.5, "elevation": 651.0},
    "Guwahati": {"lat": 26.1445, "lon": 91.7362, "timezone": 5.5, "elevation": 55.0},

    # ── Punjab / Haryana / North ──
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794, "timezone": 5.5, "elevation": 321.0},
    "Amritsar": {"lat": 31.6340, "lon": 74.8723, "timezone": 5.5, "elevation": 234.0},
    "Ludhiana": {"lat": 30.9010, "lon": 75.8573, "timezone": 5.5, "elevation": 262.0},
    "Jalandhar": {"lat": 31.3260, "lon": 75.5762, "timezone": 5.5, "elevation": 228.0},
    "Shimla": {"lat": 31.1048, "lon": 77.1734, "timezone": 5.5, "elevation": 2276.0},
    "Leh": {"lat": 34.1526, "lon": 77.5771, "timezone": 5.5, "elevation": 3500.0},
    "Srinagar": {"lat": 34.0837, "lon": 74.7973, "timezone": 5.5, "elevation": 1585.0},
    "Jammu": {"lat": 32.7266, "lon": 74.8570, "timezone": 5.5, "elevation": 327.0},

    # ── Kerala / Goa ──
    "Kochi": {"lat": 9.9312, "lon": 76.2673, "timezone": 5.5, "elevation": 4.0},
    "Cochin": {"lat": 9.9312, "lon": 76.2673, "timezone": 5.5, "elevation": 4.0},
    "Thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366, "timezone": 5.5, "elevation": 16.0},
    "Trivandrum": {"lat": 8.5241, "lon": 76.9366, "timezone": 5.5, "elevation": 16.0},
    "Kozhikode": {"lat": 11.2588, "lon": 75.7804, "timezone": 5.5, "elevation": 1.0},
    "Panaji": {"lat": 15.4909, "lon": 73.8278, "timezone": 5.5, "elevation": 10.0},
    "Goa": {"lat": 15.2993, "lon": 74.1240, "timezone": 5.5, "elevation": 10.0},

    # ── International Capitals & Hubs ──
    "London": {"lat": 51.5074, "lon": -0.1278, "timezone": 0.0, "elevation": 25.0, "tz_name": "Europe/London"},
    "New York": {"lat": 40.7128, "lon": -74.0060, "timezone": -5.0, "elevation": 10.0, "tz_name": "America/New_York"},
    "San Francisco": {"lat": 37.7749, "lon": -122.4194, "timezone": -8.0, "elevation": 16.0, "tz_name": "America/Los_Angeles"},
    "Dubai": {"lat": 25.2048, "lon": 55.2708, "timezone": 4.0, "elevation": 5.0, "tz_name": "Asia/Dubai"},
    "Singapore": {"lat": 1.3521, "lon": 103.8198, "timezone": 8.0, "elevation": 15.0, "tz_name": "Asia/Singapore"},
    "Toronto": {"lat": 43.6532, "lon": -79.3832, "timezone": -5.0, "elevation": 76.0, "tz_name": "America/Toronto"},
    "Sydney": {"lat": -33.8688, "lon": 151.2093, "timezone": 10.0, "elevation": 19.0, "tz_name": "Australia/Sydney"},
    "Kathmandu": {"lat": 27.7172, "lon": 85.3240, "timezone": 5.75, "elevation": 1400.0, "tz_name": "Asia/Kathmandu"},
    "Colombo": {"lat": 6.9271, "lon": 79.8612, "timezone": 5.5, "elevation": 1.0, "tz_name": "Asia/Colombo"},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503, "timezone": 9.0, "elevation": 40.0, "tz_name": "Asia/Tokyo"},
}

CITY_CACHE: Dict[str, Dict[str, Any]] = {}


def get_city_details(name: str) -> Optional[Dict[str, Any]]:
    """Return dictionary with lat, lon, timezone, tz_name, elevation for a city."""
    if not name:
        return None

    clean_name = name.strip()
    c = CITIES.get(clean_name)

    if not c:
        lower_name = clean_name.lower()
        for key, val in CITIES.items():
            if key.lower() == lower_name:
                c = val
                break

    if not c and clean_name in CITY_CACHE:
        c = CITY_CACHE[clean_name]

    if not c:
        return None

    res = dict(c)
    if "tz_name" not in res:
        res["tz_name"] = "Asia/Kolkata" if res.get("timezone") == 5.5 else "UTC"
    if "timezone_offset" not in res and "timezone" in res:
        res["timezone_offset"] = res["timezone"]
    return res


def get_city(name: str) -> Optional[Tuple[float, float, float]]:
    if not name:
        return None

    clean_name = name.strip()

    if clean_name in CITIES:
        c = CITIES[clean_name]
        return c["lat"], c["lon"], c["timezone"]

    lower_name = clean_name.lower()
    for key, c in CITIES.items():
        if key.lower() == lower_name:
            return c["lat"], c["lon"], c["timezone"]

    if clean_name in CITY_CACHE:
        c = CITY_CACHE[clean_name]
        return c["lat"], c["lon"], c["timezone"]

    return None


def get_city_elevation(name: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None) -> float:
    if name:
        clean_name = name.strip()
        if clean_name in CITIES:
            return float(CITIES[clean_name].get("elevation", 0.0))
        lower_name = clean_name.lower()
        for key, c in CITIES.items():
            if key.lower() == lower_name:
                return float(c.get("elevation", 0.0))
        if clean_name in CITY_CACHE:
            return float(CITY_CACHE[clean_name].get("elevation", 0.0))

    if lat is not None and lon is not None:
        for c in CITIES.values():
            if abs(c["lat"] - lat) <= 0.05 and abs(c["lon"] - lon) <= 0.05:
                return float(c.get("elevation", 0.0))

    logger.warning(
        "Unrecognized city name '%s' (coords: lat=%s, lon=%s beyond 0.05° city radius). Defaulting elevation to sea level (0.0m).",
        name, lat, lon
    )
    return 0.0


def get_city_names() -> List[str]:
    return sorted(CITIES.keys())
