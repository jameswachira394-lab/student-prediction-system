/**
 * Screen States & UI Rendering Module (frontendesign.md Section 7.5 - 7.9, Section 9)
 *
 * NOTE FOR FRONTEND DEVELOPER:
 * Implement rendering for the 4 core screen states:
 *
 * 1. EMPTY STATE (Section 9)
 *    - 64px icon circle
 *    - Title: "Your estimate will appear here"
 *    - Subtext: "Fill in the three fields, then press Predict my result."
 *
 * 2. LOADING STATE (Section 9)
 *    - Spinner + "Working out your estimate"
 *    - Skeleton placeholders (using --track background)
 *    - Submit button disabled with "Predicting your result"
 *    - Set aria-busy="true" and role="status"
 *
 * 3. SUCCESS STATE (Section 7.5, 7.6, 7.7)
 *    - Score: big 80px Manrope 800 with "%"
 *    - GradeChip: 68px square in --primary-soft, "Grade" caption above letter
 *    - RiskBadge pill:
 *      * 'low': "On track", check circle, --ontrack-*
 *      * 'medium': "Needs attention", exclamation circle, --attention-*
 *      * 'high': "Ask for support", lifebuoy, --support-*
 *    - ScoreGauge:
 *      * 14px tall pill bar split into 3 zones (--zone-support, --zone-attention, --zone-ontrack)
 *      * Marker: 24px circle (white with 4px --ink ring) positioned by percentage: style="left: ${score}%"
 *      * Legend below: colored squares + zone names and ranges
 *    - Footnote: "This is an estimate, not a guarantee." on left; "Model v1" on right
 *    - Focus management: Move focus to result heading or announce politely
 *
 * 4. SERVER ERROR STATE (Section 9)
 *    - 64px circle with warning icon in --support-bg
 *    - Title: "We could not get your estimate"
 *    - Message: "The prediction service is not answering right now. Your answers are still in the form, so you can try again in a moment."
 *    - "Try again" button that triggers re-submission
 */

/**
 * Show the initial empty state in the result card
 */
function renderEmptyState() {
  const container = document.getElementById('result-content');
  if (!container) return;
  // Developer: Render empty state markup
}

/**
 * Show loading spinner and skeleton placeholders while waiting for the API
 */
function renderLoadingState() {
  const container = document.getElementById('result-content');
  const submitBtn = document.getElementById('submit-btn');
  if (!container) return;
  // Developer: Render loading state and disable submit button
}

/**
 * Show prediction results
 * @param {Object} result { predicted_score, grade, risk, model_version, feature_importance }
 * @param {Object} modelInfo Metadata including risk_thresholds
 */
function renderSuccessState(result, modelInfo) {
  const container = document.getElementById('result-content');
  if (!container) return;
  // Developer: Render score, GradeChip, RiskBadge, ScoreGauge, explanation, and footnote
}

/**
 * Show server error state with a retry button
 * @param {Function} onRetry Callback invoked when the student clicks "Try again"
 */
function renderErrorState(onRetry) {
  const container = document.getElementById('result-content');
  if (!container) return;
  // Developer: Render server error state with retry button
}

/**
 * Render feature importance horizontal bars
 * @param {Object} featureImportance e.g. { attendance: 0.46, study_hours: 0.33, previous_score: 0.21 }
 */
function renderInfluenceBars(featureImportance) {
  const container = document.getElementById('influence-bars');
  if (!container) return;
  // Developer: Sort features by percentage descending and render horizontal progress bars
}

/**
 * Render supportive study tips
 */
function renderTips() {
  const container = document.getElementById('tips-list');
  if (!container) return;
  // Developer: Render the 3 tips with icon circles and supportive wording
}
