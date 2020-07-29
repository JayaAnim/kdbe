from django.db import models
from kbde.django import (models as kbde_models,
                         rq as kbde_rq)

import uuid


class BgProcessModel(models.Model):
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

    slug = models.UUIDField(default=uuid.uuid4)
    bg_process_status = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
                                         choices=BG_PROCESS_STATUS_CHOICES,
                                         default=BG_PROCESS_STATUS_NEW)

    def __str__(self):
        return f"{super().__str__()} - {self.get_bg_process_status_display()}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.bg_process_status == self.BG_PROCESS_STATUS_NEW:
            # Queue the processing
            self.queue_bg_process()

    def queue_bg_process(self):
        self.bg_process_status = self.BG_PROCESS_STATUS_PENDING
        self.save()

        return kbde_rq.queue_task(self.bg_process_queue_name, self.run_bg_process)

    def run_bg_process(self):
        self.bg_process_status = self.BG_PROCESS_STATUS_PROCESSING
        self.save()

        try:
            self.bg_process()
            self.bg_process_status = self.BG_PROCESS_STATUS_COMPLETED
            self.save()

        except Exception as e:
            self.bg_process_status = self.BG_PROCESS_STATUS_FAILED
            self.save()
            raise

    def bg_process(self):
        """
        This method runs async
        Override to do work
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement self.bg_process()")
