# Student Results Prediction System: Project Documentation

This document is the single reference for how the team builds, runs, tests and ships the system. It defines who owns what, how the services fit together, and the process and design rules everyone follows.

> Status: living document. Anything marked **(proposed)** should be confirmed by the team in week one. Change it by pull request like any other file.

## Table of contents

1. [Project overview](#1-project-overview)
2. [Team and ownership](#2-team-and-ownership)
3. [Architecture](#3-architecture)
4. [Repository structure](#4-repository-structure)
5. [API contracts](#5-api-contracts)
6. [Processes](#6-processes)
7. [Design standards](#7-design-standards)
8. [Definition of done](#8-definition-of-done)
9. [Responsible use of predictions](#9-responsible-use-of-predictions)
10. [Phases and roadmap](#10-phases-and-roadmap)
11. [Learning resources](#11-learning-resources)

---

## 1. Project overview

The system predicts a student's exam result from inputs such as study hours, attendance and previous scores, and presents it as supportive guidance, not a verdict.

It is built as a small set of microservices behind a single gateway. Each team member owns one layer, and each service can be built, tested, released and rolled back on its own.

**Goals for version 1**

- A live demo reachable by a public link
- The whole system starts locally with one command: `docker compose up`
- Every change is linted, tested and built automatically before it reaches `main`
- Each member can explain and demo their own part

**Out of scope for version 1 (proposed):** user accounts and login, real school data, mobile app, Kubernetes.

---

## 2. Team and ownership

### 2.1 Roles

| Role | Focus | Starting level |
| --- | --- | --- |
| DevOps | Repository, containers, CI/CD, deployment, gateway, configuration, monitoring, results service | Extensive Cloud DevOps experience |
| AI/ML | Dataset, model training and evaluation, `predict()`, model versioning | First ML project, learning |
| Frontend | User interface, API integration, charts, user-facing wording | First frontend project, learning |

The DevOps lead also acts as technical guide: sets up the workflow, reviews pull requests with explanations, and helps teammates read CI failures.

### 2.2 Ownership by area

"Owner" is accountable for the area and is the default reviewer. "Support" helps when asked.

| Area | Owner | Support | Notes |
| --- | --- | --- | --- |
| `ml/` (data, notebooks, training, model files) | AI/ML | DevOps | DevOps helps with environments and packaging, not model choices |
| `services/prediction-service/` model loading and `predict()` | AI/ML | DevOps | |
| `services/prediction-service/` Dockerfile and API wrapper | DevOps | AI/ML | (proposed) AI/ML may take the wrapper once comfortable |
| `services/results-service/` | DevOps | AI/ML | Validates input, calls the prediction service, stores history in phase 2 |
| `frontend/` | Frontend | DevOps | DevOps owns its Dockerfile and Nginx config |
| `gateway/` | DevOps | | Routing, HTTPS, request IDs |
| `.github/workflows/` | DevOps | | CI/CD pipelines |
| `docker-compose.yml`, `.env.example` | DevOps | All | Anyone may propose changes by pull request |
| API contracts (section 5) | DevOps | AI/ML, Frontend | Changes need agreement from all three |
| `DOCUMENTATION.md`, `README.md` | DevOps | All | Everyone updates the parts they own |

### 2.3 Hand-offs

| From | To | What is handed over |
| --- | --- | --- |
| AI/ML | DevOps | Model file, model metadata file, pinned `requirements.txt`, `predict()` signature, one sample request and response |
| AI/ML | Frontend | Input fields with units and ranges, meaning of each output field, feature importance values if available |
| Frontend | DevOps | Build command, output folder, name of the API base URL setting |
| DevOps | AI/ML and Frontend | Mock API early, working `docker compose up`, CI feedback, deployed URL |

### 2.4 Code owners

Add a `.github/CODEOWNERS` file so the right person is requested for review automatically (replace the handles):

```text
/ml/                                 @ai-ml-handle
/services/prediction-service/app/    @ai-ml-handle
/services/prediction-service/        @devops-handle
/services/results-service/           @devops-handle
/frontend/src/                       @frontend-handle
/frontend/                           @devops-handle
/gateway/                            @devops-handle
/.github/                            @devops-handle
```

The last matching pattern wins, so keep the more specific paths after the general ones if you reorder.

---

## 3. Architecture

### 3.1 Overview

```mermaid
flowchart LR
    U[Browser: student or teacher] --> G[Gateway<br/>Nginx or Traefik]
    G -->|/| F[Frontend service<br/>static files]
    G -->|/api| R[Results service<br/>FastAPI]
    R -->|POST /predict| P[Prediction service<br/>FastAPI + model]
    R -.->|phase 2| D[(Postgres)]
```

### 3.2 Services

| Service | Responsibility | Technology (proposed) | Internal port | Public |
| --- | --- | --- | --- | --- |
| `gateway` | Single entry point. Routes `/` to frontend and `/api` to results service. Adds request ID, handles HTTPS | Nginx or Traefik | 80 / 443 | Yes |
| `frontend` | Serves the static web app | Nginx serving HTML/CSS/JS (or a React build) | 80 | Via gateway only |
| `results-service` | Public API. Validates input, calls the prediction service, returns the result. Phase 2: stores history, serves summary data | FastAPI, Uvicorn, SQLAlchemy | 8000 | Via gateway only |
| `prediction-service` | Loads the model and returns predictions. Stateless | FastAPI, scikit-learn, joblib | 8001 | **No** |
| `postgres` (phase 2) | Stores prediction history | PostgreSQL | 5432 | **No** |

### 3.3 Architecture rules

1. Only the gateway is reachable from outside. All other services live on an internal Docker network.
2. The prediction service is never called by the frontend. Only the results service calls it.
3. Only the results service talks to the database.
4. Services communicate over HTTP using the contracts in section 5. No service reads another service's files or database.
5. The frontend calls a relative path (`/api/...`), so browser and API share one origin and CORS is not needed in deployment. CORS is configured only for local development when the frontend runs on a different port.
6. Each service has its own Dockerfile, dependencies, tests, health endpoint and CI job.
7. A model change must not require a change to the frontend or database. Only the prediction service image is rebuilt.

### 3.4 Request flow

1. The browser sends `POST /api/predictions` to the gateway.
2. The gateway adds an `X-Request-ID` header and forwards to the results service.
3. The results service validates the input, then calls `POST /predict` on the prediction service.
4. The prediction service runs the model and returns the prediction.
5. The results service returns the result (and, in phase 2, saves it) and the frontend displays it.

### 3.5 Local networking and ports

| What | URL on your machine |
| --- | --- |
| Whole app through the gateway | `http://localhost:8080` |
| Results service docs (development only) | `http://localhost:8000/docs` |
| Prediction service docs (development only) | `http://localhost:8001/docs` |

Direct ports to the services are exposed only by `docker-compose.override.yml` for local development, never in the deployed setup.

### 3.6 Compose skeleton

A starting point for `docker-compose.yml` (DevOps refines it):

```yaml
services:
  gateway:
    build: ./gateway
    ports: ["8080:80"]
    depends_on: [frontend, results-service]

  frontend:
    build: ./frontend

  results-service:
    build: ./services/results-service
    environment:
      PREDICTION_SERVICE_URL: http://prediction-service:8001
      LOG_LEVEL: info
    depends_on:
      prediction-service:
        condition: service_healthy

  prediction-service:
    build: ./services/prediction-service
    environment:
      MODEL_PATH: /app/models/model_v1.joblib
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')"]
      interval: 10s
      timeout: 3s
      retries: 5
```

---

## 4. Repository structure

```text
student-results-prediction/
├── ml/
│   ├── data/                    # dataset notes only; large data is not committed
│   ├── notebooks/               # exploration and experiments
│   ├── train.py                 # rebuilds the model from the data
│   ├── models/                  # model_v1.joblib and model_v1.json
│   └── requirements.txt
├── services/
│   ├── prediction-service/
│   │   ├── app/                 # main.py, predict.py
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── results-service/
│       ├── app/                 # main.py, routes, schemas, clients
│       ├── tests/
│       ├── requirements.txt
│       └── Dockerfile
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
├── gateway/
│   ├── nginx.conf               # or traefik config
│   └── Dockerfile
├── docs/                        # detailed backend and frontend design specs
├── .github/
│   ├── workflows/               # ci.yml, deploy.yml
│   ├── CODEOWNERS
│   └── pull_request_template.md
├── docker-compose.yml
├── docker-compose.override.yml  # local development ports and hot reload
├── .env.example                 # names of required settings, no secrets
├── .gitignore
├── DOCUMENTATION.md
└── README.md                    # how to run, short version
```

---

## 5. API contracts

These contracts are the agreement between owners. Change them only by pull request approved by all three members, and update this section in the same pull request.

### 5.1 Conventions for every service

- JSON request and response bodies, `snake_case` field names.
- Every service exposes `GET /health`.
- Errors use one shared shape (section 7.2).
- Field names, units and ranges below are examples. AI/ML finalizes them once the dataset is chosen.

### 5.2 Prediction service (internal)

`POST /predict`

Request:

```json
{ "study_hours": 12, "attendance": 85, "previous_score": 64 }
```

Response `200`:

```json
{
  "predicted_score": 72.4,
  "grade": "B",
  "risk": "low",
  "model_version": "v1"
}
```

`GET /model-info` returns the model version, the input fields with their ranges, and the training metrics.

`GET /health` returns `{ "status": "ok", "model_loaded": true }`. If the model failed to load it returns status `503`.

### 5.3 Results service (public through the gateway)

| Method and path | Purpose | Phase |
| --- | --- | --- |
| `POST /api/predictions` | Validate input, get a prediction, return it (stores it in phase 2) | 1 |
| `GET /api/model-info` | Pass-through of the prediction service model info, used to build the form | 1 |
| `GET /api/health` | Health of the results service and its dependencies | 1 |
| `GET /api/predictions?limit=20` | Recent predictions | 2 |
| `GET /api/summary` | Counts by risk level for the teacher view | 2 |

`POST /api/predictions` request and response use the same fields as `/predict`, plus an `id` and `created_at` once storage is added in phase 2.

### 5.4 Valid input ranges (to be finalized by AI/ML)

| Field | Type | Unit | Min | Max |
| --- | --- | --- | --- | --- |
| `study_hours` | number | hours per week | 0 | 80 |
| `attendance` | number | percent | 0 | 100 |
| `previous_score` | number | percent | 0 | 100 |

The results service enforces these ranges and returns a validation error before calling the model.

### 5.5 Risk levels

| Risk | Meaning shown to the student |
| --- | --- |
| `low` | On track |
| `medium` | Some areas could use attention |
| `high` | A good moment to ask for help and adjust study habits |

AI/ML owns the thresholds and documents them in the model metadata file.

---

## 6. Processes

### 6.1 Git workflow (owner: DevOps)

**Branches**

- `main` is always deployable and is protected: changes arrive only by pull request, with one approving review and a passing CI run.
- Work happens on short-lived branches named `feature/<topic>`, `fix/<topic>` or `docs/<topic>`.

**Commits**

Use short, imperative messages with a prefix: `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `chore:`.

```text
feat: add result card to frontend
fix: return 422 for out-of-range attendance
ci: cache pip dependencies
```

**Pull requests**

1. Keep them small and focused on one thing.
2. Fill in the pull request template (what changed, how to test, screenshots for UI).
3. Request review from the code owner of the area.
4. Merge with squash once approved and green.
5. Delete the branch after merging.

**Never commit:** secrets, `.env` files, large datasets, or large model files (see 6.4).

**Pull request template** (`.github/pull_request_template.md`):

```markdown
## What changed

## How to test

## Checklist
- [ ] Runs locally with `docker compose up`
- [ ] Tests added or updated
- [ ] Docs updated if behavior or contracts changed
- [ ] No secrets or large files committed
```

### 6.2 Local development (owner: DevOps)

1. Install Docker and Docker Compose.
2. Clone the repository and copy the example settings: `cp .env.example .env`
3. Start everything: `docker compose up --build`
4. Open `http://localhost:8080`.
5. Stop with `Ctrl+C`, remove with `docker compose down`.

To work on one service, run it with its own tooling (for example `uvicorn app.main:app --reload` inside the service folder) and keep the others running in Compose.

**Mock mode:** until the real model is ready, the prediction service returns fixed fake predictions with the same response shape as the real one. This lets Frontend and the results service be built and tested immediately. Mock mode is switched by the `USE_MOCK_MODEL=true` setting.

### 6.3 ML workflow (owner: AI/ML)

```mermaid
flowchart LR
    A[Choose dataset] --> B[Clean and explore]
    B --> C[Train baseline]
    C --> D[Evaluate on test set]
    D --> E{Better than<br/>naive baseline?}
    E -->|no| C
    E -->|yes| F[Export model + metadata]
    F --> G[Open pull request]
    G --> H[Prediction service rebuilt by CI]
```

**Steps**

1. **Dataset:** choose a public student performance dataset or collect one. Document each column with its unit and range in `ml/data/README.md`.
2. **Clean and explore:** handle missing values and outliers in a notebook. Record decisions.
3. **Prediction type:** decide regression (score) or classification (pass/fail) in week one. The API contract depends on it.
4. **Baseline:** train a simple model first (for example linear regression or a random forest).
5. **Evaluate:** split data into training and test sets. Report one or two metrics (mean absolute error for scores, accuracy for pass/fail) and compare against a naive baseline such as always predicting the average.
6. **Pipeline:** include preprocessing in a scikit-learn `Pipeline` so the service does not repeat steps by hand.
7. **Export:** save `ml/models/model_vN.joblib` and `ml/models/model_vN.json` (6.4).
8. **`predict.py`:** a function that takes the agreed inputs, validates them and returns the agreed output. It is covered by unit tests.
9. **Reproduce:** `train.py` must rebuild the model from the data with one command.
10. **Notes:** update the model notes in `ml/README.md` (data source, features, metrics, limits).

### 6.4 Model versioning and delivery (owners: AI/ML and DevOps)

Every model has a version (`v1`, `v2`, ...) and two files:

- `model_vN.joblib`: the trained pipeline
- `model_vN.json`: metadata

Metadata file example:

```json
{
  "version": "v1",
  "trained_on": "2026-10-20",
  "python_version": "3.11",
  "scikit_learn_version": "1.5.2",
  "features": ["study_hours", "attendance", "previous_score"],
  "task": "regression",
  "metrics": { "mae": 6.1, "baseline_mae": 11.4 },
  "risk_thresholds": { "low": 65, "medium": 50 },
  "notes": "Trained on <dataset name>. Not validated for other schools."
}
```

The numbers above are placeholders to show the shape of the file.

**Delivery**

- Small model files (a few MB, typical for scikit-learn) are committed in `ml/models/` so builds are reproducible.
- Larger files go to GitHub Releases or object storage and are fetched at build time. Never commit large binaries to Git history.
- The model is copied into the prediction service image at build time. The image is tagged with the Git commit and the model version.
- The service reads `MODEL_PATH` at startup and refuses to start healthy if the file is missing or cannot load.
- The Python and scikit-learn versions in the metadata must match the service's `requirements.txt`. CI loads the model and runs one prediction to catch mismatches.

**Promoting a new model**

1. AI/ML opens a pull request with the new files and updated metrics.
2. CI loads the model and runs prediction tests.
3. Reviewer checks the metrics against the previous version.
4. After merge, the pipeline builds and deploys the new prediction service image.
5. To roll back, redeploy the previous image tag.

### 6.5 Frontend workflow (owner: Frontend)

1. Build against the mock API first, using the contract in section 5.
2. Build the form from `GET /api/model-info` where possible, so fields and ranges are not hard-coded twice.
3. Validate inputs in the browser before sending, with a clear message next to the field.
4. Call the API with a relative path (`/api/predictions`). The base path comes from a setting, never typed throughout the code.
5. Always handle three states: loading, success and error.
6. Show results as supportive guidance: score or grade, risk label, one line of explanation, and a note that this is an estimate.
7. Test in the browser DevTools Network tab when something fails.
8. Provide a working build command and output folder to DevOps.

**UI checklist before merging**

- [ ] Works on a phone-width screen
- [ ] Every field has a label and unit
- [ ] Error messages are readable by a non-technical person
- [ ] No sensitive inputs collected
- [ ] The estimate disclaimer is visible near the result

### 6.6 Continuous integration (owner: DevOps)

CI runs on every push and every pull request, in parallel per service where possible.

```mermaid
flowchart LR
    A[Push or PR] --> B[Lint]
    B --> C[Unit tests]
    C --> D[Build images]
    D --> E[Compose smoke test]
    E -->|merge to main| F[Push images to registry]
```

| Stage | What it checks | Fails the build when |
| --- | --- | --- |
| Lint | Python style (for example `ruff`), frontend lint, Dockerfile lint | Any error is reported |
| Unit tests | `pytest` for each service, model load and predict test | A test fails |
| Build | Each Docker image builds | A build fails |
| Smoke test | `docker compose up`, then call `/api/health` and one `/api/predictions` request | Either call fails |
| Publish (main only) | Images pushed to a container registry, tagged with the commit SHA | Push fails |

**Rules**

- A red build blocks the merge.
- Cache dependencies to keep runs fast.
- Secrets come from the CI secret store only.
- Fixing a broken `main` is the top priority for whoever broke it.

### 6.7 Deployment and rollback (owner: DevOps)

**Environments**

| Environment | Purpose | How it is updated |
| --- | --- | --- |
| Local | Development | `docker compose up` |
| Production demo | Public link for the demo | Automatic after merge to `main` |
| Staging (optional) | Test before production | Same pipeline, manual approval |

**Deployment (proposed)**

1. A small cloud VM runs Docker and Docker Compose.
2. The pipeline builds and pushes images tagged with the commit SHA.
3. The deploy step connects to the VM, pulls the new tags and restarts the stack with Compose.
4. The gateway provides HTTPS (for example with Let's Encrypt).
5. After the restart the pipeline calls the public `/api/health`. If it fails, the pipeline redeploys the previous tags automatically.

**Rollback:** redeploy the previous image tags. Because every release is tagged by commit SHA, any earlier state can be restored in minutes.

**Alternative:** a managed platform (Render, Railway, Fly.io) is acceptable if time is short, as long as the services stay separate and the same contracts apply.

### 6.8 Configuration and secrets (owner: DevOps)

- All settings come from environment variables. No setting is hard-coded.
- `.env.example` lists every variable with a safe placeholder. `.env` is in `.gitignore`.
- Real secrets (database password, server keys) live in the CI secret store and on the server, never in the repository.

| Variable | Service | Example | Purpose |
| --- | --- | --- | --- |
| `PREDICTION_SERVICE_URL` | results-service | `http://prediction-service:8001` | Where to reach the model service |
| `MODEL_PATH` | prediction-service | `/app/models/model_v1.joblib` | Model file to load |
| `USE_MOCK_MODEL` | prediction-service | `false` | Return fake predictions during development |
| `LOG_LEVEL` | all backend services | `info` | Logging detail |
| `CORS_ALLOWED_ORIGINS` | results-service | `http://localhost:5173` | Local development only |
| `DATABASE_URL` | results-service | `postgresql://user:pass@postgres:5432/results` | Phase 2 only; password is a secret |
| `API_BASE_PATH` | frontend | `/api` | Base path for API calls |

### 6.9 Monitoring and logging (owner: DevOps)

**Health checks**

- Every service exposes `GET /health`.
- Docker healthchecks use it, and Compose waits for healthy dependencies.
- The prediction service reports whether the model is loaded. The results service reports whether it can reach the prediction service (and the database in phase 2).

**Logging**

- One JSON object per line to standard output, so `docker compose logs` works everywhere.
- Required fields: `timestamp`, `level`, `service`, `request_id`, `message`.
- The gateway creates `X-Request-ID`. Every service logs it and passes it on, so one request can be followed across services.
- Never log full user inputs beyond what is needed for debugging, and never log secrets.

**Uptime**

- An external uptime check calls the public `/api/health` and alerts the team on failure.

**Optional extras:** Prometheus metrics and a Grafana dashboard for request counts, latency and prediction counts by risk level.

### 6.10 Testing strategy (everyone, per area)

| Level | Owner | What |
| --- | --- | --- |
| Model | AI/ML | `predict()` returns values in the allowed range, handles bad input, loads the saved model |
| Service unit tests | Service owner | Endpoints, validation, error shape (`pytest` with the framework's test client) |
| Contract | DevOps | Responses match section 5, including with the mock model |
| Smoke / integration | DevOps | Compose stack starts and one real request works end to end |
| UI | Frontend | Manual checklist in 6.5, plus any automated checks the team adds |

### 6.11 Troubleshooting guide

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| Model works locally but the service fails in Docker | Different Python or scikit-learn version | Compare versions in the metadata file and `requirements.txt`; pin them and rebuild |
| Prediction service never becomes healthy | Model file missing or cannot load | Check `MODEL_PATH` and the service logs |
| Frontend shows a network error | Gateway route or service not running | Check `docker compose ps` and the gateway config |
| Browser reports a CORS error | Frontend served from a different origin than the API | Use the gateway URL, or set `CORS_ALLOWED_ORIGINS` for local development |
| `422` from the API | Input outside the valid range | Check the response `details` field against section 5.4 |
| CI passes locally but fails in CI | Missing dependency or environment variable | Compare with `.env.example`; run the same commands in a clean container |
| Changes do not appear in the container | Old image used | Run `docker compose up --build` |

---

## 7. Design standards

### 7.1 API design

- Resource-style paths and plural nouns: `/api/predictions`.
- Use proper status codes: `200` success, `201` created, `400` bad request, `404` not found, `422` validation error, `503` dependency unavailable.
- Validate input at the edge (results service). The prediction service also validates, as a safety net.
- Never return stack traces to clients.
- Version through the model version in responses. If an incompatible change to a contract is unavoidable, add a new path (for example `/api/v2/...`) instead of changing the old one silently.

### 7.2 Error format

All services return errors in this shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Attendance must be between 0 and 100.",
    "details": [
      { "field": "attendance", "issue": "must be between 0 and 100" }
    ]
  },
  "request_id": "b6f1c2a0-0000-0000-0000-000000000000"
}
```

Error codes are uppercase with underscores: `VALIDATION_ERROR`, `MODEL_UNAVAILABLE`, `NOT_FOUND`, `INTERNAL_ERROR`.

### 7.3 Docker standards

- Pin base image versions (for example `python:3.11-slim`), never `latest`.
- Use multi-stage builds where they reduce image size.
- Run as a non-root user.
- Include a `.dockerignore` (exclude `.git`, datasets, notebooks, `.env`).
- One process per container.
- Define a `HEALTHCHECK` for each service.
- No secrets baked into images.
- Tag images with the Git commit SHA. `latest` is for local use only.

### 7.4 Code style

| Area | Standard |
| --- | --- |
| Python | Python 3.11 (proposed), formatted and linted with `ruff`, type hints on public functions |
| Python naming | `snake_case` for functions and variables, `PascalCase` for classes |
| JavaScript | Consistent formatter and linter agreed by Frontend, `camelCase` for variables |
| File and folder names | lowercase with hyphens for folders and services, `snake_case` for Python files |
| Comments | Explain why, not what |
| Dependencies | Pin versions in `requirements.txt` or lock files |

### 7.5 UI and wording standards

- Plain language, no jargon.
- Every number has a unit.
- Predictions are always labeled as estimates.
- Risk labels use supportive wording (section 5.5). Never show "you will fail".
- Accessible by default: labels linked to fields, sufficient color contrast, and meaning never conveyed by color alone.

### 7.6 Security basics

- Only the gateway is public; internal services are not exposed.
- HTTPS in the deployed environment.
- No secrets in the repository or images.
- Rate limiting on the gateway (proposed) to protect the prediction service.
- Keep dependencies updated and scan images in CI if time allows.

---

## 8. Definition of done

A task is done when all of the following are true:

- [ ] It runs locally with `docker compose up`
- [ ] Tests exist for new behavior and CI is green
- [ ] A teammate has reviewed and approved it
- [ ] Contracts and this document are updated if behavior changed
- [ ] No secrets, datasets or large binaries were committed

---

## 9. Responsible use of predictions

- Do not use gender, ethnicity or other sensitive attributes as model inputs.
- Present results as estimates with a risk level and suggested next steps, not as final judgments.
- State the limits of the model in `ml/README.md` and in the interface: a small dataset may not apply to other schools or courses.
- Do not store personal identifiers unless a clear need exists. If history is added in phase 2, store only what the feature needs.
- Review the wording and outputs together before the demo.

---

## 10. Phases and roadmap

| Phase | DevOps | AI/ML | Frontend |
| --- | --- | --- | --- |
| 1. Setup and agreements | Repo, branch protection, README, templates, mock prediction service, compose skeleton | Choose dataset, list columns, decide regression or classification | Pick framework, sketch layout, learn the basics |
| 2. Build in parallel | Dockerfiles for each service, gateway, CI pipeline | Clean data, train baseline, evaluate | Form, validation, result card against the mock |
| 3. Integrate | Results service calls the real model, model delivery, end-to-end smoke test | Export `model_v1`, finish `predict.py`, pin requirements | Switch to the real API, handle errors and loading states |
| 4. Deploy and harden | Deploy to the cloud VM, HTTPS, health checks, logging, uptime check, rollback test | Model notes and limits, improve the model if time allows | Polish the UI, add one extra feature (what-if sliders or a chart) |
| 5. Phase 2 features (optional) | Postgres, history endpoints, metrics dashboard | Feature importance output | History chart, teacher view |
| 6. Demo preparation | Test from a clean machine, prepare rollback, finalize docs | Plain-language explanation of the model and its metrics | Demo flow and realistic example inputs |

---

## 11. Learning resources

| Role | Start here |
| --- | --- |
| AI/ML | Kaggle Learn (Python, Pandas, Intro and Intermediate Machine Learning); StatQuest on YouTube for core concepts; the scikit-learn user guide on pipelines and model evaluation; the FastAPI tutorial for serving a model |
| Frontend | MDN guides for HTML, CSS and JavaScript; javascript.info for `fetch` and async/await; the Chart.js documentation; browser DevTools Network tab for debugging |
| DevOps | Traefik or Nginx routing docs; Docker Compose networking and healthchecks; FastAPI and SQLAlchemy docs if building the results service; Prometheus and Grafana docs for the optional dashboard |
| Everyone | A shared Git and pull request walkthrough in week one; FastAPI's built-in `/docs` page for testing APIs; a short weekly show-and-tell where each person demos what they built |
