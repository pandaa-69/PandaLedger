
# PandaLedger

Portfolio analytics for retail investors. Tracks stocks, crypto, ETFs, and mutual funds with real-time valuation and historical performance reconstruction.

**Live:** [pandaledger.tech](https://www.pandaledger.tech) · **Frontend:** [PandaLedger-Frontend](https://github.com/pandaa-69/PandaLedger-Frontend)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=flat&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production-brightgreen?style=flat)

---

## Overview

PandaLedger is a modular monolith backend that reconstructs up to 30 years of portfolio history in under 90ms, handles multi-asset classes, and serves live prices without blocking the UI.

The interesting engineering is in how it handles performance constraints — no paid data APIs, free-tier hosting, and real concurrency problems that come with live market data.

---

## Engineering Decisions

### Vectorized History Engine
`analytics/services/backfill.py`

The first version looped through every day, queried holdings, and summed them up. It worked — until I tested it at scale. At 50 assets over 15 years (5,000+ days), that's O(N×D) and completely unusable.

I rewrote it by fetching all transactions once and broadcasting them onto a master timeline. `cumsum()` calculates holdings for every single day in one pass. `ffill()` handles weekends and holidays where markets are closed. The result went from unusably slow to a 3,000-point graph in under 90ms — roughly 100× faster. That was the moment I genuinely understood why vectorization matters.

### Non-Blocking Price Fetching & Async Backfills
`portfolio/views.py` · `analytics/signals.py`

Fetching live prices for 20 mutual funds sequentially takes ~10 seconds. No user waits that long. I switched to `ThreadPoolExecutor` to fire all requests simultaneously — total wait time becomes `max(request_time)` (~0.5s) instead of `sum(request_time)` (10s).

The trickier problem was history recalculation blocking the UI on every transaction. I wired a Django `post_save` signal to trigger the backfill in a background thread instead. The user gets an instant `200 OK` and the heavy work happens behind the scenes.

```mermaid
sequenceDiagram
    participant U as User (Frontend)
    participant A as Django API
    participant T as Background Thread
    participant D as Database

    U->>A: POST /add-transaction/
    A->>D: Save Transaction
    A->>T: Signal: Trigger Backfill
    A-->>U: 200 OK (Instant Response)

    T->>D: Fetch History (15 Years)
    T->>T: Vectorized Calc (Pandas)
    T->>D: Update Analytics Tables
```

### Hybrid Data Routing
`portfolio/views.py`

Yahoo Finance is great for stocks and crypto but unreliable for Indian mutual funds. MFAPI is the opposite. Rather than picking one, I built a router that detects asset type and hits the right source automatically.

Prices are served from cache immediately while a background worker refreshes stale data. If an external API goes down, the dashboard serves the last known good price from the DB instead of crashing — I didn't want a third-party outage to take down the whole dashboard.

---

## Architecture

Modular monolith over microservices — clear module boundaries without the network overhead or deployment complexity.

```mermaid
graph TD
    subgraph "Modular Monolith"
        C[Core] -->|Auth & User| P[Portfolio]
        P -->|Transaction Signals| A[Analytics]
        L[Ledger] -->|Budget Data| C
    end

    subgraph "External"
        YF[Yahoo Finance API]
        MF[MFAPI.in]
        DB[(PostgreSQL)]
    end

    P -.->|ThreadPool Fetch| YF
    P -.->|Parallel Fetch| MF
    A -->|Vectorized Write| DB
```

| Module | Responsibility |
|--------|---------------|
| Core | Auth, custom user model, global config |
| Portfolio | Asset management, holdings, live pricing |
| Ledger | Expense tracking and categorization |
| Analytics | Vectorized history, performance metrics |

---

## Tradeoffs

Every decision here was conscious. I'd rather document the limitations than pretend they don't exist.

**External data dependencies** — Yahoo Finance and MFAPI are free but can go down. The alternative is a $500/mo Bloomberg API, which isn't happening. I leaned hard into caching and graceful degradation so a third-party outage doesn't mean a broken dashboard.

**LocMemCache locking** — The thundering herd lock lives in process memory. It works perfectly on a single worker but would silently break across multiple pods in a distributed setup. Switching to RedisCache in `settings.py` solves it when horizontal scaling actually becomes necessary.

**Threading over Celery** — I chose `ThreadPoolExecutor` over a full Celery + broker setup. If the server restarts mid-backfill, that job is lost. But backfills finish in under a second and are idempotent, so the operational overhead of managing a message queue wasn't worth it for v1.

**10-second update interval** — Not real-time, intentionally. Polling every second would get the IP banned by Yahoo Finance fast. The thundering herd lock caps outgoing requests at 360/hour regardless of how many users are active.

---

## Roadmap

- [ ] Weekly/monthly email reports via Django-Anymail
- [ ] Migrate background jobs to Celery + Redis for reliability
- [ ] Sankey diagrams for income/expense flows
- [ ] Monte Carlo simulations for portfolio projection
- [ ] LLM-powered rebalancing suggestions (concentration risk, volatility exposure)

---

## Tech Stack

- **Backend:** Python 3.10+, Django 5.0, Django REST Framework
- **Data:** Pandas, NumPy
- **Database:** PostgreSQL (prod), SQLite (dev)
- **Frontend:** React + Vite + TailwindCSS
- **Concurrency:** ThreadPoolExecutor, Django Signals

---

## Setup

**Prerequisites:** Python 3.10+, PostgreSQL

```bash
git clone https://github.com/pandaa-69/PandaLedger.git
cd PandaLedger
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost:5432/pandaledger

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@pandaledger.tech
DJANGO_SUPERUSER_PASSWORD=secure_password_123
```

```bash
python manage.py migrate
python manage.py runserver
```

A superuser is created automatically on first run from the `.env` values.
*Engineered with ❤️ (and lots of curiosity) by Durgesh (Panda).*

