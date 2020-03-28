import requests


class TrackerAPI:
    AVAILABLE_DATA_SOURCES = ("jhu", "csbs")
    ENDPOINTS = {
        'latest_global_stats': '/latest',  # Getting latest total confirmed cases, deaths, and recoveries.
        'data_by_country': '/locations',  # get all case data by country
    }
    BASE_URL = 'https://coronavirus-tracker-api.herokuapp.com/v2'

    def __init__(self, data_source: str = 'jhu'):
        if data_source in self.AVAILABLE_DATA_SOURCES:
            self.data_source = data_source
        else:
            raise Exception('Invalid data source')

    def get_latest_global_stats(self) -> dict:
        """
        Get latest count of total cases, deaths, recovered
        :return: dict
        """
        resp = self._make_api_call(endpoint=self.ENDPOINTS['latest_global_stats'], params={})

        return resp['latest']

    def get_data_by_country(self, country_code: str = None, with_timelines: bool = False) -> dict:
        """
        Get data by countries
        :param country_code: country code to filter results, returns entire country list if not provided
        :param with_timelines: get the per day stats of cases
        :return: dict
        """
        params = dict(timelines=with_timelines)

        if country_code:
            params.update(country_code=country_code)

        return self._make_api_call(endpoint=self.ENDPOINTS['data_by_country'], params=params)

    def _make_api_call(self, endpoint: str, params: dict) -> dict:
        params['source'] = self.data_source
        url = f'{self.BASE_URL}{endpoint}'

        response = requests.get(url, params)

        response.raise_for_status()

        return response.json()


