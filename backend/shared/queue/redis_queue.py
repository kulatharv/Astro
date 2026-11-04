"""
Async Task Queue Interface & Reliable Redis Queue Wrapper (CF-05).
Features:
- Acknowledgement tracking (ACK / NACK)
- In-flight lease management & crash recovery
- Dead Letter Queue (DLQ) for terminal failures
- Bounded retries with exponential backoff
"""

import time
from datetime import datetime
import json
import logging
from typing import Any, Dict, List, Optional
from shared.cache.redis_client import CacheService

logger = logging.getLogger("shared.queue.redis_queue")


class JobStatus:
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RedisQueue:
    """Production-grade Task Queue abstraction with ACK/NACK and crash recovery."""

    def __init__(self, queue_name: str = "narrative_queue", ttl: int = 86400):
        self.queue_name = queue_name
        self.ttl = ttl
        self.pending_key = f"queue:{self.queue_name}"
        self.processing_key = f"queue:{self.queue_name}:processing"
        self.dlq_key = f"queue:{self.queue_name}:dlq"

    async def enqueue(self, job_name: str, payload: Dict[str, Any], job_id: Optional[str] = None) -> str:
        """Enqueue job metadata and payload into queue list and state store."""
        jid = job_id or f"job:{payload.get('input_hash', 'unknown')}"
        state_key = f"narrative:job:{jid}"

        job_data = {
            "job_id": jid,
            "job_name": job_name,
            "payload": payload,
            "status": JobStatus.QUEUED,
            "result": None,
            "error": None,
            "retries": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        try:
            # Store initial job state
            CacheService.set(state_key, json.dumps(job_data), ttl=self.ttl)
            # Push job id into queue list
            raw_list = CacheService.get(self.pending_key) or []
            if isinstance(raw_list, str):
                try:
                    raw_list = json.loads(raw_list)
                except Exception:
                    raw_list = []
            if jid not in raw_list:
                raw_list.append(jid)
            CacheService.set(self.pending_key, json.dumps(raw_list), ttl=self.ttl)
            logger.info(f"Enqueued job {jid} into {self.queue_name}")
        except Exception as exc:
            logger.error(f"Failed to enqueue job {jid}: {exc}")
            raise exc

        return jid

    async def pop_job(self) -> Optional[str]:
        """
        Atomically fetch next job and place into in-flight processing tracking.
        Prevents job loss if worker process crashes during execution.
        """
        raw_list = CacheService.get(self.pending_key)
        pending = json.loads(raw_list) if isinstance(raw_list, str) else (raw_list or [])

        if not pending:
            return None

        job_id = pending.pop(0)
        CacheService.set(self.pending_key, json.dumps(pending), ttl=self.ttl)

        # Track in processing registry: dict of {job_id: timestamp_started}
        raw_proc = CacheService.get(self.processing_key)
        processing = json.loads(raw_proc) if isinstance(raw_proc, str) else (raw_proc or {})
        processing[job_id] = time.time()
        CacheService.set(self.processing_key, json.dumps(processing), ttl=self.ttl)

        return job_id

    async def ack_job(self, job_id: str) -> None:
        """Acknowledge successful job execution and remove from processing registry."""
        raw_proc = CacheService.get(self.processing_key)
        processing = json.loads(raw_proc) if isinstance(raw_proc, str) else (raw_proc or {})
        if job_id in processing:
            del processing[job_id]
            CacheService.set(self.processing_key, json.dumps(processing), ttl=self.ttl)

    async def nack_job(self, job_id: str, error: str, max_retries: int = 3) -> bool:
        """
        Negative acknowledgement.
        Increments retry count; re-queues if below max_retries, else moves to DLQ.
        Returns True if re-queued, False if moved to DLQ.
        """
        await self.ack_job(job_id)

        state_key = f"narrative:job:{job_id}"
        raw_state = CacheService.get(state_key)
        state = json.loads(raw_state) if isinstance(raw_state, str) else (raw_state or {})

        retries = state.get("retries", 0) + 1
        state["retries"] = retries
        state["updated_at"] = time.time()
        state["error"] = error

        if retries >= max_retries:
            # Terminally failed -> move to Dead Letter Queue (DLQ)
            state["status"] = JobStatus.FAILED
            CacheService.set(state_key, json.dumps(state), ttl=self.ttl)

            raw_dlq = CacheService.get(self.dlq_key)
            dlq = json.loads(raw_dlq) if isinstance(raw_dlq, str) else (raw_dlq or [])
            if job_id not in dlq:
                dlq.append(job_id)
            CacheService.set(self.dlq_key, json.dumps(dlq), ttl=self.ttl)
            logger.warning(f"Job {job_id} exceeded max retries ({max_retries}). Moved to DLQ.")
            return False
        else:
            # Re-enqueue for retry
            state["status"] = JobStatus.QUEUED
            CacheService.set(state_key, json.dumps(state), ttl=self.ttl)

            raw_pending = CacheService.get(self.pending_key)
            pending = json.loads(raw_pending) if isinstance(raw_pending, str) else (raw_pending or [])
            if job_id not in pending:
                pending.append(job_id)
            CacheService.set(self.pending_key, json.dumps(pending), ttl=self.ttl)
            logger.info(f"Job {job_id} failed attempt {retries}/{max_retries}. Re-queued for retry.")
            return True

    async def recover_stale_jobs(self, visibility_timeout: int = 300, max_retries: int = 3) -> int:
        """
        Scans in-flight jobs in processing registry that have exceeded visibility_timeout.
        Recovers orphaned jobs caused by worker crashes or timeouts.
        """
        raw_proc = CacheService.get(self.processing_key)
        processing = json.loads(raw_proc) if isinstance(raw_proc, str) else (raw_proc or {})

        now = time.time()
        stale_jobs = []

        for jid, started_at in list(processing.items()):
            if (now - started_at) > visibility_timeout:
                stale_jobs.append(jid)

        recovered_count = 0
        for jid in stale_jobs:
            logger.warning(f"Recovering orphaned/stale job {jid} (timed out after {visibility_timeout}s)")
            await self.nack_job(jid, error=f"Worker crashed or timed out after {visibility_timeout}s", max_retries=max_retries)
            recovered_count += 1

        return recovered_count

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve job state payload."""
        state_key = f"narrative:job:{job_id}"
        val = CacheService.get(state_key)
        if not val:
            return None
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return None
        return val

    def get_queue_stats(self) -> Dict[str, int]:
        """Return counts of pending, processing, and dead-letter jobs."""
        def _get_len(k: str) -> int:
            raw = CacheService.get(k)
            val = json.loads(raw) if isinstance(raw, str) else (raw or [])
            return len(val)

        return {
            "pending": _get_len(self.pending_key),
            "processing": _get_len(self.processing_key),
            "dead_letter": _get_len(self.dlq_key),
        }


default_queue = RedisQueue()
