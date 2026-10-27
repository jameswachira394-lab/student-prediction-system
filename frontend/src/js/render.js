/**
 * Screen States & UI Rendering Module (frontendesign.md Section 7.5 - 7.9, Section 9)
 */

/**
 * SVGs used across states
 */
const ICONS = {
  arrowRight: `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <line x1="5" y1="12" x2="19" y2="12"></line>
      <polyline points="12 5 19 12 12 19"></polyline>
    </svg>`,
  checkCircle: `
    <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="10" cy="10" r="8"></circle>
      <polyline points="6 10 9 13 14 7"></polyline>
    </svg>`,
  exclamationCircle: `
    <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="10" cy="10" r="8"></circle>
      <line x1="10" y1="6" x2="10" y2="10"></line>
      <circle cx="10" cy="14" r="0.75" fill="currentColor"></circle>
    </svg>`,
  lifebuoy: `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10"></circle>
      <circle cx="12" cy="12" r="4"></circle>
      <line x1="4.93" y1="4.93" x2="9.17" y2="9.17"></line>
      <line x1="14.83" y1="14.83" x2="19.07" y2="19.07"></line>
      <line x1="14.83" y1="9.17" x2="19.07" y2="4.93"></line>
      <line x1="4.93" y1="19.07" x2="9.17" y2="14.83"></line>
    </svg>`,
  alertTriangle: `
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
      <line x1="12" y1="9" x2="12" y2="13"></line>
      <circle cx="12" cy="17" r="1" fill="currentColor"></circle>
    </svg>`,
  calendarCheck: `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
      <line x1="16" y1="2" x2="16" y2="6"></line>
      <line x1="8" y1="2" x2="8" y2="6"></line>
      <line x1="3" y1="10" x2="21" y2="10"></line>
      <polyline points="9 16 11 18 15 14"></polyline>
    </svg>`,
  clock: `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10"></circle>
      <polyline points="12 6 12 12 16 14"></polyline>
    </svg>`,
  target: `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10"></circle>
      <circle cx="12" cy="12" r="6"></circle>
      <circle cx="12" cy="12" r="2"></circle>
    </svg>`,
};

/**
 * Resets submit button to active state
 */
function restoreSubmitButton() {
  const submitBtn = document.getElementById('submit-btn');
  if (submitBtn) {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<span>Predict my result</span>${ICONS.arrowRight}`;
  }
}

/**
 * Show the initial empty state in the result card (Section 9)
 */
function renderEmptyState() {
  const container = document.getElementById('result-content');
  const card = document.getElementById('result-card');
  if (!container) return;

  if (card) {
    card.setAttribute('aria-busy', 'false');
  }

  container.innerHTML = `
    <div class="state-empty">
      <div class="empty-icon-circle" aria-hidden="true">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
      </div>
      <h3 class="empty-title">Your estimate will appear here</h3>
      <p class="empty-desc">Fill in the three fields, then press Predict my result.</p>
    </div>
  `;
}

/**
 * Show loading spinner and skeleton placeholders while waiting for the API (Section 9)
 */
function renderLoadingState() {
  const container = document.getElementById('result-content');
  const card = document.getElementById('result-card');
  const submitBtn = document.getElementById('submit-btn');
  if (!container) return;

  if (card) {
    card.setAttribute('aria-busy', 'true');
  }

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="btn-spinner" aria-hidden="true"></span><span>Predicting your result…</span>`;
  }

  container.innerHTML = `
    <div class="state-loading" role="status">
      <div class="loading-header">
        <div class="spinner" aria-hidden="true"></div>
        <span class="loading-title">Working out your estimate…</span>
      </div>
      <div class="skeleton-score-row">
        <div class="skeleton skeleton-score"></div>
        <div class="skeleton skeleton-chip"></div>
      </div>
      <div class="skeleton skeleton-badge"></div>
      <div class="skeleton skeleton-gauge"></div>
      <div class="skeleton skeleton-text"></div>
      <div class="skeleton skeleton-text-sub"></div>
    </div>
  `;
}

