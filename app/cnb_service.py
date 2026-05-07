from datetime import date, datetime, timedelta
import requests
from sqlalchemy.orm.session import Session

from app.models import CNBRates

CNB_DAILY_URL = "https://www.cnb.cz/en/financial_markets/foreign_exchange_market/exchange_rate_fixing/daily.txt"

def _parse_daily_text(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 3:
        raise ValueError("CNB ERROR")

    first_line = lines[0]
    date_part = first_line.split("#")[0].strip()
    rate_date = datetime.strptime(date_part, "%d %b %Y").date()

    result = []
    for line in lines[2:]:
        parts = line.split("|")
        if len(parts) != 5:
            continue

        amount_str = parts[2].strip()
        code = parts[3].strip().upper()
        rate_str = parts[4].strip().replace(",", ".")

        try:
            amount = int(amount_str)
            raw_rate = float(rate_str)
            rate_per_one = raw_rate / amount
        except ValueError:
            continue

        result.append(
            {
                "rate_date": rate_date,
                "currency_code": code,
                "raw_amount": amount,
                "raw_rate": raw_rate,
                "rate_per_one": rate_per_one,
            }
        )

    return rate_date, result


def sync_one_day(target_date: date, currencies: list[str], db: Session):
    date_for_url = target_date.strftime("%d.%m.%Y")
    response = requests.get(CNB_DAILY_URL, params={"date": date_for_url}, timeout=20)

    if response.status_code != 200:
        return {"date": str(target_date), "saved": 0, "status": f"HTTP {response.status_code}"}

    try:
        parsed_date, rows = _parse_daily_text(response.text)
    except Exception as exc:
        return {"date": str(target_date), "saved": 0, "status": f"parse_error: {exc}"}

    saved = 0
    wanted = {c.upper() for c in currencies}

    for row in rows:
        if row["currency_code"] not in wanted:
            continue
        
        exists = db.query(CNBRates).filter(
            CNBRates.rate_date == parsed_date,
            CNBRates.currency_code == row["currency_code"],
        ).first()
        if exists:
            continue

        db.add(CNBRates(
            rate_date=parsed_date,
            currency_code=row["currency_code"],
            rate_per_one=row["rate_per_one"],
            raw_amount=row["raw_amount"],
            raw_rate=row["raw_rate"],
        ))
        db.commit()
        
        saved += 1

    return {"date": str(target_date), "saved": saved, "status": "ok"}


def sync_period(start_date: date, end_date: date, currencies: list[str], db: Session):
    if end_date < start_date:
        raise ValueError("end_date не может быть меньше start_date")

    result = []
    current = start_date
    while current <= end_date:
        day_result = sync_one_day(current, currencies, db)
        result.append(day_result)
        current += timedelta(days=1)

    return result
