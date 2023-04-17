from django.db import models
from kbde.django import (
    models as kbde_models,
    rq as kbde_rq,
)

import uuid, traceback


class AbstractBgProcess(models.Model):
    BG_PROCESS_STATUS_NEW = "new"
    BG_PROCESS_STATUS_PENDING = "pending"
    BG_PROCESS_STATUS_PROCESSING = "processing"
    BG_PROCESS_STATUS_COMPLETED = "completed"
    BG_PROCESS_STATUS_FAILED = "failed"
    BG_PROCESS_STATUS_CHOICES = (
        (BG_PROCESS_STATUS_NEW, "New"),
        (BG_PROCESS_STATUS_PENDING, "Pending"),
        (BG_PROCESS_STATUS_PROCESSING, "Processing"),
        (BG_PROCESS_STATUS_COMPLETED, "Completed"),
        (BG_PROCESS_STATUS_FAILED, "Failed"),
    )

    bg_process_queue_name = "default"
    bg_process_failure_ttl = 60 * 60  # 1 hour
    bg_process_refresh_from_db = True

    slug = models.UUIDField(default=uuid.uuid4)
    bg_process_status = models.CharField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        choices=BG_PROCESS_STATUS_CHOICES,
        default=BG_PROCESS_STATUS_NEW,
    )
    bg_process_exception = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{super().__str__()} - {self.get_bg_process_status_display()}"

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)

        if self.bg_process_status == self.BG_PROCESS_STATUS_NEW:
            # Queue the processing
            self.queue_bg_process()

        return result

    def queue_bg_process(self):
        self.bg_process_status = self.BG_PROCESS_STATUS_PENDING
        self.bg_process_exception = ""
        self.save(
            update_fields=[
                "bg_process_status",
                "bg_process_exception",
            ],
        )

        return kbde_rq.queue_task(
            self.bg_process_queue_name,
            self.run_bg_process,
            failure_ttl=self.bg_process_failure_ttl,
        )

    def run_bg_process(self):

        if self.bg_process_refresh_from_db:
            self.refresh_from_db()

        self.bg_process_status = self.BG_PROCESS_STATUS_PROCESSING
        self.save(update_fields=["bg_process_status"])

        try:
            self.bg_process()
            self.bg_process_status = self.BG_PROCESS_STATUS_COMPLETED
            self.save(update_fields=["bg_process_status"])

        except Exception as e:
            self.bg_process_status = self.BG_PROCESS_STATUS_FAILED
            self.bg_process_exception = traceback.format_exc()
            self.save(
                update_fields=[
                    "bg_process_status",
                    "bg_process_exception",
                ],
            )
            raise

    def bg_process(self):
        """
        This method runs async
        Override to do work
        """
        raise NotImplementedError(
            f"{self.__class__} must implement self.bg_process()",
        )


class BgProcessModel(AbstractBgProcess):
    bg_process_id = models.AutoField(primary_key=True)
