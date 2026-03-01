from celery import shared_task
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from candidates.models import Candidate
from .models import BatchRun, CandidateAttempt
import requests


@shared_task(bind=True, max_retries=3)
def process_batch(self):
    now = timezone.now()

    with transaction.atomic():

        # Recover stuck picked records (crash recovery)
        Candidate.objects.filter(
            picked_at__lte=now - timedelta(hours=1)
        ).update(picked_at=None)

        candidates = (
            Candidate.objects
            .select_for_update(skip_locked=True)
            .filter(
                Q(status__in=["PENDING", "FAILED"]),
                Q(picked_at__isnull=True)
            )[:10]
        )

        if not candidates:
            return

        batch = BatchRun.objects.create(
            scheduled_for=now,
            started_at=now,
            batch_size=len(candidates),
        )

        payload = []

        for c in candidates:
            c.picked_at = now
            c.save(update_fields=["picked_at"])

            payload.append({
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "phoneNumber": c.phone_number,
                "link": c.link,
                "dob": c.dob.strftime("%d/%m/%Y") if c.dob else None
            })

    try:
        response = requests.post(
            "https://dev.micro.mgsigma.net/batch/process",
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            raise Exception("External API failed")

        results = response.json()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

    success_count = 0
    failed_count = 0

    for result in results:
        candidate = Candidate.objects.get(id=result["id"])

        candidate.attempt_count += 1
        candidate.status = result["status"]
        candidate.picked_at = None
        candidate.save()

        CandidateAttempt.objects.create(
            candidate=candidate,
            batch_run=batch,
            attempt_no=candidate.attempt_count,
            result_status=result["status"]
        )

        if result["status"] == "SUCCESS":
            success_count += 1
        else:
            failed_count += 1

    batch.success_count = success_count
    batch.failed_count = failed_count
    batch.finished_at = timezone.now()
    batch.save()