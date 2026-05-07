import requests
from datetime import date

SYNC_CURRENCIES = "USD,EUR"
API_HOST = "127.0.0.1"
API_PORT = "5003"

BASE_URL = f"http://{API_HOST}:{API_PORT}"


def run_cli():
    print("\n=== Курс чешской кроны ===")
    print(f"Валюты для синхронизации по умолчанию: {''.join(SYNC_CURRENCIES)}")

    while True:
        print("\nВыберите действие:")
        print("1 - Ручная синхронизация за сегодня")
        print("2 - Ручная синхронизация за период")
        print("3 - Получить отчет через API")
        print("0 - Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("Выход из клиента.")
            return
        if choice == "1":
            do_sync_today()
        elif choice == "2":
            do_sync_period()
        elif choice == "3":
            do_report_request()
        else:
            print("Недопустимый пункт меню.")


def do_sync_today():
    currencies_raw = input("currencies через запятую (например USD,EUR): ").strip()
    today = date.today()
    try:
        response = requests.post(
            f"{BASE_URL}/sync",
            json={"start_date": str(today), "end_date": str(today), "currencies": currencies_raw},
            timeout=60,
        )
        print("HTTP:", response.status_code)
        print(response.json())
    except requests.RequestException as exc:
        print(f"Ошибка запроса к API: {exc}")


def do_sync_period():
    start_raw = input("Введите start_date (YYYY-MM-DD): ").strip()
    end_raw = input("Введите end_date (YYYY-MM-DD): ").strip()
    currencies_raw = input("currencies через запятую (например USD,EUR): ").strip()

    try:
        response = requests.post(
            f"{BASE_URL}/sync",
            json={"start_date": start_raw, "end_date": end_raw, "currencies": currencies_raw},
            timeout=300,
        )
        print("HTTP:", response.status_code)
        print(response.json())
    except requests.RequestException as exc:
        print(f"Ошибка запроса к API: {exc}")


def do_report_request():
    start_raw = input("start_date (YYYY-MM-DD): ").strip()
    end_raw = input("end_date (YYYY-MM-DD): ").strip()
    currencies_raw = input("currencies через запятую (например USD,EUR): ").strip()

    try:
        response = requests.get(
            f"{BASE_URL}/report",
            params={
                "start_date": start_raw,
                "end_date": end_raw,
                "currencies": currencies_raw,
            },
            timeout=20,
        )
        print("HTTP:", response.status_code)
        print(response.json())
    except requests.RequestException as exc:
        print(f"Ошибка запроса к API: {exc}")
        
run_cli()
