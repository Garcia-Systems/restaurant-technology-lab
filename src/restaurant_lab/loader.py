"""Load a restaurant configuration into validated domain objects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .model import DataSource, OperatingPeriod, Restaurant, RestaurantValidationError


def load_restaurant(path: str | Path) -> Restaurant:
    """Load and validate a restaurant JSON file with useful configuration errors."""
    config_path = Path(path)
    try:
        document = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise RestaurantValidationError(f"restaurant configuration not found: {config_path}") from error
    except json.JSONDecodeError as error:
        raise RestaurantValidationError(
            f"restaurant configuration is not valid JSON at line {error.lineno}, column {error.colno}"
        ) from error

    if not isinstance(document, dict):
        raise RestaurantValidationError("restaurant configuration must be a JSON object")
    try:
        return _restaurant_from(document)
    except KeyError as error:
        raise RestaurantValidationError(f"missing required configuration field: {error.args[0]}") from error
    except TypeError as error:
        raise RestaurantValidationError(f"invalid configuration structure: {error}") from error


def _restaurant_from(document: dict[str, Any]) -> Restaurant:
    periods = tuple(
        OperatingPeriod(
            days=tuple(period["days"]),
            service=period["service"],
            opens=period["opens"],
            closes=period["closes"],
        )
        for period in document["operating_periods"]
    )
    sources = tuple(
        DataSource(
            identifier=source["id"],
            name=source["name"],
            provides=source["provides"],
        )
        for source in document["data_sources"]
    )
    return Restaurant(
        name=document["name"],
        location=document["location"],
        concept=document["concept"],
        fictional=document["fictional"],
        capacity=document["capacity"],
        operating_periods=periods,
        menu_categories=tuple(document["menu_categories"]),
        sales_channels=tuple(document["sales_channels"]),
        data_sources=sources,
    )
