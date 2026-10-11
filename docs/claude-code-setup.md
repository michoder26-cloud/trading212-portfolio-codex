# Use with Claude Code on the web

These steps connect a Claude Code cloud session (claude.ai/code or the Claude
app) to your Trading 212 account so Claude can run the read-only reader
scripts. They were worked out on a real setup; the pitfalls section lists the
mistakes that caused failures along the way.

Claude cloud sessions run in a container behind an egress proxy. Two things
must be configured in the session's **environment** before Claude can reach
Trading 212:

1. **Network access** to `live.trading212.com` and/or `demo.trading212.com`.
   Without it, every request fails with `CONNECT tunnel failed, response 403`.
2. **Credentials**. Trading 212 uses HTTP Basic authentication: the API Key is
   the username and the API Secret is the password. It does **not** use Bearer
   tokens.

Never paste an API Key or Secret into the chat. Enter them only in the
environment settings.

## 1. Create a read-only API key

1. In the Trading 212 app or website, switch to the account you want to read:
   **Invest** (real money, `live`) or **Practice** (paper money, `demo`). A key
   works only for the account it was created in.
2. Open **Settings → API (Beta) → Generate API key**.
3. Grant only the read permissions needed for account data, portfolio and
   Pies. Do not grant order or trading permissions.
4. Copy the API Key and the API Secret right away. The Secret is shown only
   once.

## 2. Add the key to the environment (recommended: network secret)

With a network secret, the proxy adds the `Authorization` header to every
request to the allowed hosts. Claude never sees the key or secret, and the
proxy replaces any `Authorization` header the scripts send themselves.

Open the environment menu in the session's title bar, choose **Edit**, and add
a network secret (labelled *Network secrets* or *API credentials*, depending on
the app version). German labels from the app are shown in brackets.

| Field | Value |
|---|---|
| Name | `trading212` |
| Secret type (*Secret-Typ*) | **Basic** |
| Allowed websites (*Erlaubte Websites*) | `demo.trading212.com` for a Practice key, `live.trading212.com` for an Invest key |
| Path prefixes (*Pfad-Präfixe*) | **Leave empty** |
| Username (*Benutzername*) | your API Key |
| Password (*Passwort*) | your API Secret |

Save it with **Add** (*Hinzufügen*). The secret also allows network access to
the listed hosts, so no separate domain rule is needed.

Then add these ordinary environment variables:

```dotenv
ENVIRONMENT=demo
TRADING212_API_KEY=proxy
```

- `ENVIRONMENT` must match the account the key belongs to: `demo` or `live`.
- The scripts refuse to start without `TRADING212_API_KEY`. With a network
  secret, its value is only a placeholder (`proxy` is fine) because the proxy
  overwrites the header. Do not put your real key here. Leave
  `TRADING212_API_SECRET` unset.

If you have both an Invest and a Practice key, create one secret per account,
each allowing only its own host.

### Alternative: plain environment variables

This is simpler, but Claude can read the values during the session.

1. Under **Network access**, choose a level that lets you add allowed domains
   (*Limited* or *Custom*), add `live.trading212.com` and
   `demo.trading212.com`, and keep *Allow package managers* ticked.
2. Under **Environment variables**, add:

   ```dotenv
   TRADING212_API_KEY=your-api-key
   TRADING212_API_SECRET=your-api-secret
   ENVIRONMENT=live
   ```

Do not use this method and a network secret for the same host at the same
time.

## 3. Start a new session and test

Changes to environment variables apply to sessions started after you save
them, so open a new session in that environment. Then ask Claude, for example:

```text
Test the Trading 212 connection with a read-only request, then run
uv run --frozen python scripts/portfolio.py and summarize my holdings,
cash and weights. Do not place any trades.
```

A quick read-only check Claude can run from the container:

```sh
curl -sS -o /dev/null -w '%{http_code}\n' https://demo.trading212.com/api/v0/equity/account/cash
```

`200` means the connection works. Replace `demo` with `live` for an Invest
key.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `CONNECT tunnel failed, response 403` | The host is not allowed by the environment's network policy | Add a network secret for the host, or add the host to allowed domains |
| `403` with `allows the host but not path "/api/v0/..." (allowed: "/api/v1")` | A path prefix was typed into the secret | Clear *Path prefixes*. The client uses `/api/v0/`. Grey text in empty fields is only a placeholder |
| `401` on every host | Secret type set to *Bearer*, Key and Secret swapped, extra spaces copied, an old secret still overriding the header, or the key was revoked | Use type **Basic** with Key as username. Delete old secrets. Recreate the secret if unsure, because saved values cannot be viewed |
| `401` on `live` but `200` on `demo` (or the reverse) | The key belongs to the other account | Set `ENVIRONMENT` to the account that answers `200`, or create a key in the other account |
| Script exits asking for `TRADING212_API_KEY` | The variable is not set, or the session started before it was saved | Add the placeholder variable and start a new session |
| *Add* button stays disabled | A required field such as *Name* still shows only placeholder text | Type a real value |

## สรุปภาษาไทย

1. สร้าง API key ในแอป Trading 212 (Settings → API) ให้ตรงบัญชี: **Invest = live**,
   **Practice = demo** ให้สิทธิ์แค่อ่าน และก๊อป Key กับ Secret เก็บไว้ทันที
2. ในหน้า Edit ของ environment ให้เพิ่ม network secret แบบ **Basic** (ไม่ใช่ Bearer):
   - Name: `trading212`
   - Erlaubte Websites: โดเมนของบัญชีนั้น
   - **Pfad-Präfixe ปล่อยว่าง** (`/api/v1/` ที่เห็นเป็นแค่ตัวอย่างสีเทา)
   - Benutzername: API Key
   - Passwort: API Secret
3. ลบ secret เก่าที่ตั้งผิดออก ไม่อย่างนั้นจะได้ 401
4. เพิ่ม environment variable `ENVIRONMENT=demo` (หรือ `live`) และ
   `TRADING212_API_KEY=proxy` (เป็นค่าหลอก proxy จะใส่ key จริงให้เอง)
5. เปิด session ใหม่ แล้วสั่ง Claude ให้ทดสอบการเชื่อมต่อและรัน `scripts/portfolio.py`

ห้ามวาง Key หรือ Secret ลงในแชทเด็ดขาด
