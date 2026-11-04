"""Cache key computation utilities for chart computations."""

import hashlib
import json
from typing import Any
from pydantic import BaseModel


def compute_input_hash(req_data: dict[str, Any] | BaseModel) -> str:
    """
    Compute a deterministic SHA256 input hash for birth chart data.
    Ensures keys are sorted, values are normalized (canonical JSON).
    """
    if isinstance(req_data, BaseModel):
        data = req_data.model_dump()
    else:
        data = dict(req_data)

    # Standardize & normalize fields
    normalized = {
        "year": int(data.get("year", 2000)),
        "month": int(data.get("month", 1)),
        "day": int(data.get("day", 1)),
        "hour": float(data.get("hour", 12)),
        "minute": int(data.get("minute", 0)),
        "second": int(data.get("second", 0)),
        "city": str(data.get("city") or data.get("place") or "Pune").strip().lower(),
        "latitude": round(float(data.get("latitude", data.get("lat", 0.0))), 4) if ("latitude" in data and data["latitude"] is not None) or ("lat" in data and data["lat"] is not None) else None,
        "longitude": round(float(data.get("longitude", data.get("lon", 0.0))), 4) if ("longitude" in data and data["longitude"] is not None) or ("lon" in data and data["lon"] is not None) else None,
        "timezone": str(data.get("timezone") or "Asia/Kolkata").strip(),
        "ayanamsa": str(data.get("ayanamsa") or "Lahiri").strip().lower(),
    }

    # Filter out None values to keep payload tight
    clean_payload = {k: v for k, v in normalized.items() if v is not None}

    canonical_json = json.dumps(clean_payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def chart_cache_key(input_hash: str, engine_version: str = "2.0.0") -> str:
    """
    Format standard chart cache key.
    Format: chart:{engine_version}:{input_hash}
    """
    return f"chart:{engine_version}:{input_hash}"
