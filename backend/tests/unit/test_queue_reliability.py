"""
Unit tests for Background Queue Reliability, ACK/NACK, and Crash Recovery (CF-05).
"""

import pytest
import asyncio
from shared.queue.redis_queue import RedisQueue, JobStatus
from shared.cache.redis_client import CacheService


class TestQueueReliability:
    """Test suite for task queue fault tolerance, retries, and dead-letter handling."""

    def test_enqueue_and_pop_tracks_in_flight(self):
        async def _test():
            CacheService.clear()
            queue = RedisQueue(queue_name="test_queue_ack")
            job_id = "test_job_1"

            await queue.enqueue(job_name="test_task", payload={"data": 123}, job_id=job_id)
            stats = queue.get_queue_stats()
            assert stats["pending"] >= 1

            # Pop job moves it to processing
            popped = await queue.pop_job()
            assert popped == job_id
            stats_after_pop = queue.get_queue_stats()
            assert stats_after_pop["processing"] >= 1

            # ACK removes from processing
            await queue.ack_job(job_id)
            stats_after_ack = queue.get_queue_stats()
            assert stats_after_ack["processing"] == 0

        asyncio.run(_test())

    def test_nack_retries_and_dead_letter_queue(self):
        async def _test():
            CacheService.clear()
            queue = RedisQueue(queue_name="test_queue_retry")
            job_id = "test_failing_job"

            await queue.enqueue(job_name="fail_task", payload={"data": "err"}, job_id=job_id)
            await queue.pop_job()

            # Attempt 1: NACK should re-queue (max_retries=3)
            requeued_1 = await queue.nack_job(job_id, error="Transient timeout", max_retries=3)
            assert requeued_1 is True
            job_state = await queue.get_job(job_id)
            assert job_state["retries"] == 1
            assert job_state["status"] == JobStatus.QUEUED

            # Pop and Attempt 2: NACK should re-queue
            await queue.pop_job()
            requeued_2 = await queue.nack_job(job_id, error="Transient timeout", max_retries=3)
            assert requeued_2 is True
            job_state = await queue.get_job(job_id)
            assert job_state["retries"] == 2

            # Pop and Attempt 3: Terminal failure -> move to DLQ
            await queue.pop_job()
            requeued_3 = await queue.nack_job(job_id, error="Fatal provider error", max_retries=3)
            assert requeued_3 is False  # Moved to DLQ, not requeued
            job_state = await queue.get_job(job_id)
            assert job_state["retries"] == 3
            assert job_state["status"] == JobStatus.FAILED

            # Verify DLQ contains job
            stats = queue.get_queue_stats()
            assert stats["dead_letter"] >= 1

        asyncio.run(_test())

    def test_recover_stale_jobs_after_worker_crash(self):
        async def _test():
            CacheService.clear()
            queue = RedisQueue(queue_name="test_queue_crash")
            job_id = "test_orphaned_job"

            await queue.enqueue(job_name="crash_task", payload={}, job_id=job_id)
            popped = await queue.pop_job()
            assert popped == job_id

            # Worker crashes here without calling ack or nack!
            # Run stale recovery with visibility_timeout = -1 (all in-flight jobs considered stale)
            recovered = await queue.recover_stale_jobs(visibility_timeout=-1, max_retries=3)
            assert recovered >= 1

            # Verify job is recovered and back in pending queue
            re_popped = await queue.pop_job()
            assert re_popped == job_id
            await queue.ack_job(job_id)

        asyncio.run(_test())
