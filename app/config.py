"""Конфигурация проекта 3 (синхронизация курса CZK)."""

import os

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "5003"))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:5432/arch_lab_project_3",
)

SYNC_CURRENCIES = [item.strip().upper() for item in os.getenv("SYNC_CURRENCIES", "USD,EUR").split(",") if item.strip()]
SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", "86400"))
