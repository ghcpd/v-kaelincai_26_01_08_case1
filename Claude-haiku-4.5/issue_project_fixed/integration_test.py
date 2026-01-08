"""Integration test script to validate all project scenarios."""

import json
import sys
from src.models import Order, Product, ProductType, TransportMode
from src.shipping_service import ShippingService
from src.exceptions import NoValidShippingMethodFoundException


def print_header(title):
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_normal_product():
    """Test normal product shipping options."""
    print_header("TEST 1: Normal Product (No Constraints)")
    
    product = Product(
        id="P001",
        name="Python Programming Book",
        weight=0.8,
        volume=0.003,
        product_type=ProductType.NORMAL
    )
    order = Order(order_id="ORD001", products=[product])
    service = ShippingService()
    
    try:
        options = service.calculate_shipping_options(order)
        print(f"✓ Order {order.order_id} processed successfully")
        print(f"  Product: {product.name}")
        print(f"  Weight: {product.weight}kg, Volume: {product.volume}m³")
        print(f"  Available shipping methods: {len(options)}")
        for opt in options:
            print(f"    - {opt.transport_mode.value.upper():15} | Cost: ${opt.total_cost:8.2f} | Days: {opt.estimated_days}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_hazardous_product():
    """Test hazardous product (no air transport)."""
    print_header("TEST 2: Hazardous Product (No AIR Transport)")
    
    product = Product(
        id="P002",
        name="Lithium-Ion Battery Pack",
        weight=2.5,
        volume=0.006,
        product_type=ProductType.HAZARDOUS
    )
    order = Order(order_id="ORD002", products=[product])
    service = ShippingService()
    
    try:
        options = service.calculate_shipping_options(order)
        has_air = any(opt.transport_mode == TransportMode.AIR for opt in options)
        
        print(f"✓ Order {order.order_id} processed successfully")
        print(f"  Product: {product.name}")
        print(f"  Weight: {product.weight}kg, Volume: {product.volume}m³")
        print(f"  AIR Transport Excluded: {not has_air}")
        print(f"  Available shipping methods: {len(options)}")
        for opt in options:
            print(f"    - {opt.transport_mode.value.upper():15} | Cost: ${opt.total_cost:8.2f} | Days: {opt.estimated_days}")
        
        if has_air:
            print("✗ VALIDATION FAILED: AIR transport found for hazardous product!")
            return False
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_fragile_product():
    """Test fragile product (includes volumetric cost)."""
    print_header("TEST 3: Fragile Product (With Volumetric Cost)")
    
    product = Product(
        id="P003",
        name="Crystal Wine Glasses (Set of 6)",
        weight=1.5,
        volume=0.015,
        product_type=ProductType.FRAGILE
    )
    order = Order(order_id="ORD003", products=[product])
    service = ShippingService()
    
    try:
        options = service.calculate_shipping_options(order)
        has_volumetric_cost = any(opt.volumetric_cost > 0 for opt in options)
        
        print(f"✓ Order {order.order_id} processed successfully")
        print(f"  Product: {product.name}")
        print(f"  Weight: {product.weight}kg, Volume: {product.volume}m³")
        print(f"  Has Volumetric Cost: {has_volumetric_cost}")
        print(f"  Available shipping methods: {len(options)}")
        for opt in options:
            print(f"    - {opt.transport_mode.value.upper():15} | Cost: ${opt.total_cost:8.2f} (Volumetric: ${opt.volumetric_cost:.2f}) | Days: {opt.estimated_days}")
        
        if not has_volumetric_cost:
            print("✗ VALIDATION FAILED: No volumetric cost for fragile product!")
            return False
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_mixed_product():
    """Test mixed product (hazardous + fragile) - THE REGRESSION BUG FIX."""
    print_header("TEST 4: Mixed Product (Hazardous + Fragile) - REGRESSION TEST")
    
    product = Product(
        id="P004",
        name="Battery-Powered Glass Decorative Lamp",
        weight=2.0,
        volume=0.012,
        product_type=ProductType.MIXED
    )
    order = Order(order_id="ORD004", products=[product])
    service = ShippingService()
    
    try:
        options = service.calculate_shipping_options(order)
        
        has_air = any(opt.transport_mode == TransportMode.AIR for opt in options)
        has_ground = any(opt.transport_mode == TransportMode.GROUND for opt in options)
        has_priority_ground = any(opt.transport_mode == TransportMode.PRIORITY_GROUND for opt in options)
        has_volumetric = any(opt.volumetric_cost > 0 for opt in options)
        
        print(f"✓ Order {order.order_id} processed successfully")
        print(f"  Product: {product.name}")
        print(f"  Weight: {product.weight}kg, Volume: {product.volume}m³")
        print(f"  Product Type: MIXED (Hazardous + Fragile)")
        print(f"\n  VALIDATION RESULTS:")
        print(f"    ✓ Has GROUND: {has_ground}")
        print(f"    ✓ Has PRIORITY_GROUND: {has_priority_ground}")
        print(f"    ✓ NO AIR (hazardous): {not has_air}")
        print(f"    ✓ Has Volumetric Cost: {has_volumetric}")
        print(f"\n  Available shipping methods: {len(options)}")
        for opt in options:
            print(f"    - {opt.transport_mode.value.upper():15} | Cost: ${opt.total_cost:8.2f} (Volumetric: ${opt.volumetric_cost:.2f}) | Days: {opt.estimated_days}")
        
        # Validate all requirements
        success = True
        if has_air:
            print("\n✗ VALIDATION FAILED: AIR transport found (hazardous constraint violated)!")
            success = False
        if not has_ground:
            print("\n✗ VALIDATION FAILED: GROUND transport missing!")
            success = False
        if not has_priority_ground:
            print("\n✗ VALIDATION FAILED: PRIORITY_GROUND transport missing!")
            success = False
        if not has_volumetric:
            print("\n✗ VALIDATION FAILED: No volumetric cost for fragile component!")
            success = False
        
        if success:
            print("\n✓✓✓ REGRESSION FIX VALIDATED ✓✓✓")
        return success
    except NoValidShippingMethodFoundException as e:
        print(f"✗ REGRESSION BUG STILL EXISTS: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_heavy_product():
    """Test heavy product (freight only)."""
    print_header("TEST 5: Heavy Product (Freight Only)")
    
    product = Product(
        id="P005",
        name="Industrial Compressor",
        weight=85.0,
        volume=0.3,
        product_type=ProductType.NORMAL
    )
    order = Order(order_id="ORD005", products=[product])
    service = ShippingService()
    
    try:
        options = service.calculate_shipping_options(order)
        all_freight = all(opt.transport_mode == TransportMode.FREIGHT for opt in options)
        
        print(f"✓ Order {order.order_id} processed successfully")
        print(f"  Product: {product.name}")
        print(f"  Weight: {product.weight}kg, Volume: {product.volume}m³")
        print(f"  Only FREIGHT Available: {all_freight}")
        print(f"  Available shipping methods: {len(options)}")
        for opt in options:
            print(f"    - {opt.transport_mode.value.upper():15} | Cost: ${opt.total_cost:8.2f} | Days: {opt.estimated_days}")
        
        if not all_freight:
            print("✗ VALIDATION FAILED: Non-freight options found for overweight product!")
            return False
        if len(options) != 1:
            print("✗ VALIDATION FAILED: Expected exactly 1 option (FREIGHT)!")
            return False
        return True
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_recommended_shipping():
    """Test get recommended (cheapest) shipping for mixed product."""
    print_header("TEST 6: Recommended Shipping for Mixed Product")
    
    product = Product(
        id="P006",
        name="Electronic Glass Photo Frame",
        weight=0.8,
        volume=0.004,
        product_type=ProductType.MIXED
    )
    order = Order(order_id="ORD006", products=[product])
    service = ShippingService()
    
    try:
        recommended = service.get_recommended_shipping(order)
        
        print(f"✓ Order {order.order_id} processed successfully")
        print(f"  Product: {product.name}")
        print(f"  Weight: {product.weight}kg, Volume: {product.volume}m³")
        print(f"\n  RECOMMENDED SHIPPING:")
        print(f"    Transport: {recommended.transport_mode.value.upper()}")
        print(f"    Base Cost: ${recommended.base_cost:.2f}")
        print(f"    Volumetric Cost: ${recommended.volumetric_cost:.2f}")
        print(f"    Total Cost: ${recommended.total_cost:.2f}")
        print(f"    Estimated Days: {recommended.estimated_days}")
        
        # Validate
        valid_modes = [TransportMode.GROUND, TransportMode.PRIORITY_GROUND]
        if recommended.transport_mode not in valid_modes:
            print(f"\n✗ VALIDATION FAILED: Recommended mode {recommended.transport_mode.value} not in valid ground options!")
            return False
        return True
    except NoValidShippingMethodFoundException as e:
        print(f"✗ REGRESSION BUG: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_multiple_mixed_products():
    """Test order with multiple mixed products."""
    print_header("TEST 7: Multiple Mixed Products in Single Order")
    
    products = [
        Product(
            id="P007",
            name="Battery-Powered Glass Lamp",
            weight=2.5,
            volume=0.010,
            product_type=ProductType.MIXED
        ),
        Product(
            id="P008",
            name="Electronic Glass Frame",
            weight=1.0,
            volume=0.004,
            product_type=ProductType.MIXED
        )
    ]
    order = Order(order_id="ORD007", products=products)
    service = ShippingService()
    
    try:
        options = service.calculate_shipping_options(order)
        
        total_weight = sum(p.weight for p in products)
        total_volume = sum(p.volume for p in products)
        
        has_ground = any(opt.transport_mode == TransportMode.GROUND for opt in options)
        has_priority_ground = any(opt.transport_mode == TransportMode.PRIORITY_GROUND for opt in options)
        has_air = any(opt.transport_mode == TransportMode.AIR for opt in options)
        
        print(f"✓ Order {order.order_id} processed successfully")
        print(f"  Products: {len(products)}")
        for p in products:
            print(f"    - {p.name}")
        print(f"  Total Weight: {total_weight}kg, Total Volume: {total_volume}m³")
        print(f"\n  VALIDATION RESULTS:")
        print(f"    ✓ Has GROUND: {has_ground}")
        print(f"    ✓ Has PRIORITY_GROUND: {has_priority_ground}")
        print(f"    ✓ NO AIR (hazardous): {not has_air}")
        print(f"\n  Available shipping methods: {len(options)}")
        for opt in options:
            print(f"    - {opt.transport_mode.value.upper():15} | Cost: ${opt.total_cost:8.2f} | Days: {opt.estimated_days}")
        
        # Validate
        if has_air:
            print("\n✗ VALIDATION FAILED: AIR transport found!")
            return False
        if not has_ground or not has_priority_ground:
            print("\n✗ VALIDATION FAILED: Ground options missing!")
            return False
        if len(options) < 2:
            print("\n✗ VALIDATION FAILED: Expected at least 2 options!")
            return False
        return True
    except NoValidShippingMethodFoundException as e:
        print(f"✗ REGRESSION BUG: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def main():
    """Run all integration tests."""
    print("\n" + "="*70)
    print("  SHIPPING COMPLIANCE ENGINE - INTEGRATION TEST SUITE")
    print("="*70)
    
    results = []
    
    # Run all tests
    results.append(("Normal Product", test_normal_product()))
    results.append(("Hazardous Product", test_hazardous_product()))
    results.append(("Fragile Product", test_fragile_product()))
    results.append(("Mixed Product (REGRESSION FIX)", test_mixed_product()))
    results.append(("Heavy Product", test_heavy_product()))
    results.append(("Recommended Shipping", test_recommended_shipping()))
    results.append(("Multiple Mixed Products", test_multiple_mixed_products()))
    
    # Print summary
    print_header("INTEGRATION TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("✓✓✓ ALL INTEGRATION TESTS PASSED ✓✓✓\n")
        return 0
    else:
        print(f"✗✗✗ {total - passed} TEST(S) FAILED ✗✗✗\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
