"""Fail-closed admission policy for the temporary free Ox Alpha route."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.request import Request, urlopen

MODEL = "stealth/ox-alpha"
PROVIDER = "nous"
REASONING = "max"
BASE_URL = "https://inference-api.nousresearch.com/v1"
CATALOG_URL = f"{BASE_URL}/models"
BILLING_MODE = ""


def pricing_is_free(catalog: Any) -> tuple[bool, str]:
    if not isinstance(catalog, dict) or not isinstance(catalog.get("data"), list):
        return False, "official model catalog is malformed"
    matches = [
        item
        for item in catalog["data"]
        if isinstance(item, dict) and item.get("id") == MODEL
    ]
    if len(matches) != 1:
        return False, "exact model record is missing or duplicated"
    pricing = matches[0].get("pricing")
    if not isinstance(pricing, dict) or not pricing:
        return False, "pricing object is missing or empty"
    if "prompt" not in pricing or "completion" not in pricing:
        return False, "prompt or completion pricing is missing"
    for component, value in pricing.items():
        if isinstance(value, bool) or value is None:
            return False, f"pricing component {component} is not numeric zero"
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return False, f"pricing component {component} is not numeric zero"
        if not amount.is_finite() or amount != 0:
            return False, f"pricing component {component} is not zero"
    return True, "all official pricing components are zero"


def live_pricing_is_free() -> tuple[bool, str]:
    request = Request(
        CATALOG_URL,
        headers={"Accept": "application/json", "User-Agent": "1hermes-free-gate/1.0"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            catalog = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - every catalog failure must fail closed.
        return False, f"official pricing is unreadable ({type(exc).__name__})"
    return pricing_is_free(catalog)


def admission_error(
    provider: str | None,
    reasoning: str | None,
    *,
    allow_fallback: bool,
) -> str | None:
    if allow_fallback:
        return "Ox Alpha forbids --allow-fallback"
    if provider != PROVIDER:
        return f"Ox Alpha requires --provider {PROVIDER}"
    if reasoning != REASONING:
        return f"Ox Alpha requires --reasoning {REASONING}"
    return None
