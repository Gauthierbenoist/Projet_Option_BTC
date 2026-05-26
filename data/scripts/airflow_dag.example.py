"""
Exemple DAG Airflow (à copier vers votre dossier dags Airflow).

Prérequis :
  - Variable d'environnement PROJECT_ROOT ou chemins montés dans le worker
  - Dépendances installées dans l'image Airflow (requirements.txt)
  - PostgreSQL accessible depuis le worker
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_ROOT = "/chemin/vers/Projets python"
PYTHON = f"{PROJECT_ROOT}/.venv/bin/python"

default_args = {
    "owner": "quant",
    "depends_on_past": False,
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="deribit_btc_options_daily",
    default_args=default_args,
    description="ETL quotidien options BTC Deribit",
    schedule="15 0 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["deribit", "options", "etl"],
) as dag:
    run_etl = BashOperator(
        task_id="run_daily_pipeline",
        bash_command=f"cd '{PROJECT_ROOT}' && {PYTHON} data/scripts/run_daily_pipeline.py",
    )
