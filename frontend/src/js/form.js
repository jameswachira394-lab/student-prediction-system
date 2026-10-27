/**
 * Form Handling & Validation Module (frontendesign.md Section 7.2 & 9)
 */

let activeFields = [];

// Proposed default starter values matching the mockups and smoke tests
const DEFAULT_VALUES = {
  study_hours: 12,
  attendance: 85,
  previous_score: 64,
};

/**
 * Dynamically builds form slider fields inside #fields-container
 * @param {Array<Object>} fields Array of field descriptors from model info
 */
function buildForm(fields) {
  const container = document.getElementById('fields-container');
  if (!container) return;

  activeFields = fields || [];
  container.innerHTML = '';

  activeFields.forEach((field) => {
    const fieldId = field.name;
    const initialVal =
      DEFAULT_VALUES[fieldId] !== undefined
        ? DEFAULT_VALUES[fieldId]
        : Math.round((field.min + field.max) / 2);

    const fieldGroup = document.createElement('div');
    fieldGroup.className = 'slider-field';
    fieldGroup.id = `field-group-${fieldId}`;

    fieldGroup.innerHTML = `
      <div class="field-header">
        <label for="${fieldId}-number" id="${fieldId}-label" class="field-label">${field.label}</label>
        <div class="field-input-wrap">
          <input
            type="number"
            id="${fieldId}-number"
            name="${fieldId}"
            class="number-input"
            min="${field.min}"
            max="${field.max}"
            value="${initialVal}"
            aria-describedby="${fieldId}-hint"
            autocomplete="off"
          />
          <span class="field-unit" aria-hidden="true">${field.unit}</span>
        </div>
      </div>

      <input
        type="range"
        id="${fieldId}-slider"
        class="field-slider"
        min="${field.min}"
        max="${field.max}"
        step="1"
        value="${initialVal}"
        aria-label="${field.label}"
      />

      <div class="field-ticks" aria-hidden="true">
        <span>${field.min}</span>
        <span>${field.max} ${field.unit}</span>
      </div>

      <p id="${fieldId}-hint" class="field-hint">${field.hint}</p>

      <div id="${fieldId}-error" class="field-error-msg" role="alert" style="display: none;"></div>
    `;

    container.appendChild(fieldGroup);

    // Wire bidirectional synchronization between slider and number input
    const numberInput = fieldGroup.querySelector(`#${fieldId}-number`);
    const sliderInput = fieldGroup.querySelector(`#${fieldId}-slider`);

    sliderInput.addEventListener('input', () => {
      numberInput.value = sliderInput.value;
      clearSingleFieldError(fieldId);
    });

    numberInput.addEventListener('input', () => {
      const val = parseFloat(numberInput.value);
      if (!isNaN(val)) {
        sliderInput.value = val;
      }
      clearSingleFieldError(fieldId);
    });
  });
}

/**
 * Collects current numeric values from form fields
 * @returns {Object} Object with field names as keys and numbers as values
 */
function getFormValues() {
  const values = {};
  activeFields.forEach((field) => {
    const input = document.getElementById(`${field.name}-number`);
    if (input) {
      values[field.name] = input.value === '' ? NaN : parseFloat(input.value);
    }
  });
  return values;
}

/**
 * Validates inputs against min/max ranges
 * @param {Array<Object>} [fields] Optional override of field descriptors
 * @returns {Array<Object>} List of validation errors, if any
 */
function validateInputs(fields) {
  const fieldsToValidate = fields || activeFields;
  const errors = [];

  fieldsToValidate.forEach((field) => {
    const input = document.getElementById(`${field.name}-number`);
    if (!input) return;

    const rawVal = input.value.trim();
    if (rawVal === '') {
      errors.push({
        field: field.name,
        message: `Please enter a value for ${field.label.toLowerCase()}.`,
      });
      return;
    }

    const val = Number(rawVal);
    if (isNaN(val)) {
      errors.push({
        field: field.name,
        message: `${field.label} must be a valid number.`,
      });
      return;
    }

    if (val < field.min || val > field.max) {
      errors.push({
        field: field.name,
        message: `${field.label} must be between ${field.min} and ${field.max}.`,
      });
    }
  });

  return errors;
}

/**
 * Highlights a field that failed validation
 * @param {string} fieldName
 * @param {string} message
 */
function showFieldError(fieldName, message) {
  const group = document.getElementById(`field-group-${fieldName}`);
  const input = document.getElementById(`${fieldName}-number`);
  const slider = document.getElementById(`${fieldName}-slider`);
  const errorEl = document.getElementById(`${fieldName}-error`);

  if (group) group.classList.add('has-error');

  if (input) {
    input.setAttribute('aria-invalid', 'true');
    input.setAttribute('aria-describedby', `${fieldName}-error ${fieldName}-hint`);
  }
  if (slider) {
    slider.setAttribute('aria-invalid', 'true');
  }

  if (errorEl) {
    errorEl.style.display = 'flex';
    errorEl.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.8"/>
        <line x1="8" y1="4.5" x2="8" y2="8.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <circle cx="8" cy="11.5" r="0.9" fill="currentColor"/>
      </svg>
      <span>${message}</span>
    `;
  }
}

/**
 * Clears error highlight for a single field
 * @param {string} fieldName
 */
function clearSingleFieldError(fieldName) {
  const group = document.getElementById(`field-group-${fieldName}`);
  const input = document.getElementById(`${fieldName}-number`);
  const slider = document.getElementById(`${fieldName}-slider`);
  const errorEl = document.getElementById(`${fieldName}-error`);

  if (group) group.classList.remove('has-error');
  if (input) {
    input.removeAttribute('aria-invalid');
    input.setAttribute('aria-describedby', `${fieldName}-hint`);
  }
  if (slider) slider.removeAttribute('aria-invalid');
  if (errorEl) {
    errorEl.style.display = 'none';
    errorEl.innerHTML = '';
  }
}

/**
 * Clears all validation error highlights and messages
 */
function clearFieldErrors() {
  activeFields.forEach((field) => clearSingleFieldError(field.name));
}
