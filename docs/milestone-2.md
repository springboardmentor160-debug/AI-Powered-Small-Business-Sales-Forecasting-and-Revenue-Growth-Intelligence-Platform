# MarketMindAI --- Milestone 2 Evidence

**Project:** MarketMindAI --- Small Business Sales Intelligence
Platform\
**Author:** Aditya Pandya\
**Program:** Infosys-Springboard Internship\
**Milestone:** Milestone 2 --- Analytics Expansion and React Frontend\
**Document status:** Working evidence record; update as remaining
evidence is captured

------------------------------------------------------------------------

## 1. Milestone Overview

Milestone 2 extends the foundation documented in Milestone 1. The work
recorded so far focuses on expanding the analytics experience, improving
data and forecast handling, and presenting the application through the
React frontend.

The current Milestone 2 work includes:

-   React login and dashboard interfaces
-   Sales and forecast visualizations
-   Inventory preview, refresh, and JSON export
-   Invoice registry, invoice creation, and CSV export
-   Customer segmentation interface
-   Administrative user view
-   Continued backend API and data-quality validation
-   Automated test evidence for selected backend areas

This document records the evidence known to have been captured and the
tests reported as passing. It does not claim that every Milestone 2
requirement, integration, or production-readiness task is complete.

------------------------------------------------------------------------

## 2. Relationship to Milestone 1

Milestone 1 established the initial MarketMindAI foundation, including
the UCI Online Retail II transaction data, the FastAPI backend,
authentication and role-based access control, initial sales analytics, a
forecast prototype, and invoice workflows.

Milestone 2 builds on that foundation rather than replacing the original
Milestone 1 evidence. The React frontend screenshots are recorded
separately, and the existing Milestone 1 documentation and screenshots
should be retained.

The Milestone 1 document notes that inventory derived from sales is an
estimate, not verified physical warehouse stock. That distinction should
continue to be made wherever inventory preview values are presented.

------------------------------------------------------------------------

## 3. Milestone 2 Scope and Evidence Status

  -------------------------------------------------------------------------------
  Area                    Milestone 2 work/evidence      Current record
  ----------------------- ------------------------------ ------------------------
  React login             Login interface screenshot     Captured; see M2-E01

  React dashboard         Dashboard screenshot           Captured; see M2-E02

  Sales analytics         React sales analytics and KPI  Feature work reported;
                          presentation                   capture dedicated
                                                         screenshot if not
                                                         already recorded

  Forecasting             Forecast charts and            Feature/test work
                          forecast-persistence-related   reported; capture
                          backend tests                  current UI and retain
                                                         test output

  Inventory               Inventory preview, refresh,    Feature work reported;
                          and JSON export                capture preview and
                                                         export evidence

  Invoices                Invoice registry, create       Feature work reported;
                          workflow, and CSV export       capture
                                                         registry/create/export
                                                         evidence

  Customer segmentation   Segmentation interface         Feature work reported;
                                                         capture interface and
                                                         representative output

  Admin users             Administrative user interface  Feature work reported;
                                                         capture role-authorized
                                                         view

  Backend quality         Data-quality and dataset tests Passing test results
                                                         reported; retain
                                                         terminal output or CI
                                                         report

  Build                   React production build         `npm run build` reported
                                                         passing, with a
                                                         large-chunk warning
  -------------------------------------------------------------------------------

**Status interpretation:** "Reported" refers to results shared during
project work. Re-run commands and capture current outputs before
treating them as final submission evidence.

------------------------------------------------------------------------

## 4. Milestone 2 Screenshot Evidence

Screenshots are stored in `docs/screenshots/`.

### M2-E01 --- React Login Page

**File:** `docs/screenshots/09-M2-React-Login.png`

**Objective:** Record the React application's login interface before the
authenticated dashboard.

**Verification recorded:** The file was listed by PowerShell and had a
non-zero size of 105,149 bytes.

**Status:** Captured; file existence and size verified.

### M2-E02 --- React Dashboard

**File:** `docs/screenshots/10-M2-React-Dashboard.png`

**Objective:** Record the React dashboard interface after login.

**Verification recorded:** The file was listed by PowerShell and had a
non-zero size of 362,031 bytes.

