# Frontend Design

This file describes how the Student Results Prediction frontend should look and behave. It is the reference for whoever writes the frontend code. The visual mockups live on the design canvas "Student Results Prediction: Frontend Design" (boards: Predict desktop, Predict mobile, Screen states, Style guide). If this file and the mockups ever disagree, agree on the right answer as a team, then update both.

> Status: version 1 design. Values marked **(sample)** are placeholders in the mockups and must come from the API or the team.

## Contents

1. [Principles](#1-principles)
2. [Screens](#2-screens)
3. [Design tokens](#3-design-tokens)
4. [Typography](#4-typography)
5. [Spacing, shape and layout](#5-spacing-shape-and-layout)
6. [Page structure](#6-page-structure)
7. [Components](#7-components)
8. [Responsive behavior](#8-responsive-behavior)
9. [Screen states](#9-screen-states)
10. [Wording](#10-wording)
11. [Accessibility checklist](#11-accessibility-checklist)
12. [How the design connects to the API](#12-how-the-design-connects-to-the-api)
13. [Suggested file structure](#13-suggested-file-structure)
14. [Suggested build order](#14-suggested-build-order)
15. [Open items](#15-open-items)

---

## 1. Principles

- **Supportive, never harsh.** A result is an estimate with a next step, not a verdict. No screen says "you will fail".
- **Plain language.** No jargon. Every number has a unit.
- **One job per screen.** Enter three values, press one button, read one result.
- **Color is never the only signal.** Every risk level has its own icon and its own words.
- **Honest about limits.** The estimate disclaimer is always visible near the result.
- **Works on a phone.** The same content stacks into one column.

## 2. Screens

| Screen | Purpose |
| --- | --- |
| Predict, desktop (1280 px) | Form on the left, result on the right, influence and tips below |
| Predict, mobile (390 px) | The same content in one column |
| Screen states | Empty, loading, validation error, server error |
| Style guide | Colors, type, spacing and components with exact values |

Not designed yet (possible phase 2): prediction history, teacher dashboard, what-if sliders.

## 3. Design tokens

Put these in one file (for example `tokens.css`) and use them everywhere. Never type a hex value in a component.

```css
:root {
  /* Text */
  --ink: #10243E;            /* text and headings */
  --ink-soft: #31445B;       /* secondary text */
  --muted: #55657A;          /* hints and small labels */

  /* Surfaces and lines */
  --ground: #F4F7FA;         /* page background */
  --surface: #FFFFFF;        /* cards and inputs */
  --border: #DDE5EE;         /* card edges and dividers */
  --border-strong: #8A9AAE;  /* input outlines */
  --track: #E6ECF3;          /* empty part of a bar, loading skeleton */
  --tag-bg: #EEF2F7;         /* "Sample data" tag */

  /* Brand */
  --primary: #0B6E78;        /* buttons, bars, sliders */
  --primary-dark: #09595F;   /* hover, pressed, text on the soft tint */
  --primary-soft: #E3F3F5;   /* active nav, icon circles, grade chip */
  --focus: #6DB8C0;          /* keyboard focus ring */

  /* Risk: on track (low) */
  --ontrack-bg: #E6F0FF;
  --ontrack-text: #1A4FA3;
  --ontrack-line: #B9D3FA;

  /* Risk: needs attention (medium) */
  --attention-bg: #FFF1D6;
  --attention-text: #8A4B00;
  --attention-line: #F0D08A;

  /* Risk: ask for support (high) and errors */
  --support-bg: #FDE8E1;
  --support-text: #A3361B;
  --support-line: #F2C2B2;
  --error-field-bg: #FFF8F6;

  /* Score gauge zones */
  --zone-support: #F4C6B8;
  --zone-attention: #F7DB9B;
  --zone-ontrack: #B7D1F5;

  /* Disabled button */
  --disabled-bg: #C9D4DF;

  /* Shape */
  --radius-input: 10px;
  --radius-button: 12px;
  --radius-card: 16px;
  --radius-pill: 999px;
}
```

Text contrast on the surfaces above was chosen to meet 4.5:1 for normal text. If you change a color, check it again.

## 4. Typography

Fonts come from Google Fonts: **Manrope** (headings and numbers) and **Inter** (everything else).

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@700;800&display=swap">
```

Fallback for both: `system-ui, sans-serif`.

| Style | Font | Weight | Size / line height | Used for |
| --- | --- | --- | --- | --- |
| Page title | Manrope | 800 | 44 / 48 (30 / 34 on phones) | The main heading |
| Result number | Manrope | 800 | 80 / 80 (64 on phones) | The predicted score |
| Card heading | Manrope | 700 | 22 / 28 (20 on phones) | Titles of cards |
| Intro | Inter | 400 | 18 / 27 | Paragraph under the page title |
| Body | Inter | 400 | 16 / 24 | Explanations |
| Field label | Inter | 600 | 16 / 24 | Labels above inputs |
| Hint | Inter | 400 | 14 / 20 | Help text under a field |
| Tag | Inter | 600 | 12 / 16 | "Sample data" and the grade caption |
| Eyebrow | Inter | 600 | 14, uppercase, 0.06em spacing | Small line above the page title |

## 5. Spacing, shape and layout

- **Spacing scale (px):** 4, 8, 12, 16, 24, 32, 48. Use only these.
- **Radius:** inputs 10, buttons 12, cards 16, pills and badges 999.
- **Page width:** content is at most 1184 px wide and centered, with 24 px side padding (16 px on phones).
- **Cards:** white surface, 1 px `--border`, 16 px radius, 32 px padding (20 px on phones).
- **Gap between cards:** 32 px (16 px on phones).
- **Touch targets:** every button, input and slider is at least 44 px tall.
- **Focus ring:** `outline: 3px solid var(--focus); outline-offset: 2px` on buttons, links and inputs.

## 6. Page structure

```text
Page
├── Header
│   ├── Logo mark + name "Results Predictor"
│   └── Nav: Predict (active), How it works, About the model
├── Intro: eyebrow, page title, one paragraph
├── Main
│   ├── Row 1
│   │   ├── FormCard: three SliderFields + Predict button
│   │   └── ResultCard: score, grade, risk badge, gauge, explanation, footnote
│   └── Row 2
│       ├── InfluenceCard: three horizontal bars
│       └── TipsCard: three tips + "Explore what-if changes" button
└── Footer: disclaimer, "Student project by [TEAM NAME]"
```

On mobile the header shows a menu button instead of the nav, and every card is full width in one column, in the order: form, result, influence, tips.

## 7. Components

### 7.1 Header

White background, 1 px bottom border. Logo mark is a 36 px rounded square in `--primary` with a white rising line. Nav links are pills (10 px by 18 px padding). The active link has `--primary-soft` background, `--primary-dark` text and weight 600, and carries `aria-current="page"`. On mobile: a 44 px square menu button with `aria-label="Open menu"`.

### 7.2 SliderField

One field per model input. Parts, top to bottom:

1. **Label row:** `<label>` on the left, on the right a number input (72 px wide, 44 px tall, right-aligned, weight 600) and a unit text ("hours" or "%").
2. **Slider:** full width, 44 px tall, `accent-color: var(--primary)`.
3. **Range ticks (desktop only):** minimum on the left, maximum on the right, 13 px, `--muted`.
4. **Hint:** 14 px, `--muted`.

The slider and the number input are always in sync. Min, max and unit for each field come from the API (see section 12), so they are not hard-coded in the markup.

| Field | Unit | Range | Hint text |
| --- | --- | --- | --- |
| Study hours per week | hours | 0 to 80 | Time you spend studying outside class each week. |
| Attendance | % | 0 to 100 | Share of classes you attended this term. |
| Previous score | % | 0 to 100 | Your most recent exam or test result. |

The ranges above are the proposed ones from `DOCUMENTATION.md` and will be finalized by the AI/ML member.

### 7.3 Primary button ("Predict my result")

Full width of the form on mobile, otherwise fills the card width. 52 px minimum height, 12 px radius, `--primary` background, white text, 17 px weight 600, with an arrow icon on the right. Hover and pressed use `--primary-dark`. While waiting it is disabled and shows a spinner (section 9). Under the button on desktop: "Change any value and press the button again."

### 7.4 Secondary button ("Explore what-if changes")

48 px minimum height, white background, 1.5 px `--primary` border, `--primary-dark` text, 12 px radius. This is a stretch feature; hide the button until what-if is built.

### 7.5 ResultCard

Top to bottom:

1. Heading "Your estimate" and a "Sample data" tag (remove the tag when real data is shown).
2. **Score row:** the number (80 px) with a smaller "%" beside it, and the **GradeChip** (68 px square, `--primary-soft` background, caption "Grade" above the letter).
3. **RiskBadge** (below).
4. **ScoreGauge** (below).
5. One-sentence explanation, 17 px.
6. Footnote, pushed to the bottom with a top border: "This is an estimate, not a guarantee." on the left and "Model v1" on the right (the model version comes from the API).

### 7.6 RiskBadge

A pill with an icon and a label. Three variants:

| Risk value from API | Label | Icon | Colors |
| --- | --- | --- | --- |
| `low` | On track | check inside a circle | `--ontrack-*` |
| `medium` | Needs attention | exclamation inside a circle | `--attention-*` |
| `high` | Ask for support | lifebuoy | `--support-*` |

Style: 8 px 16 px 8 px 12 px padding, 1 px border in the `-line` color, 15 px weight 600, 18 px icon.

### 7.7 ScoreGauge

A 14 px tall pill-shaped bar split into three zones, left to right: `--zone-support`, `--zone-attention`, `--zone-ontrack`. The widths come from the model thresholds. The mockup uses 0 to 50, 50 to 65 and 65 to 100, which are **(sample)** thresholds from the metadata example. A marker (24 px circle, white fill, 4 px `--ink` ring) sits at the predicted score, positioned by percentage and centered with a negative margin. Under the bar, a legend lists the three zones with a small colored square, the zone name and its range, for example "On track (65 and up)".

### 7.8 InfluenceCard ("What moves your result most")

Heading, a one-line explanation ("A longer bar means that input has more influence on your estimate."), then three rows. Each row: label (112 px wide), a 14 px track in `--track` with a `--primary` fill whose width is the share in percent, and the percent on the right (weight 600). Sample shares in the mockup are 46, 33 and 21. Rows are sorted from largest to smallest.

### 7.9 TipsCard ("Small changes to try")

A list of three tips. Each has a 40 px circle in `--primary-soft` with an icon in `--primary-dark`, a bold title (16 px) and one sentence (15 px, `--ink-soft`). The sample tips are: keep attendance high, add a little study time, review your last test. In version 1 the tips can be fixed text. Later they can be chosen from the influence data.

### 7.10 Footer

White background, top border. Left: "Predictions are estimates, not guarantees. They come from a limited dataset and may not fit every school or course." Right: "Student project by [TEAM NAME]". Replace `[TEAM NAME]` before the demo.

### 7.11 Tags

"Sample data" is a small pill (12 px, weight 600, `--tag-bg` background, `--ink-soft` text). Show it only while the numbers are not real.

## 8. Responsive behavior

- Use one main breakpoint at **1080 px**. Above it, row 1 has two columns (form about 560 px, result about 440 px) and row 2 has two equal columns. Below it, every card is full width in one column. The style guide mockup says about 1030 px; use 1080 px, because that is where the two columns stop fitting.
- Below 480 px: use the phone sizes in the table in section 4, 20 px card padding, 16 px page padding and 16 px gaps.
- On phones, the nav collapses into the menu button, the slider range ticks are hidden, the gauge legend becomes one item per line, and the buttons are full width.
- Nothing scrolls sideways at any width. Long labels wrap.

## 9. Screen states

The form stays on screen in every state. Only the result area and the button change.

| State | When | What the user sees |
| --- | --- | --- |
| Empty | Before the first prediction | A 64 px icon circle, "Your estimate will appear here", "Fill in the three fields, then press Predict my result." |
| Loading | After pressing the button, until the API answers | Spinner and "Working out your estimate", gray placeholder blocks where the score, grade, badge and bar will go, the button disabled and labeled "Predicting your result". Mark the area `aria-busy="true"` and announce with `role="status"`. |
| Validation error | A value is empty or out of range | The field gets a 2 px `--support-text` border and `--error-field-bg` fill, with a message below it (alert icon, 14 px, weight 600) such as "Attendance must be between 0 and 100." The message is linked with `aria-describedby`, the input has `aria-invalid="true"`, and focus moves to the first invalid field. Other values are kept. |
| Server error | The API fails or does not answer | A 64 px circle with a warning icon in `--support-bg`, "We could not get your estimate", "The prediction service is not answering right now. Your answers are still in the form, so you can try again in a moment.", and a "Try again" button. |
| Success | The API returns a result | The ResultCard from section 7.5. Move focus to the result heading, or announce it politely, so keyboard and screen reader users know it changed. |

Validation happens in the browser first. The API validates again and returns the shared error shape from `DOCUMENTATION.md` (section 7.2), whose `details[].field` and `issue` can be shown under the matching field.

## 10. Wording

| Place | Text |
| --- | --- |
| App name | Results Predictor |
| Eyebrow | Your results estimate |
| Page title | See where your results are heading |
| Intro | Tell us a little about how you study. We will estimate your result and suggest small changes that could help. |
| Form title | Your study habits |
| Form hint | Move a slider or type a number. All three are needed. |
| Main button | Predict my result |
| Result title | Your estimate |
| Risk meanings | On track · Needs attention · Ask for support |
| Influence title | What moves your result most |
| Tips title | Small changes to try |
| Disclaimer | Predictions are estimates, not guarantees. They come from a limited dataset and may not fit every school or course. |

Rules: use "we" and "you", keep sentences short, never use the words "fail", "weak" or "bad" about a student.

## 11. Accessibility checklist

- [ ] Every input has a visible `<label>` linked with `for` and `id`. Each slider has an `aria-label`.
- [ ] Everything works with the keyboard: Tab order follows the visual order, and the focus ring is visible.
- [ ] Use real `<button>`, `<a>`, `<input>` and `<form>` elements. Do not put click handlers on `<div>` or `<span>`.
- [ ] Icons that decorate have `aria-hidden="true"`. Icon-only buttons have an `aria-label`.
- [ ] Error messages use `role="alert"` and are linked to their field.
- [ ] Loading and result changes are announced (`role="status"` or `aria-live="polite"`).
- [ ] Text contrast is at least 4.5:1 (3:1 for text 24 px and larger).
- [ ] Meaning is never carried by color alone: risk badges have icons and words, gauge zones have a legend.
- [ ] The page works zoomed to 200% and at 320 px wide.
- [ ] Set `<html lang="en">` and a page `<title>`.

## 12. How the design connects to the API

The frontend calls the results service through the gateway with a relative path. Fields and shapes come from `DOCUMENTATION.md` section 5.

**Request:** `POST /api/predictions`

```json
{ "study_hours": 12, "attendance": 85, "previous_score": 64 }
```

**Response:**

```json
{ "predicted_score": 72.4, "grade": "B", "risk": "low", "model_version": "v1" }
```

| API field | Shown as |
| --- | --- |
| `predicted_score` | The big number and the gauge marker position |
| `grade` | The letter in the GradeChip |
| `risk` | The RiskBadge variant (`low`, `medium`, `high`) |
| `model_version` | "Model v1" in the result footnote |

**Form fields from the model:** `GET /api/model-info` should return each input with its label, unit, minimum and maximum, so the form can be built from it and the ranges are not written twice. Until the API is ready, use a mock object in the frontend with the same shape.

**Not in the current contract (ask AI/ML and DevOps):**

- **Gauge thresholds** (the 50 and 65 in the mockup): needed to draw the zones. Proposal: include them in `GET /api/model-info`.
- **Feature importance** (the three bars): needed for the InfluenceCard. Proposal: add an optional `feature_importance` object to the prediction response, for example `{ "attendance": 0.46, "study_hours": 0.33, "previous_score": 0.21 }`. If it is missing, hide the card.
- **One-sentence explanation:** in version 1 the frontend can build it from `risk` and the most important input. Keep the wording supportive.

Use a setting for the API base path (`/api` by default), never hard-coded across files.

## 13. Suggested file structure

This assumes plain HTML, CSS and JavaScript. If the team picks a framework, keep the same split into tokens, components and an API module.

```text
frontend/
├── src/
│   ├── index.html
│   ├── styles/
│   │   ├── tokens.css       # section 3
│   │   ├── base.css         # reset, fonts, page layout, focus ring
│   │   └── components.css   # buttons, fields, cards, badges, gauge, bars
│   └── js/
│       ├── config.js        # API base path
│       ├── api.js           # fetch wrappers for /api/predictions and /api/model-info
│       ├── form.js          # sync slider and number input, validation
│       ├── render.js        # show empty, loading, success and error states
│       └── main.js          # wires everything together
├── Dockerfile
└── nginx.conf
```

## 14. Suggested build order

1. **Static page.** Build the desktop layout in plain HTML and CSS with the sample values. Add `tokens.css` first.
2. **Make it responsive** with the 1080 px breakpoint and the phone sizes.
3. **Form behavior.** Sync each slider with its number input, and validate ranges in the browser.
4. **Call the mock API.** Send the form values and fill in the ResultCard from the response.
5. **States.** Add empty, loading, validation error and server error.
6. **Accessibility pass** with section 11.
7. **Switch to the real API** when the model service is ready.
8. **Extras, if time allows:** influence bars, tips from the influence data, what-if sliders, prediction history chart, teacher view.

## 15. Open items

- App name: "Results Predictor" is a working name.
- `[TEAM NAME]` in the footer.
- Final input fields, units and ranges (AI/ML).
- Gauge thresholds and whether the API exposes them (AI/ML, DevOps).
- Whether the API returns feature importance in version 1 (AI/ML, DevOps).
- Frontend approach: plain JavaScript or a framework (Frontend).
- Decision on the what-if sliders, history chart and teacher view (whole team).