from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm.session import Session
from sqlalchemy import func
from datetime import date

from app.config import SYNC_CURRENCIES, SYNC_INTERVAL_SECONDS
from app.models import Base, CNBRates
from app.db import engine, get_db
from app.scheduler import SyncScheduler
from app.cnb_service import sync_period
from app.schema import SyncRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    
    scheduler = SyncScheduler(SYNC_INTERVAL_SECONDS, SYNC_CURRENCIES)
    scheduler.start()
    
    yield
    
    scheduler.stop()


app = FastAPI(lifespan=lifespan)


@app.post("/sync")
def sync(body: SyncRequest, db: Session = Depends(get_db)):
    currency_list = [c.strip().upper() for c in body.currencies.split(",") if c.strip()]
    if not currency_list:
        raise HTTPException(status_code=400, detail="Список currencies пуст")
    
    data = sync_period(body.start_date, body.end_date, currency_list, db)
    print(body.start_date)
    print(body.end_date)
    if len(data):
        return {
            "status": "success",
            "details": [data],
        }
    
    return {"status": "success", "details": f"len data is {len(data)}"}


@app.get("/report")
def report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    currencies: str = Query(...),
    db: Session = Depends(get_db),
):
    currency_list = [c.strip().upper() for c in currencies.split(",") if c.strip()]
    if not currency_list:
        raise HTTPException(status_code=400, detail="Список currencies пуст")

    results = (
        db.query(
            CNBRates.currency_code,
            func.min(CNBRates.rate_per_one).label("min_rate"),
            func.max(CNBRates.rate_per_one).label("max_rate"),
            func.avg(CNBRates.rate_per_one).label("avg_rate"),
            func.count().label("points"),
        ).filter(
            CNBRates.rate_date >= start_date,
            CNBRates.rate_date <= end_date,
            CNBRates.currency_code.in_(currency_list),
        ).group_by(CNBRates.currency_code).order_by(CNBRates.currency_code).all()
    )
    
    return {
        "period": {"start_date": str(start_date), "end_date": str(end_date)},
        "currencies": currency_list,
        "report": [
            {"currency": r.currency_code, "min": r.min_rate, "max": r.max_rate, "avg": r.avg_rate, "points": r.points}
            for r in results
        ],
    }
