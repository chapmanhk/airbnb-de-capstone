import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import mlflow
import joblib
import boto3
import os

from upload_to_s3 import upload_file_to_s3, download_from_s3

def train_model_from_cleaned_csv():
    # Paths and config
    cleaned_bucket = os.getenv("CLEANED_BUCKET")
    models_bucket = os.getenv("MODELS_BUCKET")

    # Cleaned data path
    cleaned_key = "cleaned_listings.csv"
    cleaned_local_path = "/opt/airflow/data/cleaned_listings.csv"

    # Download file
    download_from_s3(cleaned_bucket, cleaned_key, cleaned_local_path)

    # Load and split data
    df = pd.read_csv(cleaned_local_path)
    X = df.drop(columns=["high_rating"])
    y = df["high_rating"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Save test data for batch inference
    X_test_path = "/opt/airflow/data/X_test.csv"
    y_test_path = "/opt/airflow/data/y_test.csv"

    X_test.to_csv(X_test_path, index=False)
    y_test.to_csv(y_test_path, index=False)

    upload_file_to_s3(X_test_path, models_bucket, "test/X_test.csv")
    upload_file_to_s3(y_test_path, models_bucket, "test/y_test.csv")

    # Train and evaluate
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Log to MLflow
    with mlflow.start_run(run_name="rf_airbnb_model"):
        mlflow.log_param("model_type", "RandomForest")
        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("train_size", len(X_train))
        mlflow.sklearn.log_model(model, "model")

    # Save Feature Importances csv for Tableau
    importances_df = pd.DataFrame({
        "feature": X.columns,
        "importance": model.feature_importances_
    }).sort_values(by="importance", ascending=False)

    importance_path = "/opt/airflow/data/feature_importance.csv"
    importances_df.to_csv(importance_path, index=False)

    # Upload to predictions bucket
    upload_file_to_s3(importance_path, os.getenv("MODELS_BUCKET"), "model/feature_importance.csv")

    # Save model artifact locally and upload
    model_path = "/opt/airflow/data/model.pkl"
    joblib.dump(model, model_path)
    upload_file_to_s3(model_path, models_bucket, "model/model.pkl")