/**
 * Show prediction results (Section 7.5, 7.6, 7.7)
 * @param {Object} result { predicted_score, grade, risk, model_version, feature_importance }
 * @param {Object} modelInfo Metadata including risk_thresholds
 */
function renderSuccessState(result, modelInfo) {
  const container = document.getElementById('result-content');
  const card = document.getElementById('result-card');
  if (!container) return;

  restoreSubmitButton();

  if (card) {
    card.setAttribute('aria-busy', 'false');
  }

  const score = Number(result.predicted_score) || 0;
  const formattedScore = score % 1 === 0 ? score.toString() : score.toFixed(1);
  const grade = result.grade || 'B';
  const risk = (result.risk || 'low').toLowerCase();
  const isMock = result.model_version === 'mock';
  const modelVersion = result.model_version || 'v1';

  // Risk badge configuration
  const riskConfig = {
    low: {
      label: 'On track',
      badgeClass: 'low',
      icon: ICONS.checkCircle,
    },
    medium: {
      label: 'Needs attention',
      badgeClass: 'medium',
      icon: ICONS.exclamationCircle,
    },
    high: {
      label: 'Ask for support',
      badgeClass: 'high',
      icon: ICONS.lifebuoy,
    },
  }[risk] || {
    label: 'On track',
    badgeClass: 'low',
    icon: ICONS.checkCircle,
  };

  // Score gauge thresholds
  const thresholds = modelInfo?.risk_thresholds || { low: 65, medium: 50 };
  const mediumThreshold = thresholds.medium || 50;
  const lowThreshold = thresholds.low || 65;

  const supportPct = mediumThreshold;
  const attentionPct = lowThreshold - mediumThreshold;
  const onTrackPct = 100 - lowThreshold;

  const markerLeft = Math.min(100, Math.max(0, score));

  // Supportive one-sentence explanation
  let explanation = '';
  if (risk === 'low') {
    explanation = 'You are in a great position. Maintaining regular study hours and strong attendance will keep you on track.';
  } else if (risk === 'medium') {
    explanation = 'You are close to your goals. Adding a little extra study time each week can help nudge your result higher.';
  } else {
    explanation = 'Support is available to help you succeed. Reaching out to your teachers and setting up regular revision will make a real difference.';
  }

  container.innerHTML = `
    <div class="state-success">
      <div class="result-card-header">
        <h3 id="result-heading" class="card-heading" tabindex="-1">Your estimate</h3>
        ${isMock ? `<span class="sample-tag">Sample data</span>` : ''}
      </div>

      <div class="result-score-row">
        <div class="score-display">
          <span class="score-number">${formattedScore}</span>
          <span class="score-unit">%</span>
        </div>
        <div class="grade-chip" aria-label="Estimated Grade ${grade}">
          <span class="grade-caption">Grade</span>
          <span class="grade-letter">${grade}</span>
        </div>
      </div>

      <div class="risk-badge-wrap">
        <span class="risk-badge ${riskConfig.badgeClass}">
          ${riskConfig.icon}
          <span>${riskConfig.label}</span>
        </span>
      </div>

      <div class="gauge-container" aria-label="Score gauge from 0 to 100%">
        <div class="gauge-bar-wrap">
          <div class="gauge-bar" role="progressbar" aria-valuenow="${score}" aria-valuemin="0" aria-valuemax="100">
            <div class="gauge-zone support" style="width: ${supportPct}%;"></div>
            <div class="gauge-zone attention" style="width: ${attentionPct}%;"></div>
            <div class="gauge-zone ontrack" style="width: ${onTrackPct}%;"></div>
          </div>
          <div class="gauge-marker" style="left: ${markerLeft}%;" title="Estimate: ${formattedScore}%"></div>
        </div>
        <div class="gauge-legend">
          <div class="legend-item">
            <span class="legend-dot support"></span>
            <span>Ask for support (0–${mediumThreshold - 1}%)</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot attention"></span>
            <span>Needs attention (${mediumThreshold}–${lowThreshold - 1}%)</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot ontrack"></span>
            <span>On track (${lowThreshold}% and up)</span>
          </div>
        </div>
      </div>

      <p class="result-explanation">${explanation}</p>

      <div class="result-footnote">
        <span>This is an estimate, not a guarantee.</span>
        <span>Model ${modelVersion}</span>
      </div>
    </div>
  `;

  // Focus result heading politely for keyboard/screen reader users
  const heading = document.getElementById('result-heading');
  if (heading) {
    heading.focus();
  }
}

