# Trading 212 Portfolio

Read your Trading 212 holdings, cash, portfolio weights and Pie configurations
on a local computer or a cloud environment. The included reader scripts support
inherited HTTPS proxy and CA settings and submit no trading orders.

Based on [trading212-mcp-server](https://github.com/RohanAnandPandit/trading212-mcp-server).
The upstream MIT license is preserved. Original documentation is available in
[UPSTREAM_README.md](UPSTREAM_README.md).

## Install

Install Git, [uv](https://docs.astral.sh/uv/getting-started/installation/) and
Python 3.11–3.14, then run:

```sh
git clone https://github.com/chaiz-env/trading212-portfolio.git
cd trading212-portfolio
uv sync --frozen
```

For this private repository, authenticate to GitHub with an account that has
repository access. GitHub stores the code; it does not run the portfolio reader
or preserve your Trading 212 account connection automatically.

## Configure Trading 212 credentials

Generate an API Key and API Secret in the appropriate Trading 212 account.
Grant only the read permissions needed for account data, positions and Pies.
Trading permissions are unnecessary for these reader scripts. See the
[Trading 212 API documentation](https://docs.trading212.com/api) for supported
accounts and current permissions.

If `.env` does not already exist, create it from the template. On Linux/macOS:

```sh
cp .env.example .env
chmod 600 .env
nano .env
```

Do not overwrite an existing `.env`. On Windows, create and edit the file with
a text editor, ensuring its name is `.env`, not `.env.txt`. Enter values yourself:

```dotenv
TRADING212_API_KEY=YOUR_API_KEY
TRADING212_API_SECRET=YOUR_API_SECRET
ENVIRONMENT=demo
TRANSPORT=stdio
```

- Use `demo` with credentials generated for your paper account.
- Use `live` with credentials generated for your real account.
- In nano, save with Ctrl+O, Enter, then exit with Ctrl+X.
- Alternatively, use your environment's secure secret controls, if available,
  with the same variable names. Process environment variables override `.env`.
- Never paste credentials into chat, commit them to GitHub or include them in
  command arguments. A read-only cloud file viewer cannot edit `.env`; you need
  an actual editor, terminal or secure secret configuration facility.

## Read your portfolio

Run from the repository root, where `.env` is located:

```sh
uv run --frozen python scripts/portfolio.py
```

The JSON output includes account currency, total value, cash, tickers,
quantities, account-currency position values and portfolio weights. Each weight
is the position value divided by total account value, including cash. A €250
position in a €1,000 account represents 25%.

Missing or mismatched currency values remain `null` rather than being estimated.
Account and position reads are sequential, not an atomic snapshot or live stream.
Run the command again whenever you need updated data.

## Read your Pies

```sh
uv run --frozen python scripts/pies.py
```

This reads each Pie's summary and details without changing its configuration.
`expectedShare` is the target allocation; `currentShare` is the current allocation.
A value of `0.2` means 20%. An unfunded Pie can have target weights while its
actual holdings and values remain zero.

## Use with ChatGPT

There are three different workflows. Only the first two work with this
repository as it stands; a direct ChatGPT MCP app requires additional setup.

### 1. Ask ChatGPT to run the scripts in a connected cloud environment

Use a ChatGPT session that actually provides shell execution and access to your
cloud workspace. This is the workflow used to set up this project. Ordinary
chat sessions without execution tools cannot clone repositories or run Python.

1. Give the session access to this private repository through a supported
   GitHub connection or authenticated Git in its environment.
2. Ask it to clone the repository and install dependencies.
3. Configure credentials privately in that environment using an editor,
   terminal or supported secret controls. Do not assume the cloud file viewer
   has an editor or a Secrets menu.
4. After configuration, ask it to run the reader and summarize the results.

Example setup prompt:

```text
Set up https://github.com/chaiz-env/trading212-portfolio in my connected
cloud workspace. Read README.md and AGENTS.md, install with uv sync --frozen,
and tell me how to configure credentials privately using the facilities
actually available here. Do not display credential files or submit orders.
```

Example prompts after credentials are configured:

```text
From the trading212-portfolio directory, run:
uv run --frozen python scripts/portfolio.py
Summarize my holdings, cash and weights including cash. Report missing data
and when the snapshot was retrieved. Do not place any trades.
```

```text
Run uv run --frozen python scripts/pies.py from the repository root.
Show each Pie's target weights and current allocation separately.
Do not modify any Pie or submit orders.
```

A GitHub connection alone does not give ChatGPT your Trading 212 credentials
or guarantee that Python execution is available. This workflow runs scripts;
it does not register the upstream server as a ChatGPT app. The original MCP
client disables environment proxy discovery; the cloud reader scripts explicitly
preserve proxy and CA settings instead.

### 2. Upload a snapshot to a normal ChatGPT conversation

Run the reader on your own configured computer and save the output:

```sh
uv run --frozen python scripts/portfolio.py > portfolio-snapshot.json
uv run --frozen python scripts/pies.py > pies-snapshot.json
```

Upload only these financial snapshots to ChatGPT if you want to share their
contents, then ask for a holdings table, allocation comparison or concentration
analysis. Do not upload `.env`, API credentials or API caches. Snapshot output
is private financial data, even though it contains no API credentials. It does
not update automatically; generate a new snapshot when needed.

### 3. Connect a custom MCP app to ChatGPT (additional work required)

ChatGPT uses remote MCP connections rather than directly launching this
repository's local stdio server. Custom app availability and setup depend on
plan and workspace permissions. Eligible users configure an app with a
reachable MCP endpoint and its authentication, scan its tools, then select
it in chat. See the current
[OpenAI developer mode and MCP apps guide](https://help.openai.com/en/articles/12584461)
for supported access and setup steps.

**This repository does not provide that hosted, authenticated integration.**
The upstream server binds HTTP transports to localhost and is designed for a
single account. Do not expose it through an unauthenticated public tunnel.
A direct ChatGPT app needs a separately designed authenticated deployment or
supported private connectivity, with credentials kept on the server and only
the intended read tools exposed. Follow OpenAI's current guidance and review
compatibility before choosing a connectivity approach.

For a local MCP client that supports stdio, see
[the upstream setup instructions](UPSTREAM_README.md#setup). That configuration
is distinct from creating a ChatGPT custom app.

## Move to another computer, cloud or account

1. Give the new GitHub account access to the private repository, or transfer
   repository ownership if appropriate.
2. Clone it in the new environment and run `uv sync --frozen`.
3. Configure a new private `.env` or supported secret bindings there.
4. For a different Trading 212 account, supply that account's credentials and
   select the matching `demo` or `live` environment.
5. Run the readers again. Old chat history does not prove the new account's
   current holdings; retrieve a fresh snapshot.

Moving ChatGPT accounts does not automatically migrate repository access,
credentials, cloud files or a custom app connection.

## Troubleshooting

- `401`: Check that Key/Secret are a matching pair and the environment matches.
- `403`: Check API permissions and any configured IP restrictions.
- `429`: Wait and retry according to the provider's rate limits.
- Configuration error: Check variable names and run from the repository root.
- Network error: Check HTTPS proxy, trusted CA settings and cloud network policy.
  Keep TLS verification enabled.

## Privacy and validation

The initial publication excludes credentials, `.env`, caches, uploaded files
and private portfolio snapshots. `.gitignore` covers common private file names,
but inspect every commit and never force-add secrets. API caches may contain
financial data in plaintext and belong on private storage.

The upstream MCP server includes trading and Pie mutation tools; the two reader
scripts only retrieve data. No authenticated account calls are needed to run
the test suite:

```sh
uv run --frozen pytest -q
```

The initial local suite passed 96 tests. See
[PORTFOLIO_SETUP.md](PORTFOLIO_SETUP.md) for a short migration checklist.
