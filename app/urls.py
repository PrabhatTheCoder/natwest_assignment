from django.urls import path
from .views import GenerateReportView, UploadRulesView, TriggerScheduledReportView, DownloadReportView

urlpatterns = [
    path('generate-report/', GenerateReportView.as_view(), name='generate_report'),
    path('upload-rules/', UploadRulesView.as_view(), name='upload_rules'),
    path('trigger-scheduled-report/', TriggerScheduledReportView.as_view(), name='trigger_scheduled_report'),
    path('download-report/<str:task_id>/', DownloadReportView.as_view())
]
