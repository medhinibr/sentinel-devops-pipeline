# Sentinel: Cloud-Native DevSecOps Data Pipeline

[![DevOps Pipeline](https://github.com/medhinibr/sentinel-devops-pipeline/actions/workflows/devops-pipeline.yml/badge.svg)](https://github.com/medhinibr/sentinel-devops-pipeline/actions/workflows/devops-pipeline.yml)

Sentinel is a containerized Python data pipeline that fetches live cryptocurrency prices from a public REST API, stores them in a serverless PostgreSQL database, and visualizes them on a Grafana Cloud dashboard. Every push to `main` triggers a GitHub Actions workflow that builds the Docker image, scans it for vulnerabilities with Trivy, and runs the container against the production database as a smoke test.

The goal of the project is to practice the full delivery lifecycle in a small, understandable system: containerization, CI/CD, security scanning, secrets handling, a managed cloud database and observability.

---

## Architecture

```mermaid
flowchart LR
    A[Push to main] --> B[GitHub Actions]
    B --> C[Docker Buildx<br/>multi-stage build]
    C --> D[Trivy scan<br/>CRITICAL and HIGH CVEs]
    D --> E[Smoke test<br/>30 second container run]
    E --> F[Python ingestion<br/>app/main.py]
    F -->|GET price| G[CoinGecko API]
    F -->|INSERT| H[(Neon PostgreSQL)]
    H --> I[Grafana Cloud<br/>dashboard]
    S[GitHub Encrypted Secrets] -.->|DATABASE_URL| E
```

| Layer | Implementation |
|---|---|
| Ingestion | Python service (`app/main.py`) using `requests` and `psycopg2` |
| Storage | Neon serverless PostgreSQL, table `crypto_prices` |
| Automation | GitHub Actions (`.github/workflows/devops-pipeline.yml`) |
| Security | Trivy image scan, secrets injected at runtime |
| Observability | Grafana Cloud queries the table and charts price history and ingestion frequency |

---

## How It Works

1. `fetch_crypto_price()` calls the CoinGecko simple price endpoint for Bitcoin in USD and parses the response.
2. `save_to_db()` connects with the `DATABASE_URL` environment variable and inserts one row into `crypto_prices`.
3. Rows are append-only, each stamped with `fetched_at`, so the table works as a time series.
4. Grafana reads the table. A flat line or a gap on the dashboard signals that ingestion or the pipeline stopped working.

Errors from the API call and the database are caught and logged to standard output, so a transient failure does not crash the container with a traceback.

### Database schema

| Column | Description |
|---|---|
| `id` | Auto-incrementing primary key (`SERIAL`) |
| `coin_name` | Asset identifier, for example `bitcoin` |
| `price_usd` | Price in US dollars at fetch time |
| `fetched_at` | Insert timestamp, defaults to `CURRENT_TIMESTAMP` |

The schema is created by `sql/init.sql`.

---

## CI/CD and Security

The workflow in `.github/workflows/devops-pipeline.yml` runs on every push to `main`:

| Step | What it does |
|---|---|
| Checkout | Clones the repository onto an `ubuntu-latest` runner |
| Set up Buildx | Initializes the Docker Buildx builder |
| Build | Builds the `sentinel-app` image from `docker/Dockerfile` |
| Trivy scan | Scans the image for CRITICAL and HIGH vulnerabilities and prints a report table |
| Smoke test | Runs the container for up to 30 seconds with `DATABASE_URL` injected from GitHub Secrets to verify database connectivity |

**Secrets:** the database connection string is stored as a GitHub Encrypted Secret and passed to the container at runtime. It is not committed to the repository or baked into image layers.

---

## Containerization

`docker/Dockerfile` uses a two-stage build on `python:3.9-slim`:

- **Builder stage:** installs Python dependencies into the user directory with `pip install --user --no-cache-dir`.
- **Runtime stage:** starts from a fresh slim image and copies only the installed packages and `main.py`, leaving build caches and intermediate files behind.

`docker/docker-compose.yml` provides a local PostgreSQL 15 container (`postgres:15-alpine`) that loads `sql/init.sql` on first start, plus a service for the ingestion app. Both services use `restart: always`.

---

## Getting Started

### Prerequisites

- Python 3.9 or newer
- Docker and Docker Compose (for the local database)
- A PostgreSQL database: a local container or a Neon project

### Run with a local database

```bash
git clone https://github.com/medhinibr/sentinel-devops-pipeline.git
cd sentinel-devops-pipeline

# Start PostgreSQL and create the schema
cd docker
docker compose up -d db
cd ..

# Install dependencies and run the ingestion script
pip install -r app/requirements.txt
export DATABASE_URL='postgresql://admin:admin123@localhost:5432/sentinel_db'
python app/main.py
```

The credentials above are throwaway defaults for the local development container only.

### Run against Neon

```bash
export DATABASE_URL='postgresql://<user>:<password>@<host>/<database>?sslmode=require'
python app/main.py
```

### Enable the pipeline on your own fork

Add a repository secret named `DATABASE_URL` under Settings, Secrets and variables, Actions. The workflow runs on the next push to `main`.

---

## Repository Structure

```
.
├── .github/workflows/   CI/CD workflow (devops-pipeline.yml)
├── app/                 Ingestion script and requirements
├── docker/              Dockerfile and docker-compose.yml
└── sql/                 Database schema (init.sql)
```

---

## Design Notes and Limitations

- The pipeline currently tracks a single asset (Bitcoin in USD) and writes one record per run.
- Ingestion runs when the container runs, which includes the smoke test on each push. There is no separate scheduler yet.
- The Trivy step is report-only (`exit-code: 0`), so findings are visible in the logs but do not fail the build.

---

## Project Background

Sentinel was first developed on a local WSL and Docker environment. When that environment became unusable, I moved the build, scan and execution steps to GitHub Actions and managed cloud services (Neon and Grafana Cloud), which kept delivery going and made the pipeline reproducible from any machine.
