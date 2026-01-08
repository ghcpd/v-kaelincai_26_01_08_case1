# Known Issue: Mixed Product Shipping Method Regression

## Issue Summary

**Issue Type:** Regression Bug (Logic Error)

**Severity:** High - Blocks customer orders for a specific product category

**Version Introduced:** v2.0.0

**Status:** Identified, Not Fixed

## Problem Description

### Trigger Condition

Orders containing **MIXED products** (products that are both HAZARDOUS and FRAGILE) fail to find any valid shipping methods, resulting in `NoValidShippingMethodFoundException`.

**Example Products:**
- Battery-powered glass decorative lamps
- Electronic glass photo frames
- LED glass displays

### Expected Behavior (v1.0)

Mixed products should:
1. Be prohibited from AIR transport (due to hazardous constraint)
2. Be allowed on GROUND and PRIORITY_GROUND transport
3. Have volumetric weight increased by 20% (due to fragile packaging requirements)
4. Return at least 2 shipping options: GROUND and PRIORITY_GROUND

### Actual Behavior (v2.0)

Mixed products:
1. Are initially considered for AIR transport only (fragile optimization)
2. Have AIR removed due to hazardous constraint
3. End up with empty candidate list OR only GROUND (missing PRIORITY_GROUND)
4. **Result:** Either exception is thrown, or PRIORITY_GROUND option is missing

## Root Cause Analysis

### Affected Component

**Module:** Constraint Validation System

**Component:** Transport mode availability determination logic

### Bug Mechanism

The v2.0 refactoring changed the constraint validation logic from **intersection-based** (v1.0) to **additive candidate building** (v2.0). This new approach has a critical flaw:

#### v1.0 Logic (Working)
```python
# Pseudo-code for v1.0
allowed_modes = {AIR, GROUND, PRIORITY_GROUND, FREIGHT}

if has_hazardous:
    allowed_modes = allowed_modes - {AIR}

if has_fragile:
    # No change, all modes work for fragile

return allowed_modes  # Returns {GROUND, PRIORITY_GROUND, FREIGHT}
```

#### v2.0 Logic (Broken)
```python
# Actual v2.0 implementation
candidates = set()

if has_fragile:
    candidates.add(AIR)  # Only adds AIR!

if has_hazardous:
    candidates.discard(AIR)  # Removes AIR
    if not candidates:
        candidates.add(GROUND)  # Fallback only adds GROUND

# Result: candidates = {GROUND}
# PRIORITY_GROUND is never considered!
```

### Logic Flow Issue

The v2.0 implementation processes constraints sequentially:

1. Fragile items trigger an optimization that adds preferred transport modes
2. Hazardous items remove prohibited transport modes
3. A fallback mechanism attempts to ensure at least one option remains

However, when both constraints apply simultaneously (mixed products), the interaction between these steps produces an incomplete result set.

## Impact Assessment

### Business Impact

- **Customer Experience:** Orders fail at checkout for mixed products
- **Revenue Impact:** Lost sales for affected product category (estimated 5-10% of catalog)
- **Support Load:** Increased customer support tickets for "shipping not available" errors

### Technical Impact

- 4 automated tests now failing (marked with `@pytest.mark.xfail`)
- Integration with checkout service returns errors
- Shipping cost estimates unavailable for mixed products

## Reproduction Steps

### Minimal Reproduction

```python
from src.models import Order, Product, ProductType
from src.shipping_service import ShippingService
from src.exceptions import NoValidShippingMethodFoundException

# Create mixed product
product = Product(
    id="TEST-001",
    name="Battery Glass Lamp",
    weight=4.5,
    volume=0.012,
    product_type=ProductType.MIXED
)

order = Order(order_id="TEST-ORDER", products=[product])
service = ShippingService()

# This raises NoValidShippingMethodFoundException
try:
    options = service.calculate_shipping_options(order)
except NoValidShippingMethodFoundException as e:
    print(f"Bug reproduced: {e}")
```

### Automated Test Reproduction

```powershell
# Run failing regression tests
pytest tests/test_constraint_validator.py::TestConstraintValidator::test_mixed_hazardous_fragile_regression -v
pytest tests/test_shipping_service.py::TestShippingService::test_mixed_product_working_scenario -v
```

## Fix Approach (Recommended)

### Strategy 1: Restore Intersection Logic (Safest)

Revert to v1.0 style intersection-based filtering:

