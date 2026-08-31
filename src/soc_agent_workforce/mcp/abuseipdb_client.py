from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

ABUSEIPDB_API_URL = "https://api.abuseipdb.com/api/v2/check"


@traceable(name="tool_check_ip_reputation")
def check_ip_reputation(
    ip_address: str,
    categories: list[int] | None = None,
    max_age_in_days: int | None = None,
    verbose: bool | None = None,
) -> dict[str, Any]:
    """Query AbuseIPDB for a public IP reputation score and metadata.

    Returns a normalized dictionary with the abuse confidence score, total reports,
    categories, country and ISP metadata, and a verdict summary. If the API key is
    missing or the endpoint is rate-limited, this function returns a structured
    error payload instead of raising an uncaught exception.
    """
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        return {
            "ip": ip_address,
            "is_public": None,
            "abuse_confidence_score": None,
            "total_reports": 0,
            "categories": [],
            "country_code": None,
            "country": None,
            "isp": None,
            "domain": None,
            "verdict": "unknown",
            "status": "missing_api_key",
            "message": "ABUSEIPDB_API_KEY is not set. Add it to the project root .env file.",
        }

    params: dict[str, Any] = {"ipAddress": ip_address}
    if categories:
        params["categories"] = ",".join(str(value) for value in categories)
    if max_age_in_days is not None:
        params["maxAgeInDays"] = int(max_age_in_days)
    if verbose is not None:
        params["verbose"] = str(verbose).lower()

    try:
        response = httpx.get(
            ABUSEIPDB_API_URL,
            params=params,
            headers={
                "Key": api_key,
                "Accept": "application/json",
            },
            timeout=15.0,
        )
    except httpx.HTTPError as exc:
        return {
            "ip": ip_address,
            "is_public": None,
            "abuse_confidence_score": None,
            "total_reports": 0,
            "categories": [],
            "country_code": None,
            "country": None,
            "isp": None,
            "domain": None,
            "verdict": "unknown",
            "status": "request_error",
            "message": f"AbuseIPDB request failed: {exc}",
        }

    if response.status_code == 429:
        return {
            "ip": ip_address,
            "is_public": None,
            "abuse_confidence_score": None,
            "total_reports": 0,
            "categories": [],
            "country_code": None,
            "country": None,
            "isp": None,
            "domain": None,
            "verdict": "unknown",
            "status": "rate_limited",
            "message": "AbuseIPDB rate limit reached. Try again later.",
        }

    if response.status_code in {401, 403}:
        return {
            "ip": ip_address,
            "is_public": None,
            "abuse_confidence_score": None,
            "total_reports": 0,
            "categories": [],
            "country_code": None,
            "country": None,
            "isp": None,
            "domain": None,
            "verdict": "unknown",
            "status": "invalid_api_key",
            "message": "The AbuseIPDB API key is invalid or unauthorized.",
        }

    if response.status_code >= 400:
        detail = response.text[:500]
        return {
            "ip": ip_address,
            "is_public": None,
            "abuse_confidence_score": None,
            "total_reports": 0,
            "categories": [],
            "country_code": None,
            "country": None,
            "isp": None,
            "domain": None,
            "verdict": "unknown",
            "status": "api_error",
            "message": f"AbuseIPDB API returned HTTP {response.status_code}: {detail}",
        }

    try:
        payload = response.json()
    except ValueError:
        return {
            "ip": ip_address,
            "is_public": None,
            "abuse_confidence_score": None,
            "total_reports": 0,
            "categories": [],
            "country_code": None,
            "country": None,
            "isp": None,
            "domain": None,
            "verdict": "unknown",
            "status": "invalid_response",
            "message": "AbuseIPDB returned an invalid JSON payload.",
        }

    data = payload.get("data", {})
    score = int(data.get("abuseConfidenceScore", 0) or 0)
    categories_value = data.get("categories") or []

    if score >= 80:
        verdict = "malicious"
    elif score >= 50:
        verdict = "suspicious"
    elif score > 0:
        verdict = "low_risk"
    else:
        verdict = "clean"

    return {
        "ip": data.get("ipAddress", ip_address),
        "is_public": data.get("isPublic"),
        "abuse_confidence_score": score,
        "total_reports": int(data.get("totalReports", 0) or 0),
        "categories": categories_value,
        "country_code": data.get("countryCode"),
        "country": data.get("countryName") or data.get("country"),
        "isp": data.get("isp"),
        "domain": data.get("domain"),
        "verdict": verdict,
        "status": "ok",
        "message": "AbuseIPDB lookup succeeded.",
    }
