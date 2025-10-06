import json
import os
import ijson  # It will help to parse large JSON files iteratively
import logging
from connect import DatabaseConnector
from dotenv import load_dotenv
from openai import OpenAI
from model import AnalysisResult
import time
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()
FILES_PATH = os.getenv("FILES_PATH")
client = OpenAI()


def get_json_files(path=FILES_PATH):
    for file in os.listdir(path):
        if file.endswith(".json"):
            yield os.path.join(path, file)


def generate_analyse_recommendation_batch(batch):
    log_metrics = json.dumps(batch, indent=2, default=float)

    prompt = f"""You are an infrastructure performance analyzer. 
    Given the following list of system metric snapshots (each item is one observation), do the following:
    1. Analyze the data and identify any anomalies or potential issues.
    2. Explain the likely causes behind those issues.
    3. Provide concrete, actionable recommendations to optimize system performance and reliability.
    Return the result strictly following the JSON schema defined by `AnalysisResult`.

    System metrics:
    {log_metrics}
    """

    response = client.responses.parse(
        model="gpt-4.1",
        input=[{"role": "user", "content": prompt}],
        text_format=AnalysisResult,
    ).output_parsed

    analysis = AnalysisResult.model_validate(response)

    logger.info(
        f"Analysis generated with {len(analysis.anomalies_detected)} anomalies and {len(analysis.recommendations)} recommendations."
    )

    return analysis


def build_objects_for_db(analysis_result, original_batch):
    metrics_object = {
        "start_date": original_batch[0]["timestamp"],
        "end_date": original_batch[-1]["timestamp"],
        "metrics": original_batch,
    }

    analysis_object = {
        "analysis": analysis_result.analysis_summary,
        "anomalies": [
            anomaly.model_dump() for anomaly in analysis_result.anomalies_detected
        ],
        "recommendations": [
            rec.model_dump() for rec in analysis_result.recommendations
        ],
    }

    return json.dumps(metrics_object, default=float), json.dumps(analysis_object)


def process_json_file(filename, batch_size=os.getenv("BATCH_SIZE", 10)):
    def process_batch(batch):
        logger.info(f"Processing batch of size {len(batch)}")
        analysis = generate_analyse_recommendation_batch(batch)
        metrics_object, analysis_object = build_objects_for_db(analysis, batch)
        return metrics_object, analysis_object

    batch = []
    with open(filename, "r") as file:
        objects = ijson.items(file, "item")
        for obj in objects:
            batch.append(obj)
            if len(batch) >= int(batch_size):
                metrics_object, analysis_object = process_batch(batch)
                batch = []

        # We dont forget to process the last metrics if they are less than batch size
        if batch:
            metrics_object, analysis_object = process_batch(batch)
    return metrics_object, analysis_object


def save_to_db(metrics_object, analysis_object):
    db_connector = DatabaseConnector()
    db_connector.connect_to_db()
    if not db_connector.table_exist():
        db_connector.initialize_db()

    db_connector.insert_data(metrics_object, analysis_object)


if __name__ == "__main__":

    connect = DatabaseConnector()
    for file_path in get_json_files():
        metrics_object, analysis_object = process_json_file(file_path)
        save_to_db(metrics_object, analysis_object)
