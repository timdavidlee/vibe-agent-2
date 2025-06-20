import datetime
from enum import StrEnum
from pydantic import BaseModel, field_validator, Field
from webservice.data_generator.enums import Country, LodgingClass, HotelCompany
from typing import Any
from uuid import uuid4


class WebsiteUserProfile(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    home_country: Country
    phone_number: str
    email: str


class TripOpening(BaseModel):
    opening_id: str = Field(default_factory=lambda: str(uuid4()))
    start_date: datetime.datetime
    end_date: datetime.datetime
    country: Country
    lodging_class: LodgingClass
    day_rate: float
    hotel_company: HotelCompany
    # optional ranking score for sorting results by relevance
    ranking_score: float | None = -1

    @property
    def days_count(self) -> int:
        return (self.end_date - self.start_date).days


class TripReservation(BaseModel):
    reservation_id: str = Field(default_factory=lambda: str(uuid4()))
    trip_opening: TripOpening
    reservation_people_count: int
    user: str
    home_country: Country
    phone_number: str
    start_date: datetime.date
    end_date: datetime.date


class ResponseStatus(StrEnum):
    CONFIRMED = "confirmed"
    NOT_AVAILABLE = "not-available"
    NOT_FOUND = "not-found"
    FOUND = "found"
    ERROR = "error"


class TripBookingRequest(BaseModel):
    opening_id: str
    user: WebsiteUserProfile
    start_date: datetime.datetime
    end_date: datetime.datetime
    days_count: int
    people_count: int


class TripSearchRequest(BaseModel):
    country: Country | None = None
    start_date: datetime.datetime | None = None
    end_date: datetime.datetime | None = None
    rate: float | int | None = None
    limit: int | None = None


class TripSearchResultsResponse(BaseModel):
    status: ResponseStatus = ResponseStatus.FOUND
    results_count: int
    search_params: dict[str, Any]
    results: list[TripOpening]


class ExistingTripReservationsResponse(BaseModel):
    status: ResponseStatus
    reservations: dict[str, TripReservation]


class TripBookingResponse(BaseModel):
    msg: str = ""
    status: ResponseStatus
    details: TripReservation | None = None


class CountryCountsResponse(BaseModel):
    status: ResponseStatus = ResponseStatus.FOUND
    country_counts: dict[Country, int]
    total_openings: int
