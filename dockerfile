FROM apache/airflow:2.6.0-python3.11

USER root

# Install OS packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python packages

COPY airflow/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt