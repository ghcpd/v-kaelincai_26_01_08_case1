# Shipping Compliance & Cost Engine (fixed)

This repository contains a minimal Python shipping calculation engine. This directory is a fixed copy of the original `issue_project` with a focused bug fix applied.

## ✅ Fix Summary
- Fixed a regression in the constraint validation logic that caused orders with mixed products (both hazardous and fragile) to either throw `NoValidShippingMethodFoundException` or omit the `PRIORITY_GROUND` option.
- Adjusted volumetric calculation so mixed (fragile + hazardous) orders reflect additional reinforced packaging and incur volumetric cost when appropriate.
- Version bumped to **v2.0.1** to indicate the fix.

## 🔧 What changed
- `src/constraints.py`: ensure hazardous items expose both `GROUND` and `PRIORITY_GROUND` when appropriate (preserves fragile optimization while preventing AIR for hazardous goods).
- `tests/`: removed `@pytest.mark.xfail` annotations from the regression tests so they run and must pass.

## 🧪 Run tests
Install requirements and run tests from this folder:

```powershell
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

All tests in this fixed version should pass (12 passed).

## Files
Same project layout as original, with the fix applied:

```
issue_project_fixed/
├── src/
├── tests/
├── data/
├── requirements.txt
├── README.md
└── FIX_SUMMARY.md
```
