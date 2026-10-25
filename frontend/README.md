# Frontend Developer Guide

Welcome to the frontend of the **Student Results Prediction System**.

This folder contains the scaffolding for the client web app. The complete design specification is detailed in [`frontendesign.md`](../frontendesign.md) at the repository root.

---

## 1. Quick Start (Local Development)

Run a local server directly in the `frontend/src` directory:

```bash
cd frontend/src
python3 -m http.server 3000
```

Then open **http://localhost:3000** in your browser.

> **Tip:** When developing locally without backend containers, `fetchModelInfo()` in `js/api.js` automatically falls back to `MOCK_MODEL_INFO` so you can style and test all form and result states immediately.

---

## 2. File Organization

```text
frontend/
├── src/
│   ├── index.html          # Semantic HTML layout (desktop & mobile)
│   ├── styles/
│   │   ├── tokens.css      # Design tokens (colors, radii, zone colors) - DO NOT hard-code hexes
│   │   ├── base.css        # Typography scale, reset, focus ring, page container
│   │   └── components.css  # Card, slider, button, badge, gauge, and state styles
│   └── js/
│       ├── config.js       # API_BASE setting ('/api')
│       ├── api.js          # Fetch wrappers for /api/model-info and /api/predictions
│       ├── form.js         # Dynamic SliderField rendering, slider↔number sync & validation
│       ├── render.js       # Empty, Loading, Success, and Error state rendering
│       └── main.js         # App bootstrap and event wiring
├── Dockerfile              # DevOps-managed Nginx container
└── nginx.conf              # Nginx proxy config (/ -> frontend, /api -> gateway)
```

---

## 3. Key Design Requirements

1. **Principles:** Supportive, plain language, unit on every number, color is never the only signal (risk badges have icons and text).
2. **Design Tokens:** Always use CSS variables from `styles/tokens.css`.
3. **Responsive Breakpoint:**
   - **`>= 1080px`**: Two-column layout (Form on left ~560px, Result on right ~440px; Influence & Tips side-by-side).
   - **`< 1080px`**: Single-column stack (Form → Result → Influence → Tips).
4. **Interactive States:**
   - **Empty:** Shown on page load before any calculation.
   - **Loading:** Spinner + skeleton placeholders; submit button disabled.
   - **Success:** Big 80px score, GradeChip, RiskBadge pill, 3-zone ScoreGauge with positioned marker, supportive explanation, and footnote.
   - **Validation Error:** 2px `--support-text` border, `--error-field-bg` fill, alert message below field, `aria-invalid="true"`.
   - **Server Error:** Warning icon, supportive message, and "Try again" button.
5. **Accessibility Checklist:**
   - Every input linked with `<label for>` and `<input id>`.
   - Keyboard navigable with 3px focus ring (`:focus-visible`).
   - `aria-busy="true"` and `role="status"` during loading; `role="alert"` for errors.
   - Contrast ratio ≥ 4.5:1.

---

## 4. API Endpoints

- **`GET /api/model-info`**: Returns input fields, min/max ranges, and risk thresholds.
- **`POST /api/predictions`**:
  - Request: `{"study_hours": 12, "attendance": 85, "previous_score": 64}`
  - Response: `{"predicted_score": 72.4, "grade": "B", "risk": "low", "model_version": "v1"}`

For full design specifications, see [`frontendesign.md`](../frontendesign.md).
