from sqlalchemy import Column, Integer, String, Date, Numeric

from app.db import Base

class CNBRates(Base):
    __tablename__ = "cnb_rates"
    id = Column(Integer, primary_key=True, index=True)
    rate_date = Column(Date, nullable=False)
    currency_code = Column(String, nullable=False)
    rate_per_one = Column(Numeric, nullable=False)
    raw_amount = Column(Integer, nullable=False)
    raw_rate = Column(Numeric, nullable=False)

    def __str__(self):
        return f"{self.rate_date}, {self.currency_code}, {self.rate_per_one}, {self.raw_amount}, {self.raw_rate}"