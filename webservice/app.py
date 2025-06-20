"""
This is a mock webservice to mimic the booking process.

This will contain the APIs that will be called by the langgraph agent.

The agent will be responsible for booking a reservation.

The agent will be responsible for searching for openings.

The agent will be responsible for checking the availability of a reservation.
"""

from collections import defaultdict
from datetime import date, datetime
from loguru import logger
from fastapi import Query, APIRouter
from fastapi import FastAPI
import numpy as np

import uvicorn
from webservice.schemas import (
    ResponseStatus,
    TripBookingRequest,
    TripSearchResultsResponse,
    ExistingTripReservationsResponse,
    TripBookingResponse,
    CountryCountsResponse,
    TripOpening,
    TripReservation,
    WebsiteUserProfile,
)
from webservice.data_generator.enums import Country
from webservice.data_generator.generator_funcs import (
    generate_vacation_openings,
)


NP_RANDOM = np.random.RandomState(1337)

app = FastAPI()
router = APIRouter(prefix="/api/trip")

USERS_DB = {
    "otani": WebsiteUserProfile(
        username="otani",
        home_country=Country.JAPAN,
        phone_number="555-687-1234",
        email="otani@gmail.com",
    ),
    "timur22": WebsiteUserProfile(
        username="timur22",
        home_country=Country.BRAZIL,
        phone_number="555-687-5794",
        email="timur@gmail.com",
    ),
}

OPENINGS_DB = dict()

# user_id -> reservation_id -> TripReservation
RESERVATIONS_DB: dict[str, TripReservation] = dict()

# kick off
OPENINGS_DB.update({row.opening_id: row for row in generate_vacation_openings(n=3000)})


@app.get("/healthcheck")
def read_root():
    return {"Hello": "World"}


@router.get("/openings/count")
def get_count():
    return len(OPENINGS_DB)


@router.get("/openings/countries", response_model=CountryCountsResponse)
def get_countries_count():
    country_counts = defaultdict(int)
    for opening in OPENINGS_DB.values():
        country_counts[opening.country] += 1

    return {
        "status": ResponseStatus.FOUND,
        "country_counts": dict(country_counts),
        "total_openings": len(OPENINGS_DB),
    }


@router.get("/openings/add")
def generate_openings(n: int = 10):
    new_rows = [row for row in generate_vacation_openings(n=n)]
    OPENINGS_DB.update({n.vid: n for n in new_rows})

    new_ct = len(OPENINGS_DB)
    return {
        "msg": f"{len(new_rows):,} rows added",
        "updated_rows_ct": new_ct,
        "record_ids": [n.vid for n in new_rows],
    }


@router.get("/openings/search", response_model=TripSearchResultsResponse)
def search_openings(
    country: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    room_rate: float | None = Query(None),
    limit: int | None = Query(10),
    days_count: int | None = Query(2),
):
    rows: list[TripOpening] = [r for r in OPENINGS_DB.values()]
    rate = room_rate

    search_params = dict()
    if country is not None:
        if country not in Country._value2member_map_:
            return {
                "results_count": 0,
                "search_params": {"country": country},
                "results": [],
                "status": ResponseStatus.NOT_AVAILABLE,
            }

        search_params["country"] = country
        rows = [r for r in rows if r.country == country]

    if start_date is not None:
        search_params["start_date"] = start_date
        rows = [r for r in rows if r.start_date >= start_date]

    if end_date is not None:
        search_params["end_date"] = end_date
        rows = [r for r in rows if r.end_date <= end_date]

    if rate is not None:
        search_params["rate"] = rate
        rows = [r for r in rows if r.day_rate <= rate]

    if days_count is not None:
        search_params["days_count"] = days_count
        scores_and_results = []
        for row in rows:
            score = abs(row.days_count - days_count) / max(days_count, row.days_count)
            row.ranking_score = round(score, 5)

        rows = sorted(rows, key=lambda x: x.ranking_score or -1, reverse=True)

    if limit:
        rows = rows[:limit]

    results_ct = len(rows)
    logger.debug(f"Found {results_ct} results")
    return {
        "results_count": results_ct,
        "search_params": search_params,
        "results": rows,
    }


@router.get("/reservations", response_model=ExistingTripReservationsResponse)
def get_reservations_list(user: str):
    reservations_index = RESERVATIONS_DB.get(user)
    if reservations_index is not None:
        return {"status": ResponseStatus.NOT_FOUND, "reservations": dict()}

    return {"status": ResponseStatus.FOUND, "reservations": reservations_index}


def _pop_opening_and_book_reservation(request: TripBookingRequest):
    opening = OPENINGS_DB.pop(request.opening_id)
    if not opening:
        return {
            "msg": "could not find reservation: {}".format(request.opening_id),
            "status": ResponseStatus.NOT_FOUND,
        }

    new_booking = {
        "vacation_opening": opening.model_dump(),
        "user": request.user,
        "home_country": request.user.home_country,
        "phone_number": request.user.phone_number,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "reservation_people_count": request.people_count,
    }

    ressy = TripReservation.model_validate(new_booking)
    RESERVATIONS_DB[ressy.reservation_id] = ressy
    return {"msg": "booking made", "status": ResponseStatus.CONFIRMED, "details": ressy}


@router.post("/reservations/book", response_model=TripBookingResponse)
def book_reservation(request: TripBookingRequest):
    """
    This is for testing only, since there is no competition.
    This is a mock function to mimic the booking process.
    It will return a booking response with a status of CONFIRMED.
    """
    return _pop_opening_and_book_reservation(request)


@router.post("/reservations/competitive_book", response_model=TripBookingResponse)
def book_reservation_against_others(request: TripBookingRequest):
    """
    This is a mock function to mimic the competitive booking process in a production setting.
    It will return a booking response with a status of NOT_AVAILABLE 30% of the time.
    If the booking is successful, it will return a booking response with a status of CONFIRMED.
    If the booking is not successful, it will return a booking response with a status of NOT_AVAILABLE.
    If the booking is not successful, it will return a booking response with a status of NOT_AVAILABLE.
    """
    # to mimick incase reservation doesn't exist again
    if NP_RANDOM.rand() > 0.3:
        return {
            "msg": "opening is no longer available",
            "status": ResponseStatus.NOT_AVAILABLE,
        }

    return _pop_opening_and_book_reservation(request)


# Mount the router with the /api prefix
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9009, reload=True)
