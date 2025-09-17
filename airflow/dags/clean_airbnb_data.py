import pandas as pd
import numpy as np
import re

def clean_airbnb_data():
    # Load raw data
    df = pd.read_csv("/opt/airflow/data/listings2025-03.csv")

    variables = [
        'review_scores_rating', 'host_response_time', 'host_response_rate',
        'host_acceptance_rate', 'host_identity_verified', 'host_listings_count',
        'room_type', 'accommodates', 'bedrooms', 'bathrooms', 'bathrooms_text',
        'price', 'instant_bookable', 'minimum_nights', 'maximum_nights',
        'number_of_reviews_ltm'
    ]
    df = df[variables].copy()

    # Clean percentages
    def percent_to_float(x):
        if isinstance(x, str) and x.endswith('%'):
            return float(x.strip('%')) / 100
        return np.nan

    df["host_response_rate"] = df["host_response_rate"].apply(percent_to_float)
    df["host_acceptance_rate"] = df["host_acceptance_rate"].apply(percent_to_float)

    # Clean bathrooms
    def extract_bathroom_count(row):
        if pd.notnull(row["bathrooms"]):
            return row["bathrooms"]
        elif pd.notnull(row["bathrooms_text"]):
            match = re.search(r'(\d+\.?\d*)', row["bathrooms_text"])
            if match:
                return float(match.group(1))
        return np.nan

    df["clean_bathrooms"] = df.apply(extract_bathroom_count, axis=1)
    df = df.drop(["bathrooms", "bathrooms_text"], axis=1)

    # Clean price
    df["price"] = df["price"].str.replace("[$,]", "", regex=True).astype(float)

    # Drop rows with missing target
    df = df[df["review_scores_rating"].notnull()].copy()
    df["high_rating"] = (df["review_scores_rating"] >= 4.5).astype(int)
    df = df.drop('review_scores_rating', axis=1)

    # Create missing flags
    for col in ["price", "host_acceptance_rate", "host_response_rate", "bedrooms", "host_listings_count", "host_identity_verified"]:
        df[f"{col}_missing"] = df[col].isnull().astype(int)

    # Impute with median
    for col in ["price", "host_acceptance_rate", "host_response_rate", "bedrooms", "clean_bathrooms", "host_listings_count"]:
        df[col] = df[col].fillna(df[col].median())

    df["host_identity_verified"] = df["host_identity_verified"].map({"t": 1, "f": 0}).fillna(0)

    # One-hot encode
    df = pd.get_dummies(
        df,
        columns=["host_response_time", "room_type", "instant_bookable"],
        prefix=["response_time", "room", "bookable"],
        drop_first=True,
        dummy_na=True
    )

    # Save cleaned CSV
    output_path = "/opt/airflow/data/cleaned_listings.csv"
    df.to_csv(output_path, index=False)

    # Return path for use in the DAG
    return output_path