/**
 * Show server error state with a retry button (Section 9)
 * @param {Function} onRetry Callback invoked when the student clicks "Try again"
 */
function renderErrorState(onRetry) {
  const container = document.getElementById('result-content');
  const card = document.getElementById('result-card');
  if (!container) return;

  restoreSubmitButton();

  if (card) {
    card.setAttribute('aria-busy', 'false');
  }

  container.innerHTML = `
    <div class="state-error" role="alert">
      <div class="error-icon-circle" aria-hidden="true">
        ${ICONS.alertTriangle}
      </div>
      <h3 class="error-title">We could not get your estimate</h3>
      <p class="error-desc">
        The prediction service is not answering right now. Your answers are still in the form, so you can try again in a moment.
      </p>
      <button type="button" id="retry-btn" class="btn btn-primary">
        <span>Try again</span>
      </button>
    </div>
  `;

  const retryBtn = document.getElementById('retry-btn');
  if (retryBtn && typeof onRetry === 'function') {
    retryBtn.addEventListener('click', onRetry);
  }
}

/**
 * Render feature importance horizontal bars (Section 7.8)
 * @param {Object} featureImportance e.g. { attendance: 0.46, study_hours: 0.33, previous_score: 0.21 }
 */
function renderInfluenceBars(featureImportance) {
  const container = document.getElementById('influence-bars');
  const influenceCard = document.getElementById('influence-card');
  if (!container) return;

  if (!featureImportance || Object.keys(featureImportance).length === 0) {
    // If no feature importance data, hide the card per frontend design Section 12
    if (influenceCard) influenceCard.style.display = 'none';
    return;
  }

  if (influenceCard) influenceCard.style.display = 'flex';

  const labelMap = {
    attendance: 'Attendance',
    study_hours: 'Study hours',
    previous_score: 'Previous score',
  };

  // Convert to array and sort descending by weight
  const entries = Object.entries(featureImportance)
    .map(([key, val]) => ({
      key,
      label: labelMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      value: Number(val),
    }))
    .sort((a, b) => b.value - a.value);

  container.innerHTML = entries
    .map((item) => {
      // If values are <= 1, convert to percentage
      const pct = item.value <= 1 ? Math.round(item.value * 100) : Math.round(item.value);
      return `
        <div class="influence-row">
          <span class="influence-label">${item.label}</span>
          <div class="influence-track" aria-hidden="true">
            <div class="influence-fill" style="width: ${pct}%;"></div>
          </div>
          <span class="influence-val">${pct}%</span>
        </div>
      `;
    })
    .join('');
}

/**
 * Render supportive study tips (Section 7.9)
 */
function renderTips() {
  const container = document.getElementById('tips-list');
  if (!container) return;

  const tips = [
    {
      icon: ICONS.calendarCheck,
      title: 'Keep attendance high',
      body: 'Attending classes consistently gives you the strongest foundation for understanding key concepts.',
    },
    {
      icon: ICONS.clock,
      title: 'Add regular study time',
      body: 'Even 30 extra minutes of focused revision each day builds lasting mastery and confidence.',
    },
    {
      icon: ICONS.target,
      title: 'Review past feedback',
      body: 'Revisiting previous test questions helps you spot high-value topics to prioritize next.',
    },
  ];

  container.innerHTML = tips
    .map(
      (tip) => `
      <div class="tip-item">
        <div class="tip-icon-wrap" aria-hidden="true">${tip.icon}</div>
        <div class="tip-content">
          <h3 class="tip-title">${tip.title}</h3>
          <p class="tip-body">${tip.body}</p>
        </div>
      </div>
    `
    )
    .join('');
}
