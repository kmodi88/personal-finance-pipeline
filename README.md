# Personal Finance Analytics Pipeline

An end-to-end ETL pipeline that ingests bank CSV exports, auto-categorizes transactions, detects anomalies with machine learning, and visualizes spending through an interactive dashboard.

## Features

- **ETL Pipeline** — ingests bank CSV exports, normalizes columns across different bank formats
- **Auto-Categorization** — rule-based keyword matching assigns categories (Groceries, Rent, Subscriptions, etc.)
- **Anomaly Detection** — scikit-learn Isolation Forest flags unusual transactions
- **REST API** — FastAPI backend exposing summary stats, spending breakdowns, and anomaly data
- **Dashboard** — Chart.js visualization with spending by category (doughnut) and monthly cash flow (bar chart)
- **Tested** — 27 pytest tests covering ingestion, categorization, and ML model validation
- **Containerized** — Docker Compose for local development with PostgreSQL
- **CI/CD** — GitHub Actions runs tests and builds Docker image on every push
- **Deployed** — Render hosting with managed PostgreSQL

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API | FastAPI + Uvicorn |
| Database | PostgreSQL (SQLite for local dev) |
| ORM | SQLAlchemy 2.0 |
| ETL / Data | pandas |
| ML | scikit-learn (Isolation Forest) |
| Frontend | Chart.js |
| Testing | pytest + pytest-cov |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | Render |

## Getting Started

### Run locally (no Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server (uses SQLite by default)
python -m uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** and upload `data/sample_transactions.csv`.

### Run with Docker + PostgreSQL

```bash
cp .env.example .env
docker-compose up
```

Open **http://localhost:8000**.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload a bank CSV and run the pipeline |
| `GET` | `/api/summary` | Total income, expenses, net, anomaly count |
| `GET` | `/api/transactions` | Paginated transaction list with filters |
| `GET` | `/api/spending-by-category` | Expenses grouped by category |
| `GET` | `/api/monthly-cashflow` | Income vs. expenses by month |
| `GET` | `/api/anomalies` | All flagged anomalous transactions |

Interactive docs available at **http://127.0.0.1:8000/docs**.

## Running Tests

```bash
pytest tests/ -v --cov=app
```

27 tests covering:
- CSV ingestion and column normalization
- Auto-categorization keyword matching
- Isolation Forest training, scoring, and outlier detection

## Project Structure

```
├── app/
│   ├── etl/
│   │   ├── ingest.py        # CSV ingestion + column normalization
│   │   ├── categorize.py    # Keyword-based auto-categorization
│   │   ├── anomaly.py       # Isolation Forest train/detect
│   │   └── pipeline.py      # Orchestrates ETL steps → database
│   ├── api/
│   │   └── routes.py        # FastAPI route handlers
│   ├── db/
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   └── database.py      # Engine + session setup
│   └── static/
│       └── index.html       # Chart.js dashboard
├── tests/                   # pytest test suite
├── data/                    # Sample CSV + trained model
├── docker-compose.yml
├── Dockerfile
├── render.yaml              # Render deployment config
└── .github/workflows/ci.yml # GitHub Actions CI
```
