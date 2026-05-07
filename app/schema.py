from pydantic import BaseModel
from datetime import date

class SyncRequest(BaseModel):
    currencies: str
    start_date: date
    end_date: date