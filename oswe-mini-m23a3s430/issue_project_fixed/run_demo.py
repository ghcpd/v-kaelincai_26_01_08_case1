from src.models import Product, ProductType, Order
from src.shipping_service import ShippingService

service = ShippingService()

cases = [
    ("Normal product", Product(id="D001", name="Notebook", weight=0.7, volume=0.002, product_type=ProductType.NORMAL)),
    ("Fragile product", Product(id="D002", name="Glass Ornament", weight=1.5, volume=0.006, product_type=ProductType.FRAGILE)),
    ("Hazardous product", Product(id="D003", name="Spray Can", weight=0.9, volume=0.001, product_type=ProductType.HAZARDOUS)),
    ("Mixed product", Product(id="D004", name="Battery Glass Lamp", weight=4.5, volume=0.012, product_type=ProductType.MIXED)),
]

for desc, prod in cases:
    order = Order(order_id=f"DEMO-{prod.id}", products=[prod])
    print(f"\n=== {desc} ({prod.product_type.value}) ===")
    try:
        options = service.calculate_shipping_options(order)
        for opt in options:
            print(f"- {opt.transport_mode.value}: base={opt.base_cost:.2f}, volumetric={opt.volumetric_cost:.2f}, total={opt.total_cost:.2f}, eta={opt.estimated_days}d")
    except Exception as e:
        print(f"ERROR: {e}")

print("\nDemo run complete.")