**Status:** Captured; file existence and size verified.

### Additional Screenshots to Capture or Confirm

Use descriptive filenames and keep all screenshots under
`docs/screenshots/`.

  ------------------------------------------------------------------------------------
  Suggested evidence ID   Suggested filename                   What it should
                                                               demonstrate
  ----------------------- ------------------------------------ -----------------------
  M2-E03                  `11-M2-React-Sales-Analytics.png`    Sales analytics page
                                                               and visible KPIs/charts

  M2-E04                  `12-M2-React-Forecast.png`           Forecast visualization
                                                               and selected forecast
                                                               context

  M2-E05                  `13-M2-React-Inventory.png`          Inventory preview and
                                                               refresh result

  M2-E06                  `14-M2-React-Invoice-Registry.png`   Invoice registry/list

  M2-E07                  `15-M2-React-Invoice-Create.png`     Invoice creation
                                                               workflow and validation

  M2-E08                  `16-M2-React-Segmentation.png`       Customer segmentation
                                                               interface/results

  M2-E09                  `17-M2-React-Admin.png`              Administrative user
                                                               view

  M2-E10                  `18-M2-React-Export-Evidence.png`    Relevant JSON/CSV
                                                               export result, if it
                                                               can be shown safely

------------------------------------------------------------------------

## 5. React Frontend

The React application is located at:

`frontend/react-app`

The following functionality has been reported during implementation:

-   Login page and authenticated dashboard flow
-   Sales analytics and forecast charts
-   Inventory preview with refresh and JSON export
-   Invoice registry and invoice creation with CSV export
-   Customer segmentation interface
-   Administrative user interface

A production build was reported to pass using `npm run build`. A
large-chunk warning was also reported. The warning should be documented
as a build optimization item rather than represented as a failed build.

### Frontend Validation Checklist

-   [x] Confirm login with valid credentials.
-   [x] Confirm invalid login is handled safely.
-   [X] Confirm successful login reaches the dashboard.
-   [x] Refresh the dashboard and verify the user is not unexpectedly
    redirected to login.
-   [x] Confirm logout returns the user to the unauthenticated state.
-   [x] Confirm protected pages and actions enforce the expected
    permissions.
-   [x] Confirm each analytics page loads data and presents empty/error
    states clearly.
-   [x] Confirm export actions generate the intended file.
-   [x] Capture screenshots for the completed flows.

Mark each item only after running it against the current application.

------------------------------------------------------------------------

## 6. Backend and Data Validation

Milestone 1 documented a FastAPI backend and CSV-based UCI Online Retail
II workflow. Milestone 2 continues backend validation and adds or
expands analytics-related behavior.

The following backend test results were reported during project work:

  Test area                                    Reported result
  ------------------------------------------ -----------------
  `tests/test_auth.py`                               19 passed
  `tests/test_authorization.py`                      48 passed
  `tests/test_api_health.py`                          2 passed
  `tests/test_uci_forecast_persistence.py`            3 passed
  `tests/test_m5_quality.py`                          8 passed
  `tests/test_m5_dataset.py`                         16 passed
  `tests/test_phase4_schema.py`                       4 passed

These are previously reported results, not a fresh test run performed
while generating this document. Re-run the relevant test suite and
preserve the terminal output before submission. A passing test file does
not by itself prove that all application workflows are correct.

### Suggested verification commands

Run from the repository root in the activated virtual environment.
Adjust the command only if the repository's test configuration requires
it.

``` powershell
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_authorization.py -v
python -m pytest tests/test_api_health.py -v
python -m pytest tests/test_uci_forecast_persistence.py -v
python -m pytest tests/test_m5_quality.py -v
python -m pytest tests/test_m5_dataset.py -v
python -m pytest tests/test_phase4_schema.py -v
```

For the React frontend:

``` powershell
Set-Location .\frontend\react-app
npm run build
```

Capture fresh output or save it to the project's evidence folder. Do not
include environment secrets in evidence.

------------------------------------------------------------------------

## 7. Data and Analytics Notes

### UCI Online Retail II

