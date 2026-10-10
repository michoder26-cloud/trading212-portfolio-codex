"""Read-only portfolio snapshot using the cloud's inherited HTTPS proxy."""

import json
import math
import os
import ssl
from datetime import UTC, datetime

import httpx
from pydantic import ValidationError

from trading212_mcp.client import Trading212Client
from trading212_mcp.errors import Trading212Error
from trading212_mcp.settings import Settings


def snapshot(account, positions):
    rows = []
    for position in positions:
        instrument = position.instrument
        impact = position.walletImpact
        value = impact.currentValue if impact else None
        if value is not None and (
            not math.isfinite(value) or impact.currency != account.currency
        ):
            value = None
        total = account.totalValue
        rows.append(
            {
                "ticker": instrument.ticker if instrument else None,
                "name": instrument.name if instrument else None,
                "quantity": position.quantity,
                "account_currency_value": value,
                "percent_of_total_account": 100 * value / total
                if value is not None
                and total is not None
                and math.isfinite(total)
                and total > 0
                else None,
            }
        )
    return {
        "observed_at": datetime.now(UTC).isoformat(),
        "account_currency": account.currency,
        "total_account_value": account.totalValue,
        "cash": account.cash.model_dump() if account.cash else None,
        "positions": rows,
        "note": "Weights include cash in the denominator. Missing or mismatched currency values remain null. This is a snapshot, not a live feed.",
    }


def main():
    try:
        settings = Settings.from_env()
    except ValidationError:
        raise SystemExit(
            "Configure TRADING212_API_KEY, TRADING212_API_SECRET and ENVIRONMENT securely before running."
        ) from None
    settings = settings.model_copy(update={"account_ttl": 0})
    ca_file = os.getenv("SSL_CERT_FILE")
    context = ssl.create_default_context(cafile=ca_file)
    proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    transport = httpx.HTTPTransport(proxy=proxy, verify=context, trust_env=True)
    try:
        with Trading212Client(settings, transport=transport) as client:
            account = client.get_account_summary()
            positions = client.get_positions()
        print(
            json.dumps(
                snapshot(account, positions),
                ensure_ascii=False,
                allow_nan=False,
                indent=2,
            )
        )
    except (Trading212Error, httpx.HTTPError):
        raise SystemExit(
            "Portfolio retrieval failed. Check credentials, read permissions and cloud network readiness; no orders were submitted."
        ) from None


if __name__ == "__main__":
    main()
