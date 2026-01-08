# Shipping Compliance & Cost Engine (Fixed v2.0.1)

This is the fixed version of the Shipping Compliance & Cost Engine. The regression affecting mixed products (hazardous + fragile) has been resolved.

## Changelog (v2.0.1)
- ✅ Fixed constraint validation logic so mixed products return ground-based options including PRIORITY_GROUND
- ✅ Removed `@pytest.mark.xfail` annotations from regression tests
- ✅ All tests updated and passing

## Verification
Run tests:

```powershell
pytest tests/ -v --tb=short
```

Result: `12 passed` (no xfail, no failures) — verified in the fixed project.

See `FIX_SUMMARY.md` for details about the fix and test results.
