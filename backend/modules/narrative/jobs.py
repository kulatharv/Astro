"""Job store for async narrative generation tasks."""

import hashlib
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from shared.cache.redis_client import CacheService
from shared.queue.redis_queue import JobStatus, default_queue
from modules.narrative.schemas import NarrativeJobRequest, NarrativeJobStatus, NarrativeJobResult

logger = logging.getLogger("modules.narrative.jobs")
JOB_TTL_SECONDS = 86400  # 24 hours


def compute_job_id(input_hash: str, engine_version: str = "2.0.0", prompt_version: str = "1.0.0") -> str:
    """Deterministic 16-character job ID from input hash and engine/prompt versions."""
    raw = f"{input_hash}:{engine_version}:{prompt_version}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


async def create_job(req: NarrativeJobRequest) -> str:
    """Create or return existing narrative job state in Redis."""
    job_id = compute_job_id(req.input_hash, req.engine_version, req.prompt_version)
    state_key = f"narrative:job:{job_id}"

    # Check if job already exists
    existing = CacheService.get(state_key)
    if existing:
        if isinstance(existing, str):
            try:
                existing = json.loads(existing)
            except Exception:
                existing = None

        if existing and isinstance(existing, dict):
            logger.info(f"Narrative job {job_id} already exists with status: {existing.get('status')}")
            return job_id

    now_iso = datetime.utcnow().isoformat()
    req_dict = req.model_dump() if hasattr(req, "model_dump") else req.dict()
    job_state = {
        "job_id": job_id,
        "status": JobStatus.QUEUED,
        "input_hash": req.input_hash,
        "language": req.lang,
        "created_at": now_iso,
        "request": req_dict,
        "result": None,
        "error": None,
    }

    CacheService.set(state_key, json.dumps(job_state), ttl=JOB_TTL_SECONDS)
    await default_queue.enqueue(job_name="process_narrative", payload=job_state["request"], job_id=job_id)
    return job_id


async def get_job(job_id: str) -> Optional[NarrativeJobStatus]:
    """Get job status and result from Redis store."""
    state_key = f"narrative:job:{job_id}"
    raw = CacheService.get(state_key)
    if not raw:
        return None
    if isinstance(raw, str):
        data = json.loads(raw)
    else:
        data = raw

    res_obj = NarrativeJobResult(**data["result"]) if data.get("result") else None
    input_hash = data.get("input_hash") or (data.get("request", {}).get("input_hash") if isinstance(data.get("request"), dict) else "unknown")
    raw_created = data.get("created_at")
    if isinstance(raw_created, (int, float)):
        created_at = datetime.utcfromtimestamp(raw_created).isoformat()
    elif raw_created:
        created_at = str(raw_created)
    else:
        created_at = datetime.utcnow().isoformat()
    return NarrativeJobStatus(
        job_id=data["job_id"],
        status=data["status"],
        input_hash=input_hash,
        language=data.get("language", "en"),
        created_at=created_at,
        result=res_obj,
        error=data.get("error"),
    )


async def mark_running(job_id: str) -> None:
    """Update job state to RUNNING."""
    await _update_job_status(job_id, JobStatus.RUNNING)


async def mark_completed(job_id: str, result: NarrativeJobResult) -> None:
    """Update job state to COMPLETED with payload."""
    res_dict = result.model_dump() if hasattr(result, "model_dump") else result.dict()
    await _update_job_status(job_id, JobStatus.COMPLETED, result=res_dict)


async def mark_failed(job_id: str, error_msg: str) -> None:
    """Update job state to FAILED with error details."""
    await _update_job_status(job_id, JobStatus.FAILED, error=error_msg)


async def _update_job_status(job_id: str, status: str, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> None:
    state_key = f"narrative:job:{job_id}"
    raw = CacheService.get(state_key)
    if not raw:
        return
    data = json.loads(raw) if isinstance(raw, str) else raw
    data["status"] = status
    if result is not None:
        data["result"] = result
    if error is not None:
        data["error"] = error
    CacheService.set(state_key, json.dumps(data), ttl=JOB_TTL_SECONDS)
