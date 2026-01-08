# Shipping Compliance & Cost Engine - v2.0.1 (FIXED)

A Python-based shipping calculation system that determines valid shipping methods and costs for e-commerce orders based on product characteristics (hazardous, fragile, weight) and transportation constraints.

## 🐛 Fixed Regression Issue

**Version 2.0.1 fixes the regression bug** introduced in v2.0 that caused orders with **mixed products** (both hazardous AND fragile) to fail with `NoValidShippingMethodFoundException`.

**Fixed scenario:**
- Product: Battery-powered glass decorative lamp (MIXED type)
- Expected: Return GROUND and PRIORITY_GROUND shipping options
- Status: ✅ **FIXED** - Now returns correct options

## 📋 Project Structure

```
issue_project_fixed/
├── src/
│   ├── __init__.py
│   ├── models.py              # Data models (Product, Order, ShippingMethod)
│   ├── constraints.py         # ConstraintValidator (FIXED)
│   ├── calculator.py          # VolumetricCalculator for cost calculation
│   ├── shipping_service.py    # Main ShippingService
│   └── exceptions.py          # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_constraint_validator.py  # Unit tests (all passing)
│   └── test_shipping_service.py      # Integration tests (all passing)
├── data/
│   └── sample_orders.json     # Sample order data with test cases
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── FIX_SUMMARY.md            # Detailed fix documentation
```

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Run Tests

Run all tests:

```powershell
pytest tests/ -v
```

Expected output: **11 passed** (no failures, no xfail)

## ✅ Fixed Issues

### What Was Fixed

The constraint validation system now correctly handles products that have multiple constraints (hazardous + fragile). The fix uses an intersection-based approach instead of the broken additive approach.

### Key Changes

- **File Modified:** `src/constraints.py`
- **Root Cause:** Logic error in `get_available_transport_modes()` method
- **Solution:** Changed from additive candidate building to constraint-based intersection logic

### Test Results

All 11 tests now pass:
- ✅ 5 unit tests in `test_constraint_validator.py`
- ✅ 6 integration tests in `test_shipping_service.py`

Previously failing tests now pass:
- ✅ `test_mixed_hazardous_fragile_regression`
- ✅ `test_order_with_multiple_mixed_products`
- ✅ `test_mixed_product_working_scenario`
- ✅ `test_get_recommended_for_mixed_product`

## 📖 Usage Example

```python
from src.models import Product, Order, ProductType
from src.shipping_service import ShippingService

# Create a mixed product (hazardous + fragile)
product = Product(
    id="P001",
    name="Battery-Powered Glass Lamp",
    weight=4.5,
    volume=0.012,
    product_type=ProductType.MIXED
)

# Create order
order = Order(order_id="ORD001", products=[product])

# Get shipping options
service = ShippingService()
options = service.calculate_shipping_options(order)

# Get recommended (cheapest) option
recommended = service.get_recommended_shipping(order)
print(f"Recommended: {recommended.transport_mode.value} - ${recommended.total_cost}")
```

## 📝 Changes Summary

See [FIX_SUMMARY.md](FIX_SUMMARY.md) for detailed analysis of the bug and fix.
