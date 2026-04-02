# calendar-feed

A lightweight Flask microservice that serves iCal (`.ics`) feeds of legislative hearings from the LegTracker database. Subscribe any calendar app to these URLs and hearings will appear automatically.

---

## Endpoints

| Endpoint | Auth | Description |
|---|---|---|
| `GET /feed/chamber/<chamber_id>` | None | All hearings in a chamber |
| `GET /feed/committee/<committee_id>` | None | All hearings in a committee |
| `GET /feed/org/<token>` | Org token | Hearings for bills on an org's dashboard |
| `GET /feed/user/<token>` | User token | Hearings for bills on a user's personal dashboard |
| `GET /feed/working-group/<token>` | User token (WG member) | Hearings for bills on the working group dashboard |
| `GET /health` | None | Health check |

Chamber and committee feeds are public. Org/user/working-group feeds require a secret token in the URL.

---

## Token Setup (one-time)

### 1. Apply the DB migration

```bash
psql $DATABASE_URL -f migrations/001_add_feed_tokens.sql
```

### 2. Generate tokens for all existing users and orgs

Run from the monorepo root:

```bash
python -m db.scripts.generate_tokens
```

Raw tokens are printed to stdout **once and never stored**. The DB stores only the sha256 hash.

### 3. Regenerate a single token (admin only)

```bash
# For a user
python -m db.scripts.generate_tokens --regenerate user someone@example.com

# For an org
python -m db.scripts.generate_tokens --regenerate org 42

# For all
python -m db.scripts.generate_tokens --regenerate
```

---

## Local Development

Requires Docker. Create a `credentials.ini` file in the `db` module.

```bash
# From monorepo root
docker compose -f calendar-feed-service/compose.yaml up --build
```

Service is available at `http://localhost:5001`.

Test a public feed:
```bash
curl http://localhost:5001/feed/chamber/1
```

Test a token-authenticated feed:
```bash
curl http://localhost:5001/feed/org/<raw_token>
```

---

## [UNDER CONSTRUCTION] Project Structure

---

## Deployment (DO App Platform)

1. Point App Platform at the monorepo repo.
2. Set the **build context** to the repo root and **Dockerfile path** to `calendar-feed-service/Dockerfile`.
3. Add DB credentials as environment variables in the App Platform dashboard.
4. The `/health` endpoint is used as the health check path.

---

## Notes

- All feeds return hearings from today onwards. The mat view is truncated and refreshed daily by the existing cron job — no additional scheduling needed here.
- The `Cache-Control: max-age=3600` header tells calendar clients to re-poll hourly, which is a reasonable balance between freshness and load.
- Working group feed returns a `403` (not `401`) when the token is valid but the user is not a WG member, so clients can distinguish "bad token" from "not authorized".