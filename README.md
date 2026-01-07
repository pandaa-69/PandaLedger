
# 🐼 PandaLedger
> **Institutional-Grade Analytics for Personal Finance.**
> *Because "tracking expenses" is for amateurs. I track Net Worth.*

![Status](https://img.shields.io/badge/Status-Production-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Vectorized-150458?style=for-the-badge&logo=pandas&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React_Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black)

---
## 🖥️ Frontend
This is the Backend Engine (API).
Looking for the User Interface? Check out the **[Frontend Repository](https://github.com/pandaa-69/PandaLedger-Frontend)**.
## 📖 Overview

**PandaLedger** is not your average expense tracker. It is a **Modular Monolith** engineered to bring hedge-fund level portfolio analysis to retail investors.

While it looks like a simple finance app on the surface, the backend is a high-performance engine capable of reconstructing **15+ years of financial history in milliseconds**, handling complex corporate actions, and managing multi-asset portfolios (Stocks, Crypto, ETFs, Mutual Funds) with real-time valuation.

---

## ⚡ Engineering Highlights: The "Wow" Factor

I didn't just write loops; I engineered solutions. Here is the hidden complexity powering PandaLedger:

### 1. 🏎️ Vectorized "Time-Machine" Engine
*Found in: `analytics/services/backfill.py`*

**The Challenge:** How do you calculate the daily net worth of a user for the last 15 years (5,000+ days) across 50 different assets without killing the database?
**The Naive Approach:** Loop through every day, query the DB for holdings, sum them up. (Complexity: O(N*D) - Slow & Heavy).
**My Solution:**
I utilize **Pandas Vectorization** to perform this operation in **O(1)** (effectively).
- **Broadcasting**: I fetch all transactions once and broadcast them onto a master timeline.
- **`cumsum()`**: I use cumulative sums to instantly calculate holdings for every single day in one CPU cycle.
- **`ffill()`**: Missing price data (weekends/holidays) is forward-filled instantly.
- **Result**: Generates a 3,000-point graph in **<90ms**.

### 2. 🚀 Non-Blocking Concurrency & Event-Driven Architecture
*Found in: `portfolio/views.py` & `analytics/signals.py`*

**The Challenge:** Fetching live prices for 20 Mutual Funds takes ~10 seconds. Users won't wait that long. Also, recalculating history on every transaction blocks the UI.
**My Solution:**
- **Parallel Execution**: I use `ThreadPoolExecutor` to fire 20 API requests *simultaneously*. Total wait time = `max(request_time)` (~0.5s) instead of `sum(request_time)` (10s).
- **Async Signals**: When a transaction is saved, a **Django Signal** (`post_save`) triggers a background thread to recalculate history asynchronously. The user gets an instant "Success" response.

```mermaid
sequenceDiagram
    participant U as User (Frontend)
    participant A as Django API
    participant T as Background Thread
    participant D as Database

    U->>A: POST /add-transaction/
    A->>D: Save Transaction
    A->>T: Signal: Trigger Backfill ⚡
    A-->>U: 200 OK (Instant Response)
    Note over U: UI Updates Immediately
    
    Note right of T: 🔄 The "Ghost" Work
    T->>D: Fetch History (15 Years)
    T->>T: Vectorized Calc (Pandas)
    T->>D: Update Analytics Tables

```

### 3. 🛡️ Hybrid Data Layer & Smart Routing

*Found in: `portfolio/views.py`*

**The Challenge:** Yahoo Finance is great for Stocks but terrible for Indian Mutual Funds. MFAPI is great for MFs but doesn't have US Stocks.
**My Solution:**

* **Smart Routing**: The backend automatically detects the asset type. Stock/Crypto? Batch request to Yahoo. Mutual Fund? Route to MFAPI.
* **Stale-While-Revalidate**: I serve cached prices immediately (from Redis/DB) to ensure the UI is snappy, while a background worker refreshes the data if it's stale.

---

## 🏗️ Architecture: Modular Monolith

I rejected the hype of Microservices for the pragmatic power of a **Modular Monolith**. This gives code isolation (clear boundaries) with deployment simplicity (zero network latency).

```mermaid
graph TD
    subgraph "Modular Monolith"
        C[🔐 Core App] -->|Auth & User| P[📈 Portfolio App]
        P -->|Transaction Signals| A[📊 Analytics App]
        L[📒 Ledger App] -->|Budget Data| C
    end
    
    subgraph "External World"
        YF[Yahoo Finance API]
        MF[MFAPI.in]
        DB[(PostgreSQL)]
    end

    P -.->|ThreadPool Fetch| YF
    P -.->|Parallel Fetch| MF
    A -->|Vectorized Write| DB

```

| Module | Responsibility |
| --- | --- |
| **🔐 Core** | Authentication, Custom User Model, Global Config. |
| **📈 Portfolio** | The "Heavy Lifter". Manages Assets, Holdings, and Live Pricing. |
| **📒 Ledger** | High-volume expense tracking and categorization. |
| **📊 Analytics** | The Intelligence Layer. Consumes data to build vectorized insights. |

---

## ⚖️ Design Tradeoffs & Limitations

Every architecture decision carries a cost. Here are the conscious tradeoffs made in PandaLedger:

### 1. External Data Dependencies
*   **Limitation:** The system relies on **Yahoo Finance** and **MFAPI.in** for live data.
*   **Tradeoff:** Instead of paying $500/mo for a Bloomberg Terminal API, we accept that data fetching might fail if these services go down.
*   **Mitigation:** The system relies heavily on **Caching** and **Graceful Degradation**. If an external API fails, the dashboard serves the last known good price from the DB rather than crashing.

### 2. Single-Process Architecture (LocMemCache)
*   **Limitation:** The current locking mechanism (`market_update_lock`) uses `LocMemCache` (RAM). This means it works perfectly on a single worker instance but would fail in a distributed cluster (e.g., Kubernetes with 50 pods).
*   **Tradeoff:** Keeps hosting simple (no Redis required) for the free tier.
*   **Future Path:** Switch `CACHES` to `RedisCache` in `settings.py` for horizontal scaling.

### 3. Concurrency Model (Threading vs. Celery)
*   **Limitation:** Background jobs (price updates, history backfills) use Python's `threading` and `ThreadPoolExecutor`.
*   **Tradeoff:** Avoids the operational overhead of managing a separate message queue (RabbitMQ/Redis) and worker process (Celery) for a personal finance app.
*   **Risk:** If the server restarts *during* a backfill, that job is lost.
*   **Reasoning:** Since backfills are fast (<1s) and idempotent, the complexity of Celery wasn't justified for v1.

### 4. Rate-Limited Updates (10s Interval)
*   **Limitation:** The live dashboard updates every 10 seconds, not sub-second real-time.
*   **Tradeoff:** Prevents our IP from being banned by Yahoo Finance's abuse detection systems.
*   **Mechanism:** A custom "Thundering Herd" lock ensures we only send **360 requests/hour** to Yahoo, regardless of how many users are online.

---

## 🛠️ Tech Stack

* **Core**: Python 3.10+, Django 5.0
* **Data Science**: Pandas, NumPy (Vectorization)
* **API**: Django Rest Framework (DRF)
* **Frontend**: React + Vite + TailwindCSS
* **Database**: PostgreSQL (Production), SQLite (Dev)
* **Concurrency**: `ThreadPoolExecutor`, Django Signals

---

## ⚡ Quick Start (Secure Setup)

### Prerequisites

* Python 3.10+
* PostgreSQL

### Installation

1. **Clone & Install**
```bash
git clone [https://github.com/pandaa-69/PandaLedger.git](https://github.com/pandaa-69/PandaLedger.git)
cd PandaLedger
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

```


2. **Environment Setup**
Create a `.env` file. Note the **Auto-Superuser** configuration:
```env
DEBUG=True
SECRET_KEY=super-secret-key
DATABASE_URL=postgres://user:pass@localhost:5432/pandaledger

# 🔐 Secure Superuser Creation (Auto-runs on startup)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@pandaledger.tech
DJANGO_SUPERUSER_PASSWORD=secure_password_123

```


3. **Run & Fly**
```bash
python manage.py migrate
python manage.py runserver

```


*The system will automatically create your admin account on the first run based on the .env variables.*

---

*Engineered with ❤️ (and a lot of coffee) by Durgesh (Panda).*

