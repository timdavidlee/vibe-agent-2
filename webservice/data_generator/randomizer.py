import numpy as np
from numpy.typing import ArrayLike
from enum import Enum
import pandas as pd
from loguru import logger

from webservice.data_generator.enums import (
    Country,
    LodgingClass,
    HotelCompany,
    LODGING_RATE_RANGE,
)
from webservice.data_generator.enums import LODGING_RATE_RANGE

RANDOM_STATE = np.random.RandomState(42)


def _generate_choice_probs(n: int) -> ArrayLike:
    vals = np.arange(1, n + 1)
    fracs = 1 / vals
    prof = fracs / fracs.sum()
    return prof


def _generate_weighted_sample(var_enum: type[Enum], generated_ct: int):
    vals = list(var_enum.__members__.values())
    probs = _generate_choice_probs(len(vals))
    return RANDOM_STATE.choice(np.array(vals), size=generated_ct, p=np.array(probs))


def generate_countries(n: int):
    return _generate_weighted_sample(Country, generated_ct=n)


def generate_lodging(n: int):
    lodgings = _generate_weighted_sample(LodgingClass, generated_ct=n)
    collector = []
    for ld in lodgings:
        low, high = LODGING_RATE_RANGE[ld]
        rate = RANDOM_STATE.randint(low, high)
        collector.append([ld, rate])
    return collector


def generate_hotel(n: int):
    return _generate_weighted_sample(HotelCompany, generated_ct=n)


def generate_start_dates(n: int):
    annual_dates = pd.date_range("2024-01-01", "2024-12-31")
    annual_dates = [ad.date() for ad in annual_dates]
    return RANDOM_STATE.choice(annual_dates, size=n)


def generate_durations(n: int):
    return RANDOM_STATE.randint(2, 30, size=n)
