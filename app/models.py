# models.py

from django.db import models

class ReportRun(models.Model):
    id = models.UUIDField(primary_key=True)
    report_name = models.CharField(max_length=255)
    task_id = models.CharField(max_length=255)
    output_path = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, default="Scheduled")  # Add status field

    def __str__(self):
        return self.report_name
