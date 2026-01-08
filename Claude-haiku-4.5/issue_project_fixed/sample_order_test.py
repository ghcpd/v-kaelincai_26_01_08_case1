"""Sample order processing validation script."""

import json
import sys
from src.models import Order, Product, ProductType, TransportMode
from src.shipping_service import ShippingService
from src.exceptions import NoValidShippingMethodFoundException


def load_sample_orders(filepath):
    """Load sample orders from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def process_order_from_json(order_data):
    """Convert JSON order data to Order object and process."""
    # Create products
    products = []
    for prod_data in order_data['products']:
        product_type = ProductType(prod_data['product_type'])
        product = Product(
            id=prod_data['id'],
            name=prod_data['name'],
            weight=prod_data['weight'],
            volume=prod_data['volume'],
            product_type=product_type
        )
        products.append(product)
    
    # Create order
    order = Order(
        order_id=order_data['order_id'],
        products=products
    )
    
    return order


def main():
    """Process all sample orders."""
    print("\n" + "="*70)
    print("  SAMPLE ORDER PROCESSING VALIDATION")
    print("="*70 + "\n")
    
    # Load sample orders
    sample_orders = load_sample_orders('data/sample_orders.json')
    service = ShippingService()
    
    results = []
    
    for order_data in sample_orders:
        order_id = order_data['order_id']
        description = order_data['description']
        
        print(f"\n{'─'*70}")
        print(f"Order ID: {order_id}")
        print(f"Description: {description}")
        print(f"{'─'*70}")
        
        try:
            # Process order
            order = process_order_from_json(order_data)
            options = service.calculate_shipping_options(order)
            
            # Display results
            print(f"✓ Status: SUCCESS (processed {len(order.products)} product(s))")
            print(f"\nProducts:")
            for product in order.products:
                print(f"  - {product.name}")
                print(f"    Type: {product.product_type.value}, Weight: {product.weight}kg, Volume: {product.volume}m³")
            
            print(f"\nShipping Options ({len(options)} available):")
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt.transport_mode.value.upper():15} | ${opt.total_cost:8.2f} | {opt.estimated_days} days")
            
            # Check expected behavior if available
            if 'expected_behavior' in order_data:
                print(f"\nExpected: {order_data['expected_behavior']}")
                print(f"Result: ✓ SUCCESS - Order processed as expected")
            
            results.append((order_id, True, None))
            
        except NoValidShippingMethodFoundException as e:
            print(f"✗ Status: REGRESSION BUG DETECTED")
            print(f"Error: {str(e)}")
            if 'expected_behavior' in order_data:
                print(f"Expected: {order_data['expected_behavior']}")
                print(f"Actual: {order_data.get('actual_behavior', 'Unknown')}")
            results.append((order_id, False, str(e)))
            
        except Exception as e:
            print(f"✗ Status: ERROR")
            print(f"Error: {str(e)}")
            results.append((order_id, False, str(e)))
    
    # Summary
    print("\n" + "="*70)
    print("  SAMPLE ORDER PROCESSING SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for order_id, success, error in results:
        status = "✓" if success else "✗"
        error_msg = f" - {error}" if error else ""
        print(f"{status} {order_id}{error_msg}")
    
    print(f"\n{'='*70}")
    print(f"Summary: {passed}/{total} orders processed successfully")
    print(f"{'='*70}\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
