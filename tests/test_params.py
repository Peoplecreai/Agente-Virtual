import re
from datetime import date, timedelta

from services.params import build_flight_params


def test_build_flight_params_full_dates():
    text = "Viaje de CDMX a SFO del 2024-09-05 al 2024-09-09"
    params = build_flight_params(text, api_key="demo")
    assert params["departure_id"] == "MEX"
    assert params["arrival_id"] == "SFO"
    assert params["outbound_date"] == "2024-09-05"
    assert params["return_date"] == "2024-09-09"
    assert params["engine"] == "google_flights"
    assert params["bags"] == "1"


def test_build_flight_params_partial_dates():
    text = "CDMX a SFO del 5 al 9"
    params = build_flight_params(text, api_key="demo")
    assert params["departure_id"] == "MEX"
    assert params["arrival_id"] == "SFO"
    assert re.match(r"\d{4}-\d{2}-\d{2}", params["outbound_date"])
    assert re.match(r"\d{4}-\d{2}-\d{2}", params["return_date"])
    assert params["bags"] == "1"


def test_compound_city_and_one_way():
    text = "Vuelo de Ciudad de México a San José solo ida con Aeromexico en negocios"
    params = build_flight_params(text, api_key="demo")
    assert params["departure_id"] == "MEX"
    assert params["arrival_id"] == "SJC"
    assert "return_date" not in params
    assert params.get("include_airlines") == "AM"
    assert params["travel_class"] == "2"
    assert params["bags"] == "1"


def test_default_dates_future_weekdays():
    text = "CDMX a SFO"
    params = build_flight_params(text, api_key="demo")
    out = date.fromisoformat(params["outbound_date"])
    assert out >= date.today() + timedelta(days=3)
    assert out.weekday() < 5
    assert params["bags"] == "1"