Milestone 1 identifies UCI Online Retail II as the original retail
transaction dataset. Its identifiers and descriptions should retain
their original meaning and provenance.

### Walmart M5 Data

Milestone 1 planned Walmart M5 data expansion as part of subsequent
work. M5 data should be documented as a distinct source with its own
identifiers and provenance. Do not assume that M5 identifiers directly
correspond to UCI identifiers without a validated mapping.

### Inventory

Where inventory is estimated from sales-derived calculations, label it
as estimated inventory. Do not describe derived estimates as observed
warehouse stock unless independently verified inventory records support
that claim.

### Forecasting

Milestone 1 described forecasting as a prototype requiring validation.
Although Milestone 2 includes expanded forecast UI and
persistence-related tests, production accuracy should not be claimed
without appropriate evaluation, baseline comparison, and documented
metrics.

### Exports

The inventory JSON export and invoice CSV export should be verified by
opening the generated files and checking their structure and contents.
Capture evidence of successful exports without exposing private business
or user data.

------------------------------------------------------------------------

## 8. Authentication and Authorization

Milestone 1 documented JWT-based authentication, password hashing, and
role-based access control. Milestone 2 should preserve these security
boundaries as the frontend changes.

Validation should confirm:

-   Authentication is handled by the backend, not only by hiding
    frontend elements.
-   Protected API requests require appropriate authentication.
-   Role restrictions are enforced by backend authorization checks.
-   Logout clears the client-side authenticated state appropriately.
-   Secrets and access tokens are not embedded in screenshots, committed
    code, or public evidence.
-   User-facing errors do not disclose sensitive implementation details.

The reported passing authentication and authorization test suites are
supporting evidence, but should be rerun before final submission.

------------------------------------------------------------------------

## 9. Known Build and Completion Notes

-   The React production build was reported as successful.
-   A large JavaScript chunk warning was reported; consider code
    splitting or lazy loading as a follow-up optimization.
-   Login and dashboard screenshots have been captured and their file
    sizes verified.
-   Additional feature screenshots and current test outputs should be
    added as the corresponding flows are revalidated.
-   The final Milestone 2 completion status should be decided against
    the official internship milestone requirements, not from screenshot
    availability alone.

------------------------------------------------------------------------

## 10. Repository Evidence Layout

Expected documentation and evidence layout:

``` text
marketmindai/
├── docs/
│   ├── milestone-1.md
│   ├── milestone-2-evidence.md
│   ├── architecture/
│   │   └── architecture.md
│   └── screenshots/
│       ├── 01-Login.png
│       ├── 02-Dashboard.png
│       ├── ...
│       ├── 09-M2-React-Login.png
│       └── 10-M2-React-Dashboard.png
└── frontend/
    └── react-app/
```

This is an illustrative layout. Preserve the actual repository files and
paths if they differ. The existing Milestone 1 document and screenshots
should not be overwritten by Milestone 2 evidence.

------------------------------------------------------------------------

## 11. React Frontend Screenshot Evidence — Updated

All screenshot paths below are relative to `docs/`.

| Evidence ID | Screenshot | Recorded status |
|---|---|---|
| M2-E01 | `screenshots/09-M2-React-Login.png` | File verified |
| M2-E02 | `screenshots/10-M2-React-Dashboard.png` | File verified |
| M2-E03 | `screenshots/11-M2-React-Sales-Analytics.png` | File verified |
| M2-E04 | `screenshots/12-M2-React-Forecast.png` | File verified |
| M2-E05 | `screenshots/13-M2-React-Inventory.png` | File verified |
| M2-E06 | `screenshots/14-M2-React-Invoice-Registry.png` | File verified |
| M2-E07 | `screenshots/15-M2-React-Invoice-Create.png` | File verified |
| M2-E08 | `screenshots/16-M2-React-Segmentation.png` | File verified |
| M2-E09 | `screenshots/17-M2-React-Admin.png` | File verified |

**Verification note:** PowerShell confirmed that all nine screenshot files exist and have non-zero file sizes. This confirms file presence, not independent visual validation or successful end-to-end functionality.

------------------------------------------------------------------------

## 12. Final Milestone 2 Evidence Checklist

