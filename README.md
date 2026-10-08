# The Daily Waddle 🐧

A public, read-only penguin REST API (FastAPI + async SQLAlchemy + SQLite) and a Discord bot that broadcasts the Penguin of the Day.

## Structure
```
daily-waddle/
├── app/
│   ├── main.py          # FastAPI app, CORS, startup (create tables + seed)
│   ├── config.py        # typed settings from .env
│   ├── database.py      # async engine / session dependency
│   ├── models.py        # Penguin, PenguinFact (DB schema)
│   ├── schemas.py       # Pydantic response models
│   ├── seed.py          # mock data (Emperor, Adélie, Little Blue)
│   └── routers/penguins.py
├── bot/discord_bot.py   # !waddle command + scheduled daily post
├── .env.example
└── requirements.txt
```

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

uvicorn app.main:app --reload        # API on http://127.0.0.1:8000  (docs at /docs)
```
Try it:
```bash
curl localhost:8000/api/v1/penguins
curl localhost:8000/api/v1/penguins/emperor
curl localhost:8000/api/v1/penguins/random
curl localhost:8000/api/v1/penguins/daily
curl "localhost:8000/api/v1/penguins/daily?on=2026-12-25"   # deterministic per date
```

## Run the bot
1. Discord Developer Portal -> New Application -> Bot -> copy token into `DISCORD_TOKEN`.
2. Enable **Message Content Intent** (Bot -> Privileged Gateway Intents).
3. Invite with scopes `bot`, permissions: View Channel, Send Messages, Embed Links.
4. Set `DISCORD_CHANNEL_ID` for the scheduled post, then, with the API running:
```bash
python -m bot.discord_bot
```
Commands: `!waddle` (daily), `!waddle random`.

## Design notes
- `/daily` uses `date.toordinal() % species_count`: no cron, no stored state, same answer for everyone.
- `/random` and `/daily` are registered before `/{species_id}` so they aren't swallowed by the path param.
- Security: read-only GET API, CORS limited to GET without credentials, validated path params, ORM-parameterised queries, bot token only via env, bot has timeouts, cooldown and error handling.
- Image URLs are placeholders. Swap in images you are licensed to use.

## Next steps
Add the remaining species to `app/seed.py`; add rate limiting (e.g. `slowapi` or your reverse proxy); Alembic migrations; pytest with `httpx.ASGITransport`; Dockerfile; deploy API (Fly.io/Render) and run the bot as a second process.
