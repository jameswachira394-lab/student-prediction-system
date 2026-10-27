/**
 * Main Application Orchestrator (frontendesign.md Section 13 & 14)
 */

document.addEventListener('DOMContentLoaded', async () => {
  let modelInfo = null;

  // 1. Initialize UI with empty state and static tips
  renderEmptyState();
  renderTips();

  // 2. Fetch model metadata and dynamically build form fields
  try {
    modelInfo = await fetchModelInfo();
    buildForm(modelInfo.fields || []);

    // Render initial influence bars from model info if available
    if (modelInfo.feature_importance) {
      renderInfluenceBars(modelInfo.feature_importance);
    }
  } catch (err) {
    console.error('Failed to initialize model metadata:', err);
  }

  // 3. Form submission handling
  const form = document.getElementById('prediction-form');

  async function handlePredictionSubmit(e) {
    if (e && e.preventDefault) e.preventDefault();

    // Clear previous field errors
    clearFieldErrors();

    // Validate inputs in the browser first
    const validationErrors = validateInputs(modelInfo?.fields);
    if (validationErrors.length > 0) {
      validationErrors.forEach((err) => {
        showFieldError(err.field, err.message);
      });

      // Move keyboard focus to the first invalid field
      const firstInvalidInput = document.getElementById(`${validationErrors[0].field}-number`);
      if (firstInvalidInput) {
        firstInvalidInput.focus();
      }
      return;
    }

    // Inputs are valid; show loading state
    renderLoadingState();

    const values = getFormValues();

    try {
      const result = await postPrediction(values);

      // Render success state
      renderSuccessState(result, modelInfo);

      // Update influence bars if returned by API
      if (result.feature_importance) {
        renderInfluenceBars(result.feature_importance);
      }
    } catch (err) {
      console.error('Prediction request error:', err);

      // If backend returned a 422 validation error
      if (err.status === 422 && err.body?.error?.details) {
        const details = err.body.error.details;
        details.forEach((item) => {
          showFieldError(item.field, `${item.field.replace(/_/g, ' ')} ${item.issue}`);
        });

        // Re-render empty state and restore button
        renderEmptyState();
        restoreSubmitButton();

        if (details[0]?.field) {
          document.getElementById(`${details[0].field}-number`)?.focus();
        }
      } else {
        // Server error or connection failure
        renderErrorState(() => handlePredictionSubmit({ preventDefault: () => {} }));
      }
    }
  }

  if (form) {
    form.addEventListener('submit', handlePredictionSubmit);
  }

  // 4. Mobile navigation menu toggle
  const menuBtn = document.querySelector('.menu-btn');
  const nav = document.querySelector('.nav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', () => {
      const isExpanded = menuBtn.getAttribute('aria-expanded') === 'true';
      menuBtn.setAttribute('aria-expanded', String(!isExpanded));
      nav.classList.toggle('nav-open');
    });

    // Close menu when a navigation link is clicked
    nav.querySelectorAll('.nav-link').forEach((link) => {
      link.addEventListener('click', () => {
        menuBtn.setAttribute('aria-expanded', 'false');
        nav.classList.remove('nav-open');
      });
    });
  }

  // 5. Info Modal Dialogs (How it works & About the model)
  const modalOverlay = document.getElementById('info-modal');
  const modalTitle = document.getElementById('modal-title');
  const modalBody = document.getElementById('modal-body');
  const modalCloseBtn = document.getElementById('modal-close-btn');

  function openModal(title, content) {
    if (!modalOverlay || !modalTitle || !modalBody) return;
    modalTitle.textContent = title;
    modalBody.innerHTML = content;
    modalOverlay.classList.add('open');
    modalCloseBtn?.focus();
  }

  function closeModal() {
    if (modalOverlay) {
      modalOverlay.classList.remove('open');
    }
  }

  if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', closeModal);
  }
  if (modalOverlay) {
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) closeModal();
    });
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalOverlay?.classList.contains('open')) {
      closeModal();
    }
  });

  const howItWorksLink = document.getElementById('link-how-it-works');
  if (howItWorksLink) {
    howItWorksLink.addEventListener('click', (e) => {
      e.preventDefault();
      openModal(
        'How it works',
        `
        <p><strong>1. Enter your study patterns:</strong> Provide your weekly study hours, attendance percentage, and most recent score.</p>
        <br>
        <p><strong>2. Machine Learning estimate:</strong> Our trained regression model analyzes historical student trends to calculate an estimated score.</p>
        <br>
        <p><strong>3. Practical guidance:</strong> Along with your score and grade estimate, you will receive supportive insights highlighting which factors make the biggest positive difference.</p>
      `
      );
    });
  }

  const aboutModelLink = document.getElementById('link-about-model');
  if (aboutModelLink) {
    aboutModelLink.addEventListener('click', (e) => {
      e.preventDefault();
      openModal(
        'About the model',
        `
        <p><strong>Model architecture:</strong> A supervised regression pipeline trained on student performance metrics.</p>
        <br>
        <p><strong>Input factors:</strong> Weekly study hours outside class, course attendance rate, and prior exam results.</p>
        <br>
        <p><strong>Supportive design:</strong> Predictions are statistical estimates designed to empower your learning choices, never to set limitations.</p>
      `
      );
    });
  }
});
