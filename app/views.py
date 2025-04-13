import os
import uuid
import yaml

from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from celery.result import AsyncResult
from .utils import generate_report_task


class GenerateReportView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        input_file = request.FILES.get('input')
        reference_file = request.FILES.get('reference')

        if not input_file or not reference_file:
            return Response({"error": "Both input and reference files are required."}, status=400)

        unique_id = str(uuid.uuid4())
        input_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}_input.csv")
        ref_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}_reference.csv")
        rules_path = os.path.join(settings.BASE_DIR, 'app', 'transformation', 'configs', 'rules.json')

        # Save input files
        for file_obj, path in [(input_file, input_path), (reference_file, ref_path)]:
            with open(path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

        task = generate_report_task.delay(input_path, ref_path, rules_path)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


from django.http import FileResponse
import os


class DownloadReportView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)

        if not result.ready():
            return Response({"status": result.status}, status=202)

        output_path = result.get()

        # 🔍 Log for debugging
        print("Returned result from task:", repr(output_path))
        print("Type:", type(output_path))

        if not isinstance(output_path, str):
            return Response({
                "error": "Invalid return from Celery task",
                "value": str(output_path),
                "type": str(type(output_path))
            }, status=500)

        if not os.path.exists(output_path):
            return Response({"error": "Report file not found."}, status=404)

        return FileResponse(
            open(output_path, 'rb'),
            content_type='text/csv',
            as_attachment=True,
            filename=os.path.basename(output_path)
        )



class UploadRulesView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_type = request.query_params.get('type', 'json').lower()
        uploaded_file = request.FILES.get('file')

        if file_type not in ['json', 'yaml']:
            return Response({"error": "Unsupported file type. Use 'json' or 'yaml'."}, status=400)

        if not uploaded_file:
            return Response({"error": "No file uploaded."}, status=400)

        rules_dir = os.path.join(settings.BASE_DIR, 'app', 'transformation', 'configs')
        os.makedirs(rules_dir, exist_ok=True)
        rules_path = os.path.join(rules_dir, f"rules.{file_type}")

        try:
            with open(rules_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            return Response({"message": f"Rules file uploaded successfully as rules.{file_type}"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class TriggerScheduledReportView(APIView):
    def post(self, request):
        input_path = os.path.join(settings.MEDIA_ROOT, 'input.csv')
        ref_path = os.path.join(settings.MEDIA_ROOT, 'reference.csv')
        rules_path = os.path.join(settings.BASE_DIR, 'app', 'transformation', 'configs', 'rules.json')

        if not (os.path.exists(input_path) and os.path.exists(ref_path)):
            return Response({"error": "Required files not found in media folder."}, status=400)

        try:
            task = generate_report_task.delay(input_path, ref_path, rules_path)
            return Response({"message": "Scheduled report generation triggered.", "task_id": task.id}, status=202)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
