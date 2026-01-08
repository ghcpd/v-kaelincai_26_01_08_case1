"""Unit tests for ConstraintValidator - these tests expose the regression bug."""

import pytest
from src.models import Order, Product, ProductType, TransportMode
from src.constraints import ConstraintValidator


class TestConstraintValidator:
    """Test suite for constraint validation logic."""
    
    def test_normal_product_all_modes_available(self):
        """Normal products should have all standard transport modes available."""
        product = Product(
            id="P001",
            name="Regular Widget",
            weight=5.0,
            volume=0.01,
            product_type=ProductType.NORMAL
        )
        order = Order(order_id="O001", products=[product])
        
        available = ConstraintValidator.get_available_transport_modes(order)
        
        # Should have AIR, GROUND, and PRIORITY_GROUND
        assert len(available) >= 2
        assert TransportMode.AIR in available or TransportMode.GROUND in available
    
    def test_hazardous_product_no_air_transport(self):
        """Hazardous products must not use air transport."""
        product = Product(
            id="P002",
            name="Lithium Battery Pack",
            weight=3.0,
            volume=0.005,
            product_type=ProductType.HAZARDOUS
        )
        order = Order(order_id="O002", products=[product])
        
        available = ConstraintValidator.get_available_transport_modes(order)
        
        # AIR should be prohibited
        assert TransportMode.AIR not in available
        # But GROUND should be available
        assert TransportMode.GROUND in available
    
    def test_fragile_product_has_air_option(self):
        """Fragile products should have air transport as an option (v2.0 optimization)."""
        product = Product(
            id="P003",
            name="Crystal Vase",
            weight=2.0,
            volume=0.008,
            product_type=ProductType.FRAGILE
        )
        order = Order(order_id="O003", products=[product])
        
        available = ConstraintValidator.get_available_transport_modes(order)
        
        # AIR should be available for fragile items (new optimization)
        assert TransportMode.AIR in available
    
    def test_overweight_requires_freight(self):
        """Orders over 50kg must use freight."""
        product = Product(
            id="P004",
            name="Heavy Machinery Part",
            weight=75.0,
            volume=0.05,
            product_type=ProductType.NORMAL
        )
        order = Order(order_id="O004", products=[product])
        
        available = ConstraintValidator.get_available_transport_modes(order)
        
        # Only FREIGHT should be available
        assert available == [TransportMode.FREIGHT]
    
    def test_mixed_hazardous_fragile_regression(self):
        """
        REGRESSION TEST: Mixed products (hazardous + fragile) should work.
        
        Example: Battery-powered glass decorative lamp
        - Is hazardous (battery) -> cannot use AIR
        - Is fragile (glass) -> prefers AIR in v2.0
        
        EXPECTED (v1.0 behavior): Should return GROUND and PRIORITY_GROUND
        ACTUAL (v2.0): Returns incomplete shipping options
        """
        product = Product(
            id="P005",
            name="Battery-Powered Glass Lamp",
            weight=4.5,
            volume=0.012,
            product_type=ProductType.MIXED  # Both hazardous AND fragile
        )
        order = Order(order_id="O005", products=[product])
        
        available = ConstraintValidator.get_available_transport_modes(order)
        
        # Should have ground-based options available
        assert len(available) > 0, "Mixed items should have at least one valid shipping method"
        
        # AIR should NOT be available (hazardous constraint)
        assert TransportMode.AIR not in available, "Hazardous items cannot use air transport"
        
        # GROUND should be available
        assert TransportMode.GROUND in available, "Ground transport should be available"
        
        # PRIORITY_GROUND should also be available (THIS FAILS in v2.0)
        assert TransportMode.PRIORITY_GROUND in available, \
            "Priority Ground should be available for mixed items"
    
    def test_order_with_multiple_mixed_products(self):
        """
        REGRESSION TEST: Order with multiple mixed-type products.
        
        Demonstrates the issue affects orders with multiple mixed items.
        """
        products = [
            Product(
                id="P006",
                name="Battery-Powered Glass Lamp",
                weight=4.5,
                volume=0.012,
                product_type=ProductType.MIXED
            ),
            Product(
                id="P007",
                name="Electronic Glass Photo Frame",
                weight=1.2,
                volume=0.004,
                product_type=ProductType.MIXED
            )
        ]
        order = Order(order_id="O006", products=products)
        
        available = ConstraintValidator.get_available_transport_modes(order)
        
        # Should have valid shipping methods
        assert len(available) >= 2, \
            "Order with mixed products should have multiple ground-based shipping options"
        
        # Both GROUND and PRIORITY_GROUND should be present
        ground_options = [m for m in available if m in [TransportMode.GROUND, TransportMode.PRIORITY_GROUND]]
        assert len(ground_options) >= 2, \
            f"Expected both GROUND and PRIORITY_GROUND, but got: {available}"
