/**
 * API Integration Module (frontendesign.md Section 12)
 *
 * CONTRACTS:
 * 1. GET /api/model-info
 *    Returns input fields, units, min/max ranges, and risk thresholds.
 *
 * 2. POST /api/predictions
 *    Request:  { "study_hours": 12, "attendance": 85, "previous_score": 64 }
 *    Response: { "predicted_score": 72.4, "grade": "B", "risk": "low", "model_version": "v1" }
 */

// Fallback mock model info to use if API is offline during local UI development
const MOCK_MODEL_INFO = {
  model_version: 'mock',
  task: 'regression',
  fields: [
    { name: 'study_hours', label: 'Study hours per week', unit: 'hours', min: 0, max: 80, hint: 'Time you spend studying outside class each week.' },
    { name: 'attendance', label: 'Attendance', unit: '%', min: 0, max: 100, hint: 'Share of classes you attended this term.' },
    { name: 'previous_score', label: 'Previous score', unit: '%', min: 0, max: 100, hint: 'Your most recent exam or test result.' },
  ],
  risk_thresholds: { low: 65, medium: 50 },
};

/**
 * Fetch model information (fields, ranges, thresholds)
 * @returns {Promise<Object>}
 */
async function fetchModelInfo() {
  // Developer:
  // 1. Fetch from `${CONFIG.API_BASE}/model-info`
  // 2. If it fails or in offline development, fall back to MOCK_MODEL_INFO
  try {
    const res = await fetch(`${CONFIG.API_BASE}/model-info`);
    if (!res.ok) throw new Error('Failed to fetch model info');
    return await res.json();
  } catch (err) {
    console.warn('Using fallback MOCK_MODEL_INFO:', err);
    return MOCK_MODEL_INFO;
  }
}

/**
 * Submit inputs to get a prediction
 * @param {Object} data { study_hours, attendance, previous_score }
 * @returns {Promise<Object>}
 */
async function postPrediction(data) {
  // Developer:
  // 1. Send POST request to `${CONFIG.API_BASE}/predictions` with JSON body
  // 2. Handle HTTP 422 (validation error) and 503 (model unavailable)
  const res = await fetch(`${CONFIG.API_BASE}/predictions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    const error = new Error('Prediction API error');
    error.status = res.status;
    error.body = errBody;
    throw error;
  }

  return res.json();
}
