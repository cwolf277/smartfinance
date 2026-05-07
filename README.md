# SmartFinance

Full-stack personal finance dashboard with Plaid integration, transaction analytics, and machine-learning overspending prediction.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18, React Router, Chart.js, react-plaid-link |
| Backend | Flask, Flask-CORS, Plaid Python SDK, Gunicorn |
| Data | SQLAlchemy + SQLite (default), pandas |
| ML | scikit-learn (logistic regression), joblib |
| Infra | Docker, docker-compose, GitHub Actions CI |

## Architecture

```
React (3000) ──HTTP──> Flask API (5000) ──> Plaid API
                            │
                            ├──> SQLAlchemy ──> SQLite/Postgres
                            │
                            └──> ETL pipeline ──> ML (scikit-learn)
                                                    │
                                                    └──> overspend prediction
```

## Features

- Plaid Link flow (sandbox) — link account, exchange public token, fetch transactions
- ETL pipeline — extract from CSV/Plaid, normalize, enrich with calendar features, aggregate monthly
- ML model — logistic regression predicting monthly overspending risk
- Privacy — account ID masking and address scrubbing on outbound responses
- Dashboard — totals, category breakdown, transactions table
- Predictions UI — train + predict from the browser
- Docker — multi-container deployment behind nginx
- CI — pytest + jest + lint + docker build on every push

## Run it in the cloud

### GitHub Codespaces (zero-setup, browser only)

[![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/cwolf277/smartfinance)

Click the badge → `Create codespace on main`. The devcontainer auto-installs deps and starts both servers. The frontend opens in the Ports tab once it's ready (~3 min first time).

To pre-fill Plaid keys, set them as Codespaces secrets:
**Settings → Codespaces → New repository secret** → add `PLAID_CLIENT_ID` and `PLAID_SECRET`.

### Render (one-click public deployment)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/cwolf277/smartfinance)

The repo includes `render.yaml` (Blueprint) provisioning the Flask backend and React frontend as separate services. Backend uses a 1GB persistent disk for the SQLite DB. Add your Plaid keys as environment variables in the Render dashboard after the first deploy.

## Run it locally

### 1. Clone

```bash
git clone https://github.com/cwolf277/smartfinance.git
cd smartfinance
```

### 2. Environment

```bash
cp .env.example .env
# Edit .env and add your Plaid sandbox keys (optional — ETL works without them)
```

### 3. Backend

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m backend.app
# API on http://localhost:5000
```

### 4. Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm start
# UI on http://localhost:3000
```

### 5. Load sample data

In the UI, go to **Transactions → Run ETL on sample data**, or:

```bash
curl -X POST http://localhost:5000/etl/run -H "Content-Type: application/json" \
     -d '{"source": "data/sample_transactions.csv"}'
```

### 6. Train + predict

```bash
curl -X POST http://localhost:5000/ml/train
curl -X POST http://localhost:5000/ml/predict -H "Content-Type: application/json" \
     -d '{"monthly_spend": 5000, "txn_count": 50, "avg_txn": 100, "max_txn": 1500, "weekend_ratio": 0.4, "category_diversity": 8}'
```

## Docker

```bash
docker-compose up --build
# Frontend: http://localhost:3000   Backend: http://localhost:5000
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| POST | `/create_link_token` | Plaid Link token |
| POST | `/exchange_public_token` | Exchange Plaid public token |
| GET | `/get_transactions` | Pull recent Plaid transactions |
| GET | `/transactions` | Stored transactions (`?limit=N`) |
| POST | `/etl/run` | Run ETL pipeline (`{source: path}`) |
| POST | `/ml/train` | Train overspend model |
| POST | `/ml/predict` | Predict overspend probability |

## Tests

```bash
pytest                     # Python tests
cd frontend && npm test    # React tests
```

## Project layout

```
smartfinance/
├── backend/                 # Flask app + Plaid wiring
│   ├── app.py
│   └── plaid_config.py
├── smartfinance/            # Reusable Python package
│   ├── config.py
│   ├── db.py                # SQLAlchemy models + helpers
│   ├── etl/                 # extract / transform / load / pipeline
│   ├── ml/                  # features / model / predict
│   └── utils/               # masking, archiving
├── frontend/                # React app
│   ├── src/components/      # Dashboard, Transactions, LinkAccount, Predictions
│   └── src/services/api.js  # axios client
├── tests/                   # pytest suite
├── data/                    # sample CSV + sqlite (gitignored)
├── .github/workflows/ci.yml # CI pipeline
├── Dockerfile               # backend image
├── frontend/Dockerfile      # frontend image (nginx)
└── docker-compose.yml
```

## License

MIT — see [LICENSE](LICENSE).
