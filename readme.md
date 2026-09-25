# Automated Data Cleaning + EDA Pipeline

A reusable Python pipeline that profiles, cleans, and (soon) generates an exploratory data analysis (EDA) report for any messy CSV dataset — built to work on unseen data, not tuned to one file.

> **Status: core cleaning pipeline complete and tested. EDA report generation and CLI wrapper still in progress.**

## Why this project exists

Most "data cleaning" scripts are one-off notebooks tuned to a single file — they work by coincidence, not by design. This project is built as a **generalizable tool**: cleaning decisions are driven by the *shape* of the data (value cardinality, uniqueness ratio, parse success rate) rather than hardcoded column names wherever possible, every action is logged with its reasoning, and the pipeline is verified against two structurally different datasets to prove it actually generalizes.

## Datasets used

| Dataset | Role |
|---|---|
| `olist_orders_dataset.csv` | Real-world messy data — tests date-sequence validity checks and key-integrity checks |
| Retail Store Sales (dirty) | Real-world messy data — tests numeric derivation/fill logic and boolean/categorical fill logic |

Both datasets run through the same pipeline code, with no per-dataset branching except where explicitly noted below.

## The cleaning ruleset

**Completeness**
- Null detection and % calculation per column
- Column 100% null → dropped, logged
- Column >40% null → flagged for manual review, not auto-filled
- Numeric column, ≤90% unique values → median fill; >90% unique → treated as an identifier, flagged instead
- Boolean-like columns (detected generically by having exactly 2 unique non-null values) → filled with a semantically correct default, reasoning logged
- Categorical columns → filled with `"Unknown"`
- Datetime columns → missing values (NaT) are left unfilled; missingness is treated as meaningful (e.g. an order that never reached a delivery stage), not as a gap to guess at
- **Derivation pre-pass** (dataset-specific): where a mathematical relationship exists between columns (e.g. `Total = Quantity × Price`), a missing value is recovered by calculation instead of estimated by median, whenever exactly one of the three values is missing in a row

**Uniqueness**
- Fully duplicate rows → dropped, count logged
- Semi-duplicate rows (same user-specified key column, differing other values) → flagged only, never auto-dropped

**Validity**
- Column dtypes are corrected generically: any text column is sample-tested for date-like values and converted to real `datetime` type if a high proportion of values parse successfully — no column names hardcoded
- Faulty/illogical date sequences (e.g. a delivery date earlier than the purchase date) are flagged — this check currently targets Olist's specific delivery-chain columns and explicitly logs when it doesn't apply to a dataset, rather than failing silently

**Consistency**
- Text columns are normalized (whitespace stripped, case lowercased, edge punctuation stripped) — columns with a high uniqueness ratio are skipped and treated as identifiers to avoid corrupting IDs

## Project structure

```
retail project/
├── data/
│   └── raw/
├── notebooks/             # exploratory/throwaway analysis
├── src/
│   ├── profiler.py         # "before" snapshot: row/col counts, null %, dtypes, duplicates
│   └── cleaner.py           # all cleaning functions + orchestrator
├── tests/
│   └── test_cleaner.py       # unit tests for every function, verified against known ground truth
├── reports/                  # generated EDA reports (in progress)
├── requirements.txt
└── README.md
```

## How it works

1. **Profile** (`profiler.py`) — captures a structured "before" snapshot of any raw CSV without modifying it: row/column counts, null counts and percentages, duplicate row count, dtypes.
2. **Clean** (`cleaner.py` → `clean_dataset()`) — runs the full pipeline in a fixed, dependency-aware order:
   `drop_full_duplicates → flag_semi_duplicates → fix_dtypes → derive_missing_values → handle_missing_values → flag_faulty_dates → normalize_text_columns`
   Every step appends a human-readable entry to a shared log — nothing changes silently.
3. **Report** *(in progress)* — automated EDA report on the cleaned data via `ydata-profiling`.
4. **CLI wrapper** *(in progress)* — accept any CSV path as a command-line argument instead of hardcoded file paths.

## Engineering notes worth highlighting

- **Detection over hardcoding, wherever feasible.** Boolean columns, identifier columns, and date columns are all detected by measurable properties of the data (cardinality, uniqueness ratio, parse success rate), not by column name — the same logic correctly handled a completely different schema (retail sales) without modification.
- **Every function is independently unit-tested** against hand-built dataframes with known correct answers — not just checked for "runs without error."
- **Known, stated limitations rather than silent gaps.** Where a check is genuinely dataset-specific (faulty-date sequencing, numeric derivation), the pipeline says so explicitly in its log rather than pretending to be more general than it is.
- **Defensive by design.** Date parsing wraps risky operations in a sample-check + try/except, so one malformed column can't crash the entire pipeline run.

## Tech stack

Python 3.13, pandas, numpy, ydata-profiling *(planned)*

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Mac/Linux
pip install -r requirements.txt
```

## Progress

- [x] Design: fixed ruleset across 4 data-quality pillars
- [x] `profiler.py` — verified against manual null counts
- [x] `cleaner.py` — all 7 functions built, individually unit-tested
- [x] `clean_dataset()` orchestrator — verified end-to-end on two structurally different datasets
- [ ] Automated EDA report generation
- [ ] CLI wrapper (`--input` / `--output` arguments)
- [ ] README limitations section expanded with edge cases (division-by-zero in derivation, generic faulty-date detection)
