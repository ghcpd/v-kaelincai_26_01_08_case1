"""Demo runner to exercise ShippingService using sample orders."""
import json
from src.models import Product, ProductType, Order
from src.shipping_service import ShippingService


def _ptype(ptype_str):
    mapping = {
        "normal": ProductType.NORMAL,
        "hazardous": ProductType.HAZARDOUS,
        "fragile": ProductType.FRAGILE,
        "mixed": ProductType.MIXED,
    }
    return mapping.get(ptype_str, ProductType.NORMAL)


def run_demo():
    svc = ShippingService()
    with open("data/sample_orders.json", "r", encoding="utf-8") as fh:
        orders = json.load(fh)

    for o in orders:
        print(f"\nOrder: {o.get('order_id')} - {o.get('description')}")
        products = []
        for p in o.get("products", []):
            prod = Product(
                id=p["id"],
                name=p["name"],
                weight=p["weight"],
                volume=p["volume"],
                product_type=_ptype(p.get("product_type"))
            )
            products.append(prod)

        order = Order(order_id=o.get("order_id"), products=products)

        try:
            options = svc.calculate_shipping_options(order)
            print(f"  Available {len(options)} option(s):")
            for opt in options:
                print(
                    f"    - mode={opt.transport_mode.value}, total_cost={opt.total_cost:.2f}, volumetric_cost={opt.volumetric_cost:.2f}, est_days={opt.estimated_days}"
                )
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    run_demo()