```python
def get_available_transport_modes(order: Order) -> List[TransportMode]:
    # Start with all modes
    allowed = {
        TransportMode.AIR,
        TransportMode.GROUND,
        TransportMode.PRIORITY_GROUND,
        TransportMode.FREIGHT
    }
    
    # Apply weight constraint
    if order.total_weight() > MAX_STANDARD_WEIGHT:
        return [TransportMode.FREIGHT]
    
    # Remove AIR if hazardous
    if order.has_hazardous():
        allowed.discard(TransportMode.AIR)
    
    # Remove FREIGHT from standard options
    if order.total_weight() <= MAX_STANDARD_WEIGHT:
        allowed.discard(TransportMode.FREIGHT)
    
    return list(allowed)
```

**Pros:**
- Simple, proven logic
- Easy to understand
- Covers all edge cases

**Cons:**
- Loses the "fragile prefers AIR" optimization

### Strategy 2: Fix Additive Logic (Preserves Optimization)

Repair the candidate-building logic to preserve all valid options:

```python
def get_available_transport_modes(order: Order) -> List[TransportMode]:
    candidates = set()
    
    # Weight constraint
    if order.total_weight() > MAX_STANDARD_WEIGHT:
        return [TransportMode.FREIGHT]
    
    # Start with ground-based options as baseline
    candidates = {TransportMode.GROUND, TransportMode.PRIORITY_GROUND}
    
    # Add AIR if no hazardous items
    if not order.has_hazardous():
        candidates.add(TransportMode.AIR)
    
    # Prioritize AIR for fragile (if allowed)
    if order.has_fragile() and TransportMode.AIR in candidates:
        # AIR gets priority in sorting, but don't remove other options
        pass
    
    return list(candidates)
```

**Pros:**
- Preserves the optimization intent
- More explicit about baseline options

**Cons:**
- More complex than Strategy 1

### Strategy 3: Hybrid Approach

Use constraint-based filtering with explicit priority hints:

```python
def get_available_transport_modes(order: Order) -> List[TransportMode]:
    # Define base constraints
    forbidden = set()
    
    if order.has_hazardous():
        forbidden.add(TransportMode.AIR)
    
    if order.total_weight() > MAX_STANDARD_WEIGHT:
        return [TransportMode.FREIGHT]
    
    # All standard modes minus forbidden
    allowed = {
        TransportMode.AIR,
        TransportMode.GROUND,
        TransportMode.PRIORITY_GROUND
    } - forbidden
    
    return list(allowed)
```

**Pros:**
- Clean separation of concerns
- Easy to add new constraints

**Cons:**
- Priority/optimization logic needs separate implementation

## Testing Verification

After implementing fix, verify these tests pass:

```powershell
# All regression tests should pass
pytest tests/test_constraint_validator.py::TestConstraintValidator::test_mixed_hazardous_fragile_regression -v
pytest tests/test_constraint_validator.py::TestConstraintValidator::test_order_with_multiple_mixed_products -v
pytest tests/test_shipping_service.py::TestShippingService::test_mixed_product_working_scenario -v
pytest tests/test_shipping_service.py::TestShippingService::test_get_recommended_for_mixed_product -v

# All tests should pass
pytest tests/ -v
```

## Related Issues

- None currently tracked (this is the initial bug report)

## References

- **Change Introduced In:** v2.0.0 refactoring (commit not tracked in this demo)
- **Original Requirement:** Support Priority Ground service
- **Side Effect:** Broke mixed product handling due to constraint logic rewrite

## Additional Notes

### Why This Bug Is Subtle

1. **Passes for single-constraint products:** Hazardous-only and fragile-only products work fine
2. **Only affects combination:** The bug only manifests when BOTH constraints apply
3. **Silent failure path:** The fallback logic partially masks the issue (adds GROUND but not PRIORITY_GROUND)
4. **New feature obscures it:** The bug was introduced while adding a new feature, making it look like an enhancement rather than a regression

### Lessons Learned

1. **Test edge cases explicitly:** Need tests for constraint combinations, not just individual constraints
2. **Regression tests are critical:** Tests should cover previously working scenarios before refactoring
3. **Logic simplicity matters:** The v1.0 intersection approach was simpler and less error-prone
4. **Additive vs. Subtractive:** Building up candidate lists is more error-prone than filtering down from complete sets

---

**Document Version:** 1.0  
**Last Updated:** January 8, 2026  
**Author:** Engineering Team
