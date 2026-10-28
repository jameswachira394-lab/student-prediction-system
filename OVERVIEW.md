# Student Results Prediction System: Technical Overview

This document provides a comprehensive overview of the architecture, components, and implementation details of the **Student Results Prediction System**. It is organized into three distinct technical domains: **DevOps & Backend** (owned by the DevOps lead/Backend engineer), **Frontend**, and **Machine Learning (AI/ML)**.

---

## Architecture at a Glance

The application employs a decoupled microservices architecture fronted by an Nginx reverse-proxy gateway and orchestrated using Docker Compose.

```
                    +---------------------------------------+
                    |           Public Client               |
                    +---------------------------------------+
                                        |
                                        v
                    +---------------------------------------+
                    |           gateway (Nginx)             |
                    |              Port 8080                |
                    +---------------------------------------+
                             /                     \
       HTTP GET / (Static)  /                       \  HTTP /api/*
                           v                         v
            +--------------------+       +-------------------------+
            |  frontend (Nginx)  |       | results-service (API)   |
            |     HTML/CSS/JS    |       |      FastAPI :8000      |
            +--------------------+       +-------------------------+
                                                      |
                                                      | Internal HTTP :8001
                                                      v
                                         +-------------------------+
                                         | prediction-service (ML) |
                                         |      FastAPI :8001      |
                                         |  scikit-learn pipeline  |
                                         +-------------------------+
```

---

## 1. DevOps & Backend

> **Owner:** DevOps / Backend Developer  
> **Responsibilities:** Cloud infrastructure, microservices architecture, API edge routing, data validation, containerization, CI/CD pipelines, and health monitoring.

### 1.1 Microservices Architecture
The server layer is split into two specialized asynchronous services implemented in **Python 3.11** with **FastAPI** and **Uvicorn**:

1. **Results Service (`services/results-service/`)**:
   - Acts as the public API edge controller behind the gateway.
   - Enforces request validation using **Pydantic** (`services/results-service/app/validation.py`) for incoming feature inputs.
   - Forwards inference requests to the internal prediction service via asynchronous **HTTPX** client calls (`services/results-service/app/clients.py`).
   - Standardizes response envelopes and propagates incoming tracing headers (`X-Request-ID`).
   - Serves public endpoints:
     - `POST /api/predictions`: Validates student data and returns predicted scores, letter grades, and risk tiers.
     - `GET /api/model-info`: Proxies metadata describing active model fields and ranges to drive dynamic frontend rendering.
     - `GET /api/health`: Aggregated health check verifying the readiness of both itself and dependent services.

2. **Prediction Service (`services/prediction-service/`)**:
   - Internal service isolated from direct public internet access.
   - Loads the serialized machine learning pipeline into memory on startup (`services/prediction-service/app/predict.py`).
   - Provides a built-in mock mode (`USE_MOCK_MODEL=true`) allowing end-to-end frontend and pipeline testing before final model weights are baked in.
   - Serves internal endpoints:
     - `POST /predict`: Executes pipeline inference against structured input payloads.
     - `GET /model-info`: Returns model version, accepted feature schemas, min/max bounds, and grade thresholds.
     - `GET /health`: Internal readiness probe verifying model memory presence.

