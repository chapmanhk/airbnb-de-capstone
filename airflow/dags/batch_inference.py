# batch_inference.py

import pandas as pd
import joblib
import os
from sklearn.metrics import roc_auc_score
from upload_to_s3 import upload_file_to_s3, download_from_s3
from sklearn.metrics import classification_report

def run_batch_inference():
    models_bucket = os.getenv("MODELS_BUCKET")
    predictions_bucket = os.getenv("PREDICTIONS_BUCKET")

    # S3 Keys and Local Paths
    x_test_key = "test/X_test.csv"
    y_test_key = "test/y_test.csv"
    model_key = "model/model.pkl"

    local_x_test = "/opt/airflow/data/X_test.csv"
    local_y_test = "/opt/airflow/data/y_test.csv"
    local_model = "/opt/airflow/data/model.pkl"

    # Download test data and model
    download_from_s3(models_bucket, x_test_key, local_x_test)
    download_from_s3(models_bucket, y_test_key, local_y_test)
    download_from_s3(models_bucket, model_key, local_model)

    # Load data
    X = pd.read_csv(local_x_test)
    y = pd.read_csv(local_y_test).squeeze()  # Ensure it's a Series
    model = joblib.load(local_model)

    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1]
    auc = roc_auc_score(y, y_proba)

    # Get classification metrics
    report = classification_report(y, y_pred, output_dict=True)

    # Extract and reshape to long format
    long_metrics = []
    for class_label in ["0", "1"]:
        for metric in ["precision", "recall"]:
            long_metrics.append({
                "class": int(class_label),
                "metric": metric,
                "value": report[class_label][metric]
            })

    # Save and upload performance_by_class.csv
    perf_df = pd.DataFrame(long_metrics)
    perf_path = "/opt/airflow/data/performance_by_class.csv"
    perf_df.to_csv(perf_path, index=False)

    upload_file_to_s3(
        perf_path,
        predictions_bucket,
        "metrics/performance_by_class.csv"
    )

    # Save and upload roc-auc score to CSV
    auc_df = pd.DataFrame([{"metric": "roc_auc", "value": auc}])
    auc_path = "/opt/airflow/data/roc_auc.csv"
    auc_df.to_csv(auc_path, index=False)

    upload_file_to_s3(
        auc_path,
        predictions_bucket,
        "metrics/roc_auc.csv"
    )
    
    # Save and upload predictions
    predictions_df = pd.DataFrame({
        "actual": y,
        "predicted": y_pred,
        "probability": y_proba
    })

    pred_path = "/opt/airflow/data/predictions.csv"
    predictions_df.to_csv(pred_path, index=False)
    upload_file_to_s3(pred_path, predictions_bucket, "predictions/predictions.csv")
    
    print(f"Batch AUC: {auc:.3f}")