| Evidence item | Recorded result | Limitation |
|---|---|---|
| React screenshots | Nine screenshot files verified | File presence does not confirm visual correctness |
| Backend automated tests | 100 passed across eight selected test files | Not a full-repository test run |
| React production build | Successful | Large JavaScript chunk warning remains |
| Inventory JSON export | JSON parsing passed; 6,891 product records | Stock values are estimates |
| Invoice CSV export | CSV parsing passed; 2 data rows and 9 columns | Validation does not prove completeness of all records |

### Final Review Before Submission

- Review each screenshot to confirm it shows the intended page.
- Check that screenshots and exports do not expose passwords, tokens, secret keys, or unnecessary personal information.
- Preserve the detailed test and build output if required by the submission criteria.
- Compare the implemented features and evidence against the official Milestone 2 requirements.
- Record any incomplete requirements honestly; do not describe unverified workflows as fully tested.

This checklist summarizes the validation evidence recorded in this document. It is not a claim that every Milestone 2 requirement has been completed.

---

## 13. Technical Validation Evidence -

### 13.1 Backend Automated Tests

Two backend test runs completed successfully.

| Test group | Result |
|---|---:|
| Authentication, authorization, API health | 69 passed |
| Forecast persistence, M5 quality, M5 dataset, schema validation | 31 passed |
| Total across both runs | 100 passed |

The reported combined result is 100 passing tests across the eight selected test files. These results do not establish that every test in the repository has been executed.

### 13.2 React Production Build

**Command:** `npm run build`

**Result:** Successful

- TypeScript build: completed
- Vite version: 8.3.4
- Modules transformed: 2,487
- Build time: 1.57 seconds
- Main JavaScript bundle: 655.31 kB minified
- Main JavaScript bundle: 191.41 kB gzip

**Warning:** Vite reported that some chunks exceed 500 kB after minification. This is a build optimization warning, not a build failure. Code splitting or lazy loading may be evaluated as a future optimization.

### 13.3 Evidence Limitations

These results record the terminal summaries shared during validation. Preserve the detailed terminal output for submission where required. Automated tests and a successful production build support technical validation, but do not independently establish that every end-to-end user workflow or production deployment requirement is satisfied.

---

## 14. Export Workflow Validation —

### 14.1 Inventory JSON Export

**File:** `marketmind-inventory-preview.json`
**Location:** Windows Downloads folder

| Validation | Result |
|---|---|
| File exists and has non-zero size | Pass |
| JSON parsing | Pass |
| Top-level structure | Object |
| Source files listed | 2 |
| Product records | 6,891 |
| Inventory totals and method fields | Present |

The export includes product records, source-file information, inventory-method metadata, and estimated stock totals.

Inventory figures derived from sales must continue to be labelled as estimates rather than verified physical warehouse stock.

### 14.2 Invoice CSV Export

**File:** `marketmind-invoices.csv`
**Location:** Windows Downloads folder

| Validation | Result |
|---|---|
| File exists and has non-zero size | Pass |
| CSV parsing | Pass |
| Data rows | 2 |
| Columns | 9 |
| Invoice fields | Present |

The CSV contains invoice identifiers, customer and product fields, quantities, pricing, payment status, creator, and creation timestamp.

A sample record was inspected, and its quantity, unit price, and total amount were arithmetically consistent.

**Privacy note:** Exported invoice data can contain customer names and account emails. Do not include actual personal information in publicly shared evidence.

### 14.3 Validation Limitations

These checks establish that the downloaded exports are readable and contain structured data. They do not independently prove that every record is correct, that the export includes every expected record, or that all edge cases are handled.

---

## 15. Final Assessment

The evidence recorded here shows that the React login and dashboard
screenshots have been captured, and that a range of React functionality
and backend tests were reported during Milestone 2 development. The
reported frontend build passed with a large-chunk warning.

This document is a working evidence record, not a declaration that every
Milestone 2 requirement is complete. Final status should be assigned
only after the remaining feature workflows, test results, exports, and
official milestone criteria have been verified.

___

## Author

**Aditya Pandya**\
Infosys-Springboard Internship Project\
**MarketMindAI --- Small Business Sales Intelligence Platform**

---