### 1.2 Error Handling & API Contracts
All services implement a uniform error contract to eliminate client-side ambiguity:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Study hours must be between 0 and 80.",
    "details": [
      { "field": "study_hours", "issue": "must be between 0 and 80" }
    ]
  },
  "request_id": "a9b8c7d6-0000-0000-0000-000000000000"
}
```

### 1.3 Gateway & Reverse Proxy
- Implemented with **Nginx** in `gateway/nginx.conf`.
- Exposes port `8080` to the host environment as the single public ingress.
- Routes path `/` to the `frontend` container and `/api/` to `results-service`.
- Injects correlation tracking via `$request_id` passed down to upstream services in the `X-Request-ID` header.

### 1.4 Containerization & Local Orchestration
- **Dockerfiles:** Lean, multi-stage images based on `python:3.11-slim` and `nginx:alpine`, running as unprivileged non-root users.
- **Docker Compose (`docker-compose.yml`):**
  - Defines service boundaries, environment configurations, and network isolation.
  - Implements container-level healthchecks (`test: ["CMD", "python", "-c", "..."]`) ensuring dependent services start in correct topological sequence (`condition: service_healthy`).

### 1.5 CI/CD & Automated Quality Gates
Configured with **GitHub Actions** (`.github/workflows/main.yml`) executing on every pull request and push to `main`:
- **Static Analysis & Linting:** Automated checks across all Python services with **Ruff**.
- **Automated Testing:** Test suites run via **pytest** and **pytest-asyncio** covering API endpoints, input validation boundaries, mock responses, and error shapes.
- **Image Verification:** Automated headless Docker image builds verifying container compilation integrity.

---

## 2. Frontend

> **Owner:** Frontend Developer  
> **Responsibilities:** User interface design, client-side input validation, dynamic form generation, state management, and accessible presentation of predictive guidance.

### 2.1 Technology Stack & Structure
The client application is intentionally engineered with lightweight, dependency-free **Vanilla JavaScript (ES6+)**, **Semantic HTML5**, and modern **CSS3**, served through an Nginx container (`frontend/`):
- `frontend/src/index.html`: Accessible, responsive markup supporting both desktop and mobile viewports.
- `frontend/src/styles/tokens.css`: Centralized CSS variables for palette colors, surface elevations, spacing, and risk tier color tokens (`--zone-green`, `--zone-amber`, `--zone-rose`).
- `frontend/src/styles/base.css`: Reset stylesheets, typography scale, container layouts, and focus rings.
- `frontend/src/styles/components.css`: Component styling for sliders, badges, gauge markers, cards, and feedback alerts.
- `frontend/src/js/config.js` & `api.js`: Resilient fetch clients for `/api/model-info` and `/api/predictions` with automatic fallback to mock schema during isolated development.
- `frontend/src/js/form.js`: Dynamic form generator and synchronizer.
- `frontend/src/js/render.js`: Component state renderer.
- `frontend/src/js/main.js`: Main lifecycle orchestrator.

### 2.2 Interactive Form & Bi-directional Binding
- Dynamically derives input fields, labels, hints, and constraints directly from the `/api/model-info` payload.
- Provides smooth bi-directional synchronization between slider controls (`<input type="range">`) and numerical stepper fields (`<input type="number">`).
- Real-time client-side validation ensuring numbers conform to min/max boundaries before network dispatch.

### 2.3 Comprehensive UI State Lifecycle
The frontend provides dedicated render implementations for each stage of user interaction:
1. **Empty State:** Clean initial guidance prompting the student to input their study metrics.
2. **Loading State:** Disabled submit buttons, animated spinner, and skeleton loaders to indicate active prediction calculation.
3. **Success State:** Displays:
   - Big 80px predicted exam score indicator.
   - Letter Grade Chip (`A`, `B`, `C`, `D`).
   - Risk Badge (`low`, `medium`, `high`) accompanied by supportive, non-punitive guidance text.
   - Visual 3-zone Score Gauge displaying relative positioning along the outcome spectrum.
4. **Validation & Error States:** Clear inline field highlighting for invalid entries (`aria-invalid="true"`) and friendly server-error alert dialogs featuring a "Try again" action.

### 2.4 Accessibility & Ethical Presentation Standards
- Built to **WCAG 2.1 AA** accessibility standards: all inputs possess programmatic `<label for>` associations, visible focus indicators, and keyboard navigation support.
- Information is never communicated solely through color: all risk statuses combine colors with descriptive textual indicators and iconography.
- Adheres to ethical guidelines: results are consistently labeled as estimates and supportive guidance rather than definitive judgments.

---

## 3. Machine Learning (AI/ML)

> **Owner:** AI/ML Developer  
> **Responsibilities:** Dataset preprocessing, exploratory data analysis, feature engineering, model training and evaluation, pipeline serialization, and the inference interface.

### 3.1 Problem Definition & Dataset
- **Objective:** Predict student academic outcomes based on historical performance indicators, study habits, and background features.
- **Target Variable:** `Pass_status` (Pass / Fail classification) and probability estimation.
- **Input Features (7 total):**
  - **Academic & Behavioral:** `Study_Hours_per_Week`, `Attendance_Rate`, `Past_Exam_Scores`, `Extracurricular_Activities`.
  - **Contextual & Demographic:** `Gender`, `Parental_Education_Level`, `Internet_Access_at_Home`.

### 3.2 Preprocessing Pipeline & Feature Engineering
- Automated data cleaning scripts (`ml/clean_data.py`, `ml/rename_columns.py`) handle missing value imputation, outlier handling, and feature standardization.
- Pipeline incorporates **scikit-learn** transformers:
  - Continuous numerical features scaled using `StandardScaler`.
  - Categorical variables encoded using `OneHotEncoder(handle_unknown='ignore')`.

### 3.3 Model Exploration, Tuning & Evaluation
Multiple machine learning algorithms and configurations were evaluated using stratified cross-validation (`ml/compare_models.py`, `ml/tune_model.py`, `ml/cross_validate_model.py`):
- **Selected Model:** A regularized **Logistic Regression** pipeline balancing high recall with interpretability.
- **Held-Out Test Set Metrics:**
  - **Accuracy:** ~75%
  - **Recall:** ~72%
  - **F1-Score:** ~63%
  - **Precision:** ~55%
- Serialized model artifact saved as `ml/models/pass_status_model.pkl` using **Joblib**.

### 3.4 Inference API Module (`ml/predictor.py`)
- Provides a clean programmatic interface `predict_student(student_data)` for integration into service backends.
- Enforces strict input feature presence validation against `FEATURE_COLUMNS`.
- Returns both deterministic class prediction (`predicted_status`) and continuous confidence scores (`probabilities` for both classes).

### 3.5 ML Testing & Validation
- Unit tests (`ml/tests/test_predictor.py`, `ml/tests/test_saved_model.py`) verify:
  - Valid loading and serialization stability of `pass_status_model.pkl`.
  - Proper handling of missing input features and validation errors.
  - Probability distributions sum to 1.0 within expected numerical precision.
