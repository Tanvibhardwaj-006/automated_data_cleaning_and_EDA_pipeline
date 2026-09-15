# Automated Data Cleaning + EDA Pipeline

A reusable Python pipeline that profiles, cleans, and generates an exploratory data analysis (EDA) report for any messy CSV dataset — built to work on unseen data, not tuned to one file.

> **Status: in progress.** This README reflects the project as currently built and will be updated as new phases are completed.

## Why this project exists

Most "data cleaning" scripts are one-off notebooks tuned to a single file — they work by coincidence, not by design. This project is built as a **generalizable tool**: every cleaning decision is rule-based (not hardcoded to one dataset), every action is logged (so the cleaning process is auditable, not a black box), and the pipeline is tested against two structurally different datasets to prove it actually generalizes rather than just happening to work once.

## Datasets used

Two deliberately different datasets, chosen to stress-test different parts of the pipeline:

| Dataset | Type | Why it was chosen |
|---|---|---|
| `olist_orders_dataset.csv` | Real-world messy data | Tests date-logic validity checks (5 timestamp columns) and key-integrity checks (`order_id` as primary key) |
| Retail Store Sales (dirty) | Real-world messy data | Tests numeric fill/derivation logic (`Total = Quantity × Price`) and categorical/boolean fill logic |

A third, self-corrupted dataset (clean data with manually injected nulls, duplicates, and inconsistent formatting) is used specifically to verify the uniqueness/duplicate-detection logic against known ground truth, since neither real-world dataset contains duplicate rows naturally.

## Design: the cleaning ruleset

Every check the pipeline performs is mapped to one of four data-quality pillars (completeness, uniqueness, validity, consistency) — no ad hoc fixes, every rule decided up front before any code was written.

**Completeness**
- Detect nulls (NaN, None, empty string) per column, calculate % missing
- Column 100% null → drop, log it
- Column >40% null → flag for manual review, do not auto-fill
- Numeric column, ≤90% unique values → derive from related columns where a formula exists (e.g. `Total = Quantity × Price`), else fill with median
- Numeric column, >90% unique values → treat as an identifier (e.g. ID/code), skip auto-fill, flag instead
- Boolean-like column → fill with the semantically correct default, reasoning logged explicitly
- Categorical column → fill with `"unknown"`

**Uniqueness**
- Fully duplicate rows → drop, log count removed
- Semi-duplicate rows (same user-specified key column, differing other values) → flag only, never auto-dropped

**Validity**
- Wrong dtypes (e.g. dates stored as text) → coerce to correct type, log conversion failures
- Out-of-range numeric values → flag, never auto-deleted
- Faulty/illogical dates → flag, never auto-deleted

**Consistency**
- Whitespace, punctuation, and inconsistent casing in text columns → normalized

## Project structure

```
retail project/
├── data/
│   └── raw/              # source CSVs (not committed if large/licensed)
├── notebooks/             # exploratory/throwaway analysis only
├── src/
│   ├── profiler.py         # "before" snapshot: row count, null %, dtypes, duplicates
│   └── cleaner.py           # cleaning logic + change log, per the ruleset above
├── tests/
│   └── test_cleaner.py       # unit tests against hand-built data with known ground truth
├── reports/                  # generated EDA reports (Phase 4)
├── requirements.txt
└── README.md
```

## How it works

1. **Profile** — `profiler.py` loads a raw CSV and captures a structured "before" snapshot (row/column counts, null counts and percentages, duplicate row count, dtypes) without modifying anything.
2. **Clean** — `cleaner.py` applies the ruleset above, function by function, appending a human-readable line to a running log for every action taken (e.g. *"Dropped 42 duplicate rows"*, *"Flagged 12 semi-duplicate rows on order_id"*). Nothing is silently changed.
3. **Report** *(planned)* — generate an automated EDA report (`ydata-profiling`) on the cleaned data.
4. **Wrap as a tool** *(planned)* — accept any CSV path as a command-line argument, rather than being hardcoded to one file.

## Tech stack

- Python 3.13
- pandas, numpy
- ydata-profiling *(planned, for EDA report generation)*
- pytest-style manual assertions for testing (see `tests/`)

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Mac/Linux

pip install -r requirements.txt
```

## Progress

- [x] Design: fixed ruleset across 4 data-quality pillars
- [x] `profiler.py` — before-snapshot profiling, verified against manual null counts
- [x] `cleaner.py` — duplicate detection (`drop_full_duplicates`, `flag_semi_duplicates`), unit-tested
- [ ] `cleaner.py` — missing value handling (`handle_missing_values`)
- [ ] `cleaner.py` — dtype correction, validity flags, text normalization
- [ ] Self-corrupted dataset for ground-truth testing of uniqueness logic
- [ ] Automated EDA report generation
- [ ] CLI wrapper (`--input` / `--output` arguments)