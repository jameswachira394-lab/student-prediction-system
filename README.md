# Student Results Prediction System

A web app that predicts a student's exam result from inputs such as study hours, attendance and previous scores, and presents it as supportive guidance, not a verdict.

Built by a team of three as a learning project: DevOps, AI/ML and Frontend.

> **Status:** in development. This README is a starting point and will be updated when the project is complete.

## How it works

The system is a small set of microservices behind one gateway, all started with Docker Compose.

```text
Browser -> Gateway -> Frontend
                  \-> Results service -> Prediction service (ML model)
```

| Service | What it does |
| --- | --- |
| `gateway` | Single public entry point. Routes `/` to the frontend and `/api` to the results service |
| `frontend` | The web interface: input form, result card, charts |
| `results-service` | Public API. Validates input, calls the prediction service, returns the result |
| `prediction-service` | Loads the trained model and returns predictions. Not exposed publicly |

Full design, API contracts and team processes are in [DOCUMENTATION.md](DOCUMENTATION.md). A structured breakdown of what was built across DevOps/Backend, Frontend, and ML is in [OVERVIEW.md](OVERVIEW.md). Detailed architectural specifications can also be found in [docs/backend.md](docs/backend.md) and [docs/frontendesign.md](docs/frontendesign.md). Machine learning pipeline details are in [ml/README.md](ml/README.md).

## Quick start

**Requirements:** [Docker](https://docs.docker.com/get-docker/) with Docker Compose, and Git.

```bash
# 1. Clone the repository
git clone https://github.com/<owner>/<repo>.git
cd <repo>

# 2. Create your local settings
cp .env.example .env

# 3. Start everything
docker compose up --build
```

Then open <http://localhost:8080>.

Stop with `Ctrl+C`, and remove the containers with `docker compose down`.

> Until the real model is ready, set `USE_MOCK_MODEL=true` in `.env`. The prediction service then returns fake predictions with the same response shape as the real one.

## Try the API

```bash
curl -X POST http://localhost:8080/api/predictions \
  -H "Content-Type: application/json" \
  -d '{"study_hours": 12, "attendance": 85, "previous_score": 64}'
```

Example response (values are illustrative):

```json
{ "predicted_score": 72.4, "grade": "B", "risk": "low", "model_version": "v1" }
```

Check that the service is up with `curl http://localhost:8080/api/health`.

## Project structure

```text
.
├── ml/                  # dataset, training scripts, saved models, ML unit tests
├── services/
│   ├── prediction-service/
│   └── results-service/
├── frontend/            # web interface
├── gateway/             # reverse proxy configuration
├── docs/                # backend and frontend design specifications
├── .github/             # CI workflow, Dependabot, CODEOWNERS, PR template
├── docker-compose.yml
├── .env.example
├── DOCUMENTATION.md     # design, ownership and processes
└── README.md
```

## Team

| Role | Owns | Member |
| --- | --- | --- |
| DevOps | Repository, containers, CI/CD, deployment, gateway, results service | _name_ |
| AI/ML | Dataset, model training, `predict()`, model versioning | _name_ |
| Frontend | User interface and API integration | _name_ |

## Contributing

1. Create a branch from `main`, named like `feature/<topic>` or `fix/<topic>`.
2. Make small, focused commits with a prefix such as `feat:`, `fix:` or `docs:`.
3. Open a pull request, fill in the template, and request a review.
4. Merge once it is approved and the **CI passed** check is green.

Never commit secrets, `.env` files, large datasets or large model files. See [DOCUMENTATION.md](DOCUMENTATION.md) for the full workflow and definition of done.

## Responsible use

Predictions are estimates based on a limited dataset, not guarantees. The model does not use sensitive attributes such as gender or ethnicity. Results should be read as guidance for where a student might want support.

## Live demo

_To be added after deployment._
