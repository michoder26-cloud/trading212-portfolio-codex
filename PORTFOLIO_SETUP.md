# Portable Trading 212 portfolio reader

This repository includes the upstream MCP server and a read-only cloud portfolio
reader in `scripts/portfolio.py`. Preserve the upstream MIT license.

## Setup on a new machine or cloud account

1. Install Git, uv and Python 3.11 or newer.
2. Clone your repository and change into its directory.
3. Run `uv sync --frozen`.
4. Create a private `.env` file in the repository root. Configure these locally,
   never in GitHub files, issues, chat messages or command arguments:

```dotenv
TRADING212_API_KEY=
TRADING212_API_SECRET=
ENVIRONMENT=demo
TRANSPORT=stdio
```

Use API credentials from the appropriate Trading 212 account, with only account
and position read permissions. On Linux use `chmod 600 .env`. Use `demo` for a
paper account or deliberately set `live` to read the real account. Do not reuse
a demo key for the live environment.

5. Run `uv run --frozen python scripts/portfolio.py`.

The script reads account summary and positions only, preserves HTTPS proxy and
CA settings, and prints current holdings and weights as JSON. Weights divide
position value in the account currency by total account value, including cash.
Missing or mismatched currency values remain null. Reads are sequential, not an
atomic or streaming snapshot. No orders are submitted by this script.

## Moving accounts

For a new ChatGPT/cloud account, clone this repository and repeat setup with a
new private `.env`. For a different Trading 212 account, supply that account's
credentials. GitHub stores code, not your portfolio or account connection;
credentials and local caches are intentionally excluded. Private financial data
can exist in API caches on disk; do not upload those caches or snapshot outputs.

The upstream MCP server also exposes trading tools. Running this reader does
not register a ChatGPT plugin. Do not expose the upstream local server using a
public tunnel without a separately designed authenticated hosting solution.

## Validation

Initial publication: all 96 upstream tests passed locally. Allocation checks
covered a 25% holding, mismatched currencies, and a zero account total.

Sources: https://github.com/RohanAnandPandit/trading212-mcp-server
and https://docs.trading212.com/api

For ChatGPT cloud execution, snapshot uploads and the additional requirements
for a custom MCP app, see [Use with ChatGPT](README.md#use-with-chatgpt).
