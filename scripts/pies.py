"""Read Pie configuration without submitting any account mutations."""

import json
import os
import ssl

import httpx
from pydantic import ValidationError

from trading212_mcp.client import Trading212Client
from trading212_mcp.errors import Trading212Error
from trading212_mcp.settings import Settings


def main():
    try:
        settings = Settings.from_env().model_copy(update={"account_ttl": 0})
    except ValidationError:
        raise SystemExit(
            "Configure API credentials and ENVIRONMENT securely."
        ) from None
    transport = httpx.HTTPTransport(
        proxy=os.getenv("HTTPS_PROXY") or os.getenv("https_proxy"),
        verify=ssl.create_default_context(cafile=os.getenv("SSL_CERT_FILE")),
        trust_env=True,
    )
    try:
        with Trading212Client(settings, transport=transport) as client:
            pies = client.get_pies()
            result = []
            for pie in pies:
                result.append(
                    {
                        "summary": pie.model_dump(mode="json"),
                        "detail": client.get_pie_by_id(pie.id).model_dump(mode="json")
                        if pie.id is not None
                        else None,
                    }
                )
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    except (Trading212Error, httpx.HTTPError):
        raise SystemExit(
            "Pie retrieval failed. Check credentials, permissions and network; no changes submitted."
        ) from None


if __name__ == "__main__":
    main()
