# core/tasks.py
from celery import shared_task
import pandas as pd
from io import BytesIO
from .transformation import TransformationEngine

@shared_task
def generate_report_task(input_path, ref_path, rule_path):
    input_df = pd.read_csv(input_path)
    ref_df = pd.read_csv(ref_path)

    engine = TransformationEngine(rule_path)
    output_df = engine.process_dataframe(input_df, ref_df)

    output_path = input_path.replace("input.csv", "output.csv")
    output_df.to_csv(output_path, index=False)
    
    print(output_path)

    return output_path  # just return path instead of content

