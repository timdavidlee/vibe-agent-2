from pydantic import BaseModel, Field

import datetime
from uuid import uuid4
from datetime import timedelta

from webservice.data_generator.enums import Country, LodgingClass, HotelCompany
from webservice.data_generator.randomizer import (
    generate_countries,
    generate_hotel,
    generate_lodging,
    generate_start_dates,
    generate_durations,
)
from webservice.schemas import TripOpening


def generate_vacation_openings(n: int = 100):
    countries = generate_countries(n)
    hotels = generate_hotel(n)
    lodge_classes = generate_lodging(n)
    start_dates = generate_start_dates(n)
    durations = generate_durations(n)

    collector = []
    zip_package = zip(countries, hotels, lodge_classes, start_dates, durations)

    for c, h, lc, s, d in zip_package:
        l, r = lc
        collector.append(
            TripOpening(
                start_date=s,
                end_date=s + timedelta(days=int(d)),
                country=c,
                lodging_class=l,
                day_rate=r,
                hotel_company=h,
            )
        )
    return collector
