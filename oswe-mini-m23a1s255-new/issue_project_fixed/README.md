# Shipping Compliance & Cost Engine — fixed (v2.0.1)

This repository is a fixed copy of the Shipping Compliance Engine. The
regression that prevented mixed (hazardous + fragile) products from
returning valid ground-based shipping options has been resolved in
version **v2.0.1**.

Highlights
- Fix: Mixed products now return both `GROUND` and `PRIORITY_GROUND` (no AIR)
- All regression tests that were previously marked xfail have been enabled
- Version bumped to `v2.0.1`

Run tests

```powershell
pip install -r requirements.txt
pytest tests/ -v --tb=short
```
