/**
 * Main Application Orchestrator (frontendesign.md Section 13 & 14)
 *
 * NOTE FOR FRONTEND DEVELOPER:
 * This script initializes the application and coordinates:
 * 1. Fetching model metadata on page load -> building form fields.
 * 2. Displaying the initial Empty state.
 * 3. Handling form submission:
 *    a. Validate inputs in the browser first.
 *    b. Show Loading state.
 *    c. Call postPrediction(values).
 *    d. On success -> renderSuccessState(), renderInfluenceBars().
 *    e. On server failure -> renderErrorState(retryHandler).
 * 4. Handling mobile navigation menu toggle.
 */

document.addEventListener('DOMContentLoaded', async () => {
  let modelInfo = null;

  // 1. Initialize UI with empty state and static tips
  renderEmptyState();
  renderTips();

  // 2. Fetch model fields and build dynamic form
  try {
    modelInfo = await fetchModelInfo();
    buildForm(modelInfo.fields || []);
  } catch (err) {
    console.error('Failed to initialize model info:', err);
  }

  // 3. Form submission handler
  const form = document.getElementById('prediction-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Developer:
      // 1. Clear previous errors
      // 2. Validate inputs
      // 3. If invalid -> show errors and focus first invalid field
      // 4. If valid -> showLoadingState(), postPrediction(), renderSuccessState()
    });
  }

  // 4. Mobile menu toggle handler
  const menuBtn = document.querySelector('.menu-btn');
  const nav = document.querySelector('.nav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', () => {
      const isExpanded = menuBtn.getAttribute('aria-expanded') === 'true';
      menuBtn.setAttribute('aria-expanded', String(!isExpanded));
      nav.classList.toggle('nav-open');
    });
  }
});
