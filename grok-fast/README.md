# Shipping Compliance & Cost Engine

A Python-based shipping calculation system that determines valid shipping methods and costs for e-commerce orders based on product characteristics (hazardous, fragile, weight) and transportation constraints.

## ✅ Fixed Version (v2.0.1)

**This is the FIXED version** of the shipping engine. The regression bug in v2.0.0 that caused mixed products (hazardous + fragile) to fail has been resolved.

**Fixed scenario:**
- Product: Battery-powered glass decorative lamp (MIXED type)
- Result: Returns GROUND and PRIORITY_GROUND shipping options with volumetric cost

See [FIX_SUMMARY.md](FIX_SUMMARY.md) for details on what was fixed.

## 📋 Project Structure

```
grok-fast/
├── src/
│   ├── __init__.py
│   ├── models.py              # Data models (Product, Order, ShippingMethod)
│   ├── constraints.py         # ConstraintValidator (FIXED)
│   ├── calculator.py          # VolumetricCalculator for cost calculation
│   ├── shipping_service.py    # Main ShippingService
│   └── exceptions.py          # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_constraint_validator.py  # Unit tests (ALL PASSING)
│   └── test_shipping_service.py      # Integration tests (ALL PASSING)
├── data/
│   └── sample_orders.json     # Sample order data with regression cases
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── FIX_SUMMARY.md            # Fix documentation
```

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Run Tests

Run all tests (all should pass):

```powershell
pytest tests/ -v
```

Run tests with coverage:

```powershell
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Expected Test Results

- **Total tests:** 11
- **Passing:** 11 tests (all functionality working)
- **Failing:** 0 tests

## 🎯 Business Logic Overview

### Product Types

1. **NORMAL**: Standard products with no special handling
2. **HAZARDOUS**: Items like batteries, sprays (cannot use air transport)
3. **FRAGILE**: Items like glass, ceramics (require reinforced packaging, +20% volume)
4. **MIXED**: Both hazardous AND fragile (e.g., battery-powered glass lamp)

### Transport Modes

1. **AIR**: Fastest (1 day), most expensive
2. **PRIORITY_GROUND**: Fast ground service (2 days) - NEW in v2.0
3. **GROUND**: Standard ground shipping (5 days)
4. **FREIGHT**: For heavy items >50kg (7 days)

### Shipping Constraints

- **Hazardous products:** Cannot use AIR transport
- **Fragile products:** Volumetric weight increased by 20% for reinforced packaging
- **Heavy items (>50kg):** Must use FREIGHT only

## 🔍 Testing the Fix

### Using Python Code

```python
from src.models import Order, Product, ProductType
from src.shipping_service import ShippingService

# Create a mixed product (hazardous + fragile)
lamp = Product(
    id="P001",
    name="Battery-Powered Glass Lamp",
    weight=4.5,
    volume=0.012,
    product_type=ProductType.MIXED
)

order = Order(order_id="O001", products=[lamp])
service = ShippingService()

# This now works correctly in v2.0.1
options = service.calculate_shipping_options(order)
print(f"Available options: {len(options)}")
for opt in options:
    print(f"- {opt.transport_mode}: ${opt.total_cost:.2f}")
```

### Using Tests

```powershell
# Run the previously failing regression tests
pytest tests/test_constraint_validator.py::TestConstraintValidator::test_mixed_hazardous_fragile_regression -v
pytest tests/test_shipping_service.py::TestShippingService::test_mixed_product_working_scenario -v

# Run all tests
pytest tests/ -v
```

## 📊 Test Coverage

The test suite includes:

1. **Unit Tests** (`test_constraint_validator.py`):
   - Normal product handling
   - Hazardous product constraints
   - Fragile product handling
   - Overweight freight requirements
   - ✅ **Mixed product regression** (now passing)

2. **Integration Tests** (`test_shipping_service.py`):
   - End-to-end shipping calculation
   - Cost calculation with volumetric weight
   - Recommended shipping selection
   - ✅ **Mixed product end-to-end** (now passing)

## 🛠️ Version History

### v2.0.1 (Current - Fixed)
- ✅ Fixed regression bug in mixed product constraint validation
- ✅ All tests passing (11/11)
- ✅ Mixed products return GROUND and PRIORITY_GROUND options

### v2.0.0 (Previous - Buggy)
- ✅ Added Priority Ground service
- ✅ Refactored ConstraintValidator with TransportMode abstraction
- ✅ Added optimization: Fragile items prefer AIR to reduce vibration
- ❌ **Bug:** Mixed products (hazardous + fragile) fail to find valid shipping methods

### v1.0.0 (Previous - Working)
- ✅ Basic constraint validation using intersection logic
- ✅ Support for hazardous, fragile, and normal products
- ✅ Mixed products worked correctly

## 📝 Sample Data

See `data/sample_orders.json` for example orders including previously failing regression cases.

## 🧪 Development

To add new tests:

```python
# tests/test_your_feature.py
import pytest
from src.models import Order, Product, ProductType

def test_your_scenario():
    # Your test code here
    pass
```

Run specific test file:

```powershell
pytest tests/test_your_feature.py -v
```

## 📄 License

This is a demonstration project for bug reproduction and fixing purposes.

## 🔗 Related Files

- [FIX_SUMMARY.md](FIX_SUMMARY.md) - Details on the fix
- [data/sample_orders.json](data/sample_orders.json) - Sample order data