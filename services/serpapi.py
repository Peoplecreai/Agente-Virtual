import os
import logging
from typing import Any, List
import requests

logger = logging.getLogger(__name__)


class SerpAPIService:
    """Wrapper around SerpApi endpoints used for flights and hotels."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("SERPAPI_KEY")
        if not self.api_key:
            logger.warning("SERPAPI_KEY not set; SerpApi disabled")
        self.base_url = "https://serpapi.com"

    def _request(self, endpoint: str, params: dict) -> Any:
        if not self.api_key:
            return None
        url = f"{self.base_url}/{endpoint}.json"
        params["api_key"] = self.api_key
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("SerpApi request failed: %s", e)
        return None

    def search_flights(self, origin: str, destination: str, date: str) -> List[dict]:
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": date,
            "bags": "1",
        }
        data = self._request("search", params)
        return data.get("flights_results", []) if data else []

    def search_hotels(self, city: str, check_in: str, check_out: str) -> List[dict]:
        params = {
            "engine": "google_hotels",
            "q": city,
            "check_in_date": check_in,
            "check_out_date": check_out,
        }
        data = self._request("search", params)
        return data.get("hotels_results", []) if data else []
