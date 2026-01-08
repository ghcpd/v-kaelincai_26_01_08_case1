# Shipping Compliance & Cost Engine (Fixed)

This is the fixed version of the shipping compliance engine. Version: **v2.0.1** (regression bug fixed).

## 🔧 Fix Summary
- Restored correct constraint handling so that MIXED products (hazardous + fragile) return valid ground-based transport options (GROUND and PRIORITY_GROUND) and do not include AIR.
- Volumetric cost behavior for fragile items preserved (20% volume increase).

## ✅ How to run tests

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run tests:

```powershell
pytest tests/ -v
```

Expected result: `11 passed` (no xfail, no failures)
Actual result observed: `12 passed` (no xfail, no failures)

## Project structure

```
issue_project_fixed/
├── src/
├── tests/
├── data/
├── requirements.txt
├── README.md
└── FIX_SUMMARY.md
```

See `FIX_SUMMARY.md` for details about the fix and validation.
