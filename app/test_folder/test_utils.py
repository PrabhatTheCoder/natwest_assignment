from django.test import TestCase
from app.utils import generate_report_task
import os

class ReportUtilsTest(TestCase):
    def test_generate_report(self):
        input_path = "sample_input.csv"
        reference_path = "sample_ref.csv"
        rules_path = "sample_rules.json"
        
        with open(input_path, "w") as f:
            f.write("field1,field2,field3,field4,field5,refkey1,refkey2\nA,B,C,D,10,R1,R2")
        with open(reference_path, "w") as f:
            f.write("refkey1,refdata1,refkey2,refdata2,refdata3,refdata4\nR1,X,R2,Y,Z,20")
        with open(rules_path, "w") as f:
            f.write('''{
                "outfield1": "field1 + field2",
                "outfield2": "refdata1",
                "outfield3": "refdata2 + refdata3",
                "outfield4": "field3 * max(field5, refdata4)",
                "outfield5": "max(field5, refdata4)"
            }''')

        output_path = generate_report_task(input_path, reference_path, rules_path)

        self.assertTrue(os.path.exists(output_path))
        os.remove(input_path)
        os.remove(reference_path)
        os.remove(rules_path)
        os.remove(output_path)

