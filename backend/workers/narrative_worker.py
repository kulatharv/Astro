"""Background narrative generation worker process with crash recovery and ACK/NACK (CF-05)."""

import asyncio
import logging
import time
from shared.logging.logger import get_logger
from shared.queue.redis_queue import default_queue, JobStatus
from modules.narrative.jobs import get_job, mark_running, mark_completed, mark_failed
from modules.narrative.engine import NarrativeEngine
from modules.narrative.schemas import NarrativeJobResult

logger = get_logger("workers.narrative_worker")


async def process_job(job_id: str, max_retries: int = 3):
    """Execute narrative LLM generation for a queued job with reliable ACK/NACK."""
    job_status = await get_job(job_id)
    if not job_status or job_status.status == JobStatus.COMPLETED:
        await default_queue.ack_job(job_id)
        return

    await mark_running(job_id)
    logger.info(f"Processing narrative job {job_id}...")

    # Load original request params from state
    from shared.cache.redis_client import CacheService
    import json
    raw = CacheService.get(f"narrative:job:{job_id}")
    data = json.loads(raw) if isinstance(raw, str) else raw
    req_dict = data.get("request", {}) if isinstance(data, dict) else {}

    try:
        res_dict = NarrativeEngine.generate_predictions(
            year=req_dict.get("year", 1990),
            month=req_dict.get("month", 1),
            day=req_dict.get("day", 1),
            hour=req_dict.get("hour", 12.0),
            city=req_dict.get("city", "Pune"),
            lang=req_dict.get("lang", "en"),
        )
        result = NarrativeJobResult(
            marriage_prediction=res_dict.get("marriage_prediction"),
            career_prediction=res_dict.get("career_prediction"),
            raw_marriage_score=res_dict.get("raw_marriage_score"),
            raw_career_score=res_dict.get("raw_career_score"),
            chart=res_dict.get("chart"),
        )
        await mark_completed(job_id, result)
        await default_queue.ack_job(job_id)
        logger.info(f"Narrative job {job_id} completed successfully and acknowledged.")
    except Exception as exc:
        logger.warning(f"Processing failed for job {job_id}: {exc}")
        requeued = await default_queue.nack_job(job_id, error=str(exc), max_retries=max_retries)
        if not requeued:
            await mark_failed(job_id, f"LLM narrative generation failed after max retries: {exc}")


async def run_worker():
    """Worker event loop pulling jobs from Redis queue with crash recovery."""
    logger.info("Narrative worker started listening for jobs...")
    last_recovery_check = time.time()

    while True:
        try:
            # Periodic orphan/stale job recovery every 60 seconds
            if time.time() - last_recovery_check > 60:
                recovered = await default_queue.recover_stale_jobs(visibility_timeout=300)
                if recovered > 0:
                    logger.info(f"Worker recovery loop recovered {recovered} orphaned jobs.")
                last_recovery_check = time.time()

            # Atomically pop job with in-flight lease tracking
            job_id = await default_queue.pop_job()
            if job_id:
                await process_job(job_id)
            else:
                await asyncio.sleep(0.5)
        except Exception as exc:
            logger.error(f"Worker loop error: {exc}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run_worker())
