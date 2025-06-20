from enum import StrEnum


class HotelCompany(StrEnum):
    JINJIAN = "Jin Jiang International"
    WYNDHAM = "Wyndham Hotels & Resorts"
    MARRIOTT = "Marriott Interational"
    HUAZHU = "Huazhu Hotels Group"
    CHOICE = "Choice Hotels International"
    HILTON = "Hilton Worldwide"
    IHG = "IHG Hotels & Resorts"
    BTG = "BTG Home Inns"
    ACCOR = "Accor"
    BWH = "BWH Hotel Group"


class LodgingClass(StrEnum):
    STUDIO = "studio"
    ONE_BED = "one_bedroom"
    TWO_BED = "two_bedroom"
    THREE_BED = "three_bedroom"
    SUITE = "suite"
    CABIN = "cabin"
    LUXURY = "luxury"


LODGING_RATE_RANGE = {
    LodgingClass.STUDIO: (200, 400),
    LodgingClass.ONE_BED: (300, 600),
    LodgingClass.TWO_BED: (400, 800),
    LodgingClass.THREE_BED: (600, 1200),
    LodgingClass.SUITE: (800, 1500),
    LodgingClass.CABIN: (1000, 1800),
    LodgingClass.LUXURY: (1500, 3000),
}


class Country(StrEnum):
    INDIA = "India"
    CHINA = "China"
    UNITED_STATES = "United States"
    INDONESIA = "Indonesia"
    PAKISTAN = "Pakistan"
    NIGERIA = "Nigeria"
    BRAZIL = "Brazil"
    BANGALDESH = "Bangladesh"
    RUSSIA = "Russia"
    MEXICO = "Mexico"
    JAPAN = "Japan"
    PHILIPPINES = "Philippines"
    ETHIOPIA = "Ethiopia"
    CONGO = "Democratic Republic of the Congo"
    EGYPT = "Egypt"
    VIETNAM = "Vietnam"
    IRAN = "Iran"
    TURKEY = "Turkey"
    GERMANY = "Germany"
    FRANCE = "France"
    UNITED_KINGDOM = "United Kingdom"
    TANZANIA = "Tanzania"
    THAILAND = "Thailand"
    SOUTH_AFRICA = "South Africa"
    ITALY = "Italy"
    COLOMBIA = "Colombia"
    KENYA = "Kenya"
    MYANMAR = "Myanmar"
    SOUTH_KOREA = "South Korea"
    SUDAN = "Sudan"
