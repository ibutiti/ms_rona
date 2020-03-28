import pycountry


def get_country(name: str) -> str:
    result = pycountry.countries.search_fuzzy(name)
    return result[0]


def get_country_code(search_text):
    country = get_country(search_text)
    return country.alpha_2

