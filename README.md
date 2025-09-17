# Airbnb Los Angeles Data Engineering Capstone

\
*(End-to-end architecture: Airflow orchestrates data movement, Terraform provisions AWS infra, MLflow tracks experiments, and Tableau visualizes results.)*

## 🎯 Project Overview

This project demonstrates an **end-to-end data engineering pipeline** using the [Inside Airbnb Los Angeles dataset (March 2025)](http://insideairbnb.com/get-the-data.html). The goal is to predict whether a listing will receive a **high guest rating (≥ 4.5 stars)** based on its metadata (e.g., room type, property type, host attributes).

The project is part of the **WGU M.S. Data Analytics – Data Engineering specialization capstone**.

## 🛠️ Tech Stack

- **Airflow (Docker Compose)** – Orchestrates the pipeline (ingestion → cleaning → model training → prediction).
- **Terraform (AWS S3 + IAM)** – Infrastructure-as-code for cloud storage.
- **AWS S3** – Stores raw, cleaned, model, and prediction datasets.
- **MLflow** – Tracks model runs, parameters, and metrics.
- **scikit-learn (Random Forest)** – Trains the classification model.
- **Tableau** – Visualizes results.

## 📂 Repository Structure

```
.
├── airflow/             # Airflow DAGs, plugins, include/ (runtime files ignored)
├── data/                # Local development data (ignored)
├── notebooks/           # Exploratory analysis (outputs/ckpts ignored)
├── terraform/           # Terraform IaC for AWS buckets
├── docker-compose.yml   # Multi-service orchestration
├── Dockerfile           # Custom Airflow image
├── sync_env_from_tf     # Script to sync TF outputs → .env
├── .env.example         # Placeholder environment file
└── README.md
```

## 🚀 Getting Started

### 1. Prerequisites

- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [Terraform](https://developer.hashicorp.com/terraform/downloads)
- AWS credentials with S3 access

### 2. Setup

Clone the repository:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

Set up environment:

```bash
cp .env.example .env
# Fill in AWS credentials
```

Provision infrastructure:

```bash
cd terraform
terraform init
terraform apply
```

Sync Terraform outputs to `.env`:

```bash
./sync_env_from_tf
```

### 3. Run Airflow

```bash
docker compose up -d
```

Access the Airflow UI at: [http://localhost:8080](http://localhost:8080)\
Trigger the DAG: \`\`

### 4. MLflow (optional)

```bash
docker compose up -d mlflow
```

Access MLflow UI at: [http://localhost:5000](http://localhost:5000)

### 5. Tableau

Exported predictions can be visualized in Tableau dashboards.

## 📊 Results

- **Key Finding:** Listing characteristics such as `room_type`, `host_is_superhost`, and `property_type` significantly influence guest ratings.
- **Model:** Random Forest Classifier
- **Accuracy:** \~XX% (see MLflow for full metrics)

## ✅ Reproducibility

- Infrastructure codified in **Terraform**.
- Environment managed with **Docker**.
- Model tracking with **MLflow**.
- `.env.example` included for safe setup.

## ⚠️ Security

- `.env` and Terraform state files are **git-ignored**.
- Do not commit AWS credentials.
- If secrets are ever committed, rotate immediately.

## 📌 Future Work

- Experiment with additional models (XGBoost, LightGBM).
- Expand to other Airbnb markets for generalization.
- Automate Tableau dashboard refresh via Airflow.