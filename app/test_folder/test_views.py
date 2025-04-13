from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class ReportGeneratorTests(APITestCase):

    def test_upload_and_generate_report(self):
        input_file = SimpleUploadedFile("input.csv", b"field1,field2,field3,field4,field5,refkey1,refkey2\nA,B,C,D,1.0,R1,R2")
        reference_file = SimpleUploadedFile("reference.csv", b"refkey1,refdata1,refkey2,refdata2,refdata3,refdata4\nR1,Data1,R2,Data2,Data3,2.0")

        url = reverse("generate-report")  # use the correct URL name
        response = self.client.post(url, data={
            'input': input_file,
            'reference': reference_file
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
