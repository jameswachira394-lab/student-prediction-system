/**
 * API Integration Module (frontendesign.md Section 12)
 *
 * CONTRACTS:
 * 1. GET /api/model-info
 *    Returns input fields, units, min/max ranges, and risk thresholds.
 *
 * 2. POST /api/predictions
 *    Request:  { "study_hours": 12, "attendance": 85, "previous_score": 64 }
 *    Response: { "predicted_score": 72.4, "grade": "B", "risk": "low", "model_version": "v1", "feature_importance": {...} }
 */

// Fallback mock model info to use if API is offline during local UI development
const MOCK_MODEL_INFO = {
  model_version: 'mock',
  task: 'regression',
  fields: [
    {
      name: 'study_hours',
      label: 'Study hours per week',
      unit: 'hours',
      min: 0,
      max: 80,
      hint: 'Time you spend studying outside class each week.',
    },
    {
      name: 'attendance',
      label: 'Attendance',
      unit: '%',
      min: 0,
      max: 100,
      hint: 'Share of classes you attended this term.',
    },
    {
      name: 'previous_score',
      label: 'Previous score',
      unit: '%',
      min: 0,
      max: 100,
      hint: 'Your most recent exam or test result.',
    },
  ],
  risk_thresholds: { low: 65, medium: 50 },
  feature_importance: {
    attendance: 0.46,
    study_hours: 0.33,
    previous_score: 0.21,
  },
};

/**
 * Fetch model information (fields, ranges, thresholds)
 * @returns {Promise<Object>}
 */
async function fetchModelInfo() {
  try {
    const res = await fetch(`${CONFIG.API_BASE}/model-info`);
    if (!res.ok) {
      throw new Error(`Failed to fetch model info (${res.status})`);
    }
    return await res.json();
  } catch (err) {
    console.warn('API /model-info unreachable, using fallback MOCK_MODEL_INFO:', err);
    return MOCK_MODEL_INFO;
  }
}

/**
 * Submit inputs to get a prediction
 * @param {Object} data { study_hours, attendance, previous_score }
 * @returns {Promise<Object>}
 */
async function postPrediction(data) {
  try {
    const res = await fetch(`${CONFIG.API_BASE}/predictions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      const error = new Error(errBody?.error?.message || 'Prediction API request failed');
      error.status = res.status;
      error.body = errBody;
      throw error;
    }

    return await res.json();
  } catch (err) {
    // If running in standalone local static dev (no backend running on port)
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      // Check if we are on standalone localhost without backend
      console.warn('Network error reaching /api/predictions:', err);
    }
    throw err;
  }
}
