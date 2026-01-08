FIX SUMMARY — Mixed hazardous+fragile shipping regression (v2.0.1)

Root cause
- The v2.0 refactor used an additive candidate-building approach in
  `ConstraintValidator.get_available_transport_modes`.
- For MIXED products the code added `AIR` (fragile optimization) then
  removed it for hazardous items and only added `GROUND` as a fallback,
  omitting `PRIORITY_GROUND`.

What I changed (minimal, focused)
- src/constraints.py: Repaired candidate-building logic so hazardous
  orders always include ground-based services (`GROUND` and
  `PRIORITY_GROUND`) while preserving fragile optimization for AIR when
  allowed.
- tests/test_constraint_validator.py: Removed `@pytest.mark.xfail` from
  mixed-product tests and left assertions intact.
- tests/test_shipping_service.py: Removed `@pytest.mark.xfail` from the
  mixed-product integration tests.
- src/__init__.py and README.md: Bumped version to **v2.0.1** and
  documented the fix.

Why this fixes the bug
- Ensures the hazardous constraint only removes `AIR` but does not
  accidentally drop valid ground alternatives that should be available
  for mixed products.
- Preserves the fragile optimization (AIR preference) without making it
  exclusive.

Files modified
- src/constraints.py (logic fix)
- tests/test_constraint_validator.py (enable regression tests)
- tests/test_shipping_service.py (enable regression tests)
- src/__init__.py, README.md, FIX_SUMMARY.md (metadata / docs)

Test results (run locally in the fixed project root)
- Command: `pytest tests/ -q`
- Result: All tests pass (11 passed)

Notes / follow-ups
- The fix is intentionally minimal; an alternative would be to
  reintroduce intersection-based logic (safer, simpler). The chosen
  change preserves the v2.0 fragile optimization and corrects the
  interaction with hazardous constraints.

How to verify
1. cd into the fixed project root
2. pip install -r requirements.txt
3. pytest tests/ -v --tb=short

If you'd like, I can open a PR with a focused commit & changelog, and
add one or two additional unit tests to further guard against future
regressions (e.g., combinations of constraints with multiple products).
