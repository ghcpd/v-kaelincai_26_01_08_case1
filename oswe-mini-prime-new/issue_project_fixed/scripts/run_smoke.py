"""Smoke test: exercise ShippingService using data/sample_orders.json and verify expected behavior."""
import sys
from pathlib import Path
# Ensure project root is on sys.path so `src` package can be imported when running this script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import traceback
from src.models import Product, ProductType, Order, TransportMode
from src.shipping_service import ShippingService


def load_orders(path="data/sample_orders.json"):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    orders = []
    for item in data:
        products = []
        for p in item.get("products", []):
            pt = ProductType(p.get("product_type"))
            products.append(Product(id=p.get("id"), name=p.get("name"), weight=p.get("weight"), volume=p.get("volume"), product_type=pt))
        orders.append((item.get("order_id"), item.get("description"), Order(order_id=item.get("order_id"), products=products)))
    return orders


def main():
    svc = ShippingService()
    orders = load_orders()

    overall_ok = True
    print("Running smoke tests for sample orders:\n")

    for order_id, desc, order in orders:
        try:
            options = svc.calculate_shipping_options(order)
        except Exception as e:
            overall_ok = False
            print(f"ORDER {order_id}: ERROR while calculating shipping options: {e}")
            traceback.print_exc()
            continue

        print(f"ORDER {order_id}: {desc}")
        if not options:
            overall_ok = False
            print("  -> No options returned (FAIL)")
            continue

        # Print options summary
        for opt in options:
            print(f"  - {opt.transport_mode.value}: total_cost={opt.total_cost:.2f}, volumetric_cost={opt.volumetric_cost:.2f}, days={opt.estimated_days}")

        # Additional checks for expected scenarios
        # Identify mixed orders by checking if any product is MIXED
        if order.has_hazardous() and order.has_fragile():
            # mixed: should not contain AIR and should contain ground-based options including PRIORITY_GROUND
            modes = [o.transport_mode for o in options]
            if TransportMode.AIR in modes:
                overall_ok = False
                print("  -> FAIL: Mixed order contains AIR (should be prohibited)")
            if not any(m in modes for m in [TransportMode.GROUND, TransportMode.PRIORITY_GROUND]):
                overall_ok = False
                print("  -> FAIL: Mixed order missing ground-based options")
            if not any(o.volumetric_cost > 0 for o in options):
                overall_ok = False
                print("  -> FAIL: Mixed order lacked volumetric cost for fragile packaging")
            else:
                print("  -> Mixed order checks OK")

        # Heavy items should be freight-only
        if order.total_weight() > 50:
            if not (len(options) == 1 and options[0].transport_mode == TransportMode.FREIGHT):
                overall_ok = False
                print("  -> FAIL: Heavy order did not return freight-only option")
            else:
                print("  -> Heavy order checks OK")

        # Hazardous-only: should not include AIR
        if order.has_hazardous() and not order.has_fragile():
            if any(o.transport_mode == TransportMode.AIR for o in options):
                overall_ok = False
                print("  -> FAIL: Hazardous-only order contains AIR")
            else:
                print("  -> Hazardous-only checks OK")

        # Fragile-only: should include volumetric cost > 0
        if order.has_fragile() and not order.has_hazardous():
            if not any(o.volumetric_cost > 0 for o in options):
                overall_ok = False
                print("  -> FAIL: Fragile-only order did not include volumetric cost")
            else:
                print("  -> Fragile-only checks OK")

        print("")

    print("Smoke test summary:")
    if overall_ok:
        print("  ALL SMOKE CHECKS PASSED")
    else:
        print("  SOME SMOKE CHECKS FAILED")


if __name__ == "__main__":
    main()
