"""Utilities for translating natural-language queries to SerpApi parameters."""

from __future__ import annotations

import os
import re
import unicodedata
from datetime import date, timedelta
from typing import Dict, Optional, Tuple

import requests


CITY_TO_IATA = {
    # México
    "CDMX": "MEX",
    "CIUDAD DE MEXICO": "MEX",
    "MEXICO": "MEX",
    "MEXICO CITY": "MEX",
    # USA
    "SAN FRANCISCO": "SFO",
    "NEW YORK": "NYC",
    "NUEVA YORK": "NYC",
    "LOS ANGELES": "LAX",
    "SAN JOSE": "SJC",
    # Europa
    "PARIS": "PAR",
    "LONDRES": "LON",
    "LONDON": "LON",
    # Asia
    "TOKIO": "TYO",
    "TOKYO": "TYO",
    # Generic tokens
    "NYC": "NYC",
}

# Minimal list of active international airports used for validation.
ACTIVE_INTL_AIRPORTS = {
    "MEX",
    "SFO",
    "NYC",
    "LAX",
    "SJC",
    "PAR",
    "LON",
    "TYO",
}

AIRLINES = {
    "AEROMEXICO": "AM",
    "DELTA": "DL",
    "UNITED": "UA",
}

TRAVEL_CLASS = {
    "ECONOMICA": "1",
    "ECONOMÍA": "1",
    "NEGOCIOS": "2",
    "BUSINESS": "2",
    "EJECUTIVA": "2",
    "PRIMERA": "3",
    "FIRST": "3",
}


def _normalize(text: str) -> str:
    """Return ``text`` upper-cased and without diacritics."""
    text = text.upper()
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _lookup_city(name: str, maps_key: Optional[str]) -> Optional[str]:
    """Resolve city name to an IATA code, optionally using Google Places."""
    key = _normalize(name)
    if key in CITY_TO_IATA:
        return CITY_TO_IATA[key]
    if maps_key:
        try:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {"query": f"airport {name}", "key": maps_key}
            resp = requests.get(url, params=params, timeout=5)
            resp.raise_for_status()
            for res in resp.json().get("results", []):
                m = re.search(r"\b([A-Z]{3})\b", res.get("name", ""))
                if m:
                    return m.group(1)
        except Exception:
            pass
    return None


def _resolve_airport(token: str, maps_key: Optional[str]) -> Optional[str]:
    token = _normalize(token)
    if re.fullmatch(r"[A-Z]{3}", token):
        return token
    return _lookup_city(token, maps_key)


def _extract_airports(text: str, maps_key: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    clean = _normalize(re.sub(r"[^\w\s]", " ", text))
    words = clean.split()
    found: list[Tuple[int, str]] = []
    for size in range(3, 0, -1):
        for i in range(len(words) - size + 1):
            phrase = " ".join(words[i : i + size])
            code = _resolve_airport(phrase, maps_key)
            if code and code in ACTIVE_INTL_AIRPORTS:
                found.append((i, code))
    found.sort(key=lambda x: x[0])
    codes: list[str] = []
    for _, code in found:
        if code not in codes:
            codes.append(code)
    dep = codes[0] if codes else None
    arr = codes[1] if len(codes) > 1 else None
    if dep and dep not in ACTIVE_INTL_AIRPORTS:
        dep = None
    if arr and arr not in ACTIVE_INTL_AIRPORTS:
        arr = None
    return dep, arr


def _next_weekday(d: date) -> date:
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def _extract_dates(text: str) -> Tuple[str, Optional[str]]:
    """Return outbound and optional return dates."""
    today = date.today()
    full_dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)
    if full_dates:
        out = date.fromisoformat(full_dates[0])
        ret = date.fromisoformat(full_dates[1]) if len(full_dates) > 1 else None
        return out.isoformat(), ret.isoformat() if ret else None

    m = re.search(r"(\d{1,2})\D+al\D+(\d{1,2})", text)
    if m:
        start_day = int(m.group(1))
        end_day = int(m.group(2))
        month = today.month
        year = today.year
        if start_day <= today.day:
            month += 1
            if month == 13:
                month = 1
                year += 1
        out = date(year, month, start_day)
        ret = date(year, month, end_day)
        return out.isoformat(), ret.isoformat()

    d_match = re.search(r"\b(\d{1,2})\b", text)
    if d_match:
        day = int(d_match.group(1))
        month = today.month if day > today.day else today.month + 1
        if month == 13:
            month = 1
            year = today.year + 1
        else:
            year = today.year
        out = date(year, month, day)
    else:
        out = _next_weekday(today + timedelta(days=3))

    ret = None
    if "solo ida" not in text.lower():
        ret = _next_weekday(out + timedelta(days=3))

    return out.isoformat(), ret.isoformat() if ret else None


def build_flight_params(
    text: str,
    api_key: str,
    *,
    hl: str = "es",
    gl: str = "mx",
    currency: str = "USD",
    travel_class: str = "1",
) -> Dict[str, str]:
    """Convert a natural language request into SerpApi parameters for flights."""
    maps_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    dep, arr = _extract_airports(text, maps_key)
    out_date, ret_date = _extract_dates(text)

    params = {
        "api_key": api_key,
        "engine": "google_flights",
        "hl": hl,
        "gl": gl,
        "currency": currency,
        "travel_class": travel_class,
        "bags": "1",
    }
    if dep:
        params["departure_id"] = dep
    if arr:
        params["arrival_id"] = arr
    if out_date:
        params["outbound_date"] = out_date
    if ret_date:
        params["return_date"] = ret_date

    upper = _normalize(text)
    for name, code in AIRLINES.items():
        if name in upper:
            params["include_airlines"] = code
            break

    for key, cls in TRAVEL_CLASS.items():
        if key in upper:
            params["travel_class"] = cls
            break
    return params
