from typing import Optional
from pydantic import BaseModel


class TripQuery(BaseModel):
    country: Optional[str]
    start_date: Optional[str]  # Use strict date parsing/validation in prod
    end_date: Optional[str]
    rate: Optional[float]
    limit: int = 10
