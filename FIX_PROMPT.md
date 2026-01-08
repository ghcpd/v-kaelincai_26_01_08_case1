# Prompt Template for Fixing the Shipping Compliance Regression Bug

Use this prompt to request fixing the buggy project. Replace `{NEW_PROJECT_PATH}` with your desired output directory path.

---

## Prompt for AI Model

**Role**: You are a senior software engineer tasked with fixing a regression bug in a Python shipping compliance engine.

**Context**:
I have a buggy Python project located at the current workspace with the following structure:

```
issue_project/
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── constraints.py
│   ├── calculator.py
│   ├── shipping_service.py
│   └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── test_constraint_validator.py    # Contains 2 failing tests
│   └── test_shipping_service.py        # Contains 2 failing tests
├── data/
│   └── sample_orders.json
├── requirements.txt
├── README.md
└── KNOWN_ISSUE.md              # Detailed bug analysis document
```

**Problem Description**:
- The project has a regression bug in the constraint validation system
- Orders with MIXED products (both hazardous AND fragile) fail to find valid shipping methods
- Expected behavior: Mixed products should return GROUND and PRIORITY_GROUND transport options
- Actual behavior: Raises `NoValidShippingMethodFoundException` or returns incomplete options
- 4 tests are currently failing (marked with `@pytest.mark.xfail`)

**Your Task**:

1. **Read and analyze** the existing buggy project:
   - Review `KNOWN_ISSUE.md` for detailed bug analysis
   - Examine the source code to identify the flawed logic
   - Review failing tests to understand expected behavior
   - Debug the code to locate the root cause

2. **Create a FIXED version** in a new directory: `{NEW_PROJECT_PATH}`
   - **DO NOT modify** the original `issue_project/` directory
   - Create complete fixed project in the new location

3. **Required directory structure** for fixed version:
   ```
   {NEW_PROJECT_PATH}/
   ├── src/
   │   ├── __init__.py
   │   ├── models.py
   │   ├── constraints.py
   │   ├── calculator.py
   │   ├── shipping_service.py
   │   └── exceptions.py
   ├── tests/
   │   ├── __init__.py
   │   ├── test_constraint_validator.py    # ✅ REMOVE @pytest.mark.xfail decorators
   │   └── test_shipping_service.py        # ✅ REMOVE @pytest.mark.xfail decorators
   ├── data/
   │   └── sample_orders.json     # Copy from original
   ├── requirements.txt           # Copy from original
   ├── README.md                  # ✅ UPDATE to indicate this is the fixed version
   └── FIX_SUMMARY.md            # ✅ CREATE NEW - Document what was fixed
   ```

4. **Specific fixes required**:
   - Identify and fix the logic bug in the constraint validation system
   - Ensure MIXED products (hazardous + fragile) return valid shipping options
   - Remove all `@pytest.mark.xfail` decorators from test files
   - Ensure ALL tests pass with `pytest tests/ -v`

5. **Success criteria**:
   - All 11 tests must PASS (no xfail, no failures)
   - Mixed products must return at least GROUND and PRIORITY_GROUND options
   - Mixed products must NOT return AIR transport (hazardous constraint)
   - Volumetric cost calculation must still work for fragile items
   - No existing passing tests should break

6. **Deliverables**:
   - Complete fixed project in `{NEW_PROJECT_PATH}/`
   - `FIX_SUMMARY.md` documenting:
     - Root cause analysis
     - What was changed and why
     - Which file(s) and component(s) were modified
     - How the fix addresses the root cause
     - Test results showing all tests passing
   - Updated `README.md` indicating this is v2.0.1 (fixed version)

7. **Important constraints**:
   - Use relative paths only (no absolute paths like `c:\...`)
   - Maintain the exact same project structure
   - Keep all existing functionality intact
   - Fix should be minimal and focused on the root cause
   - Do not add new dependencies

**After creating the fixed version**, run the following command in the new project directory to verify:

```powershell
pytest tests/ -v --tb=short
```

Expected output: `11 passed` (no failures, no xfail)

---

## Example Usage

Replace `{NEW_PROJECT_PATH}` with your actual path, for example:

```
Please fix this project and create the fixed version at: issue_project_fixed
```

or

```
Please fix this project and create the fixed version at: ../fixed_shipping_engine
```

Make sure to provide the relative or desired path when you use this prompt.
