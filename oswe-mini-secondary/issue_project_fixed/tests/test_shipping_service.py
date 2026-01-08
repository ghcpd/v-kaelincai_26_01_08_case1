"""Integration tests for ShippingService - fixed regression should pass."""

import pytest
from src.models import Order, Product, ProductType
from src.shipping_service import ShippingService
from src.exceptions import NoValidShippingMethodFoundException


class TestShippingService:
    """Integration tests for the shipping service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = ShippingService()
    
    def test_normal_product_returns_options(self):
        """Normal products should return multiple shipping options."""
        product = Product(
            id="P101",
            name="Book",
            weight=0.5,
            volume=0.002,
            product_type=ProductType.NORMAL
        )
        order = Order(order_id="O101", products=[product])
        
        options = self.service.calculate_shipping_options(order)
        
        assert len(options) > 0
        # Should be sorted by cost
        assert all(options[i].total_cost <= options[i+1].total_cost 
                  for i in range(len(options)-1))
    
    def test_hazardous_product_no_air_in_options(self):
        """Hazardous products should not have air shipping in options."""
        product = Product(
            id="P102",
            name="Spray Paint",
            weight=0.8,
            volume=0.001,
            product_type=ProductType.HAZARDOUS
        )
        order = Order(order_id="O102", products=[product])
        
        options = self.service.calculate_shipping_options(order)
        
        # Should have options
        assert len(options) > 0
        # None should be AIR
        from src.models import TransportMode
        assert all(opt.transport_mode != TransportMode.AIR for opt in options)
    
    def test_fragile_product_includes_volumetric_cost(self):
        """Fragile products should have increased volumetric cost (20% more volume)."""
        product = Product(
            id="P103",
            name="Wine Glasses Set",
            weight=2.0,
            volume=0.010,
            product_type=ProductType.FRAGILE
        )
        order = Order(order_id="O103", products=[product])
        
        options = self.service.calculate_shipping_options(order)
        
        assert len(options) > 0
        # At least one option should have volumetric cost > 0
        # because fragile adds 20% volume
        assert any(opt.volumetric_cost > 0 for opt in options)
    
    def test_mixed_product_working_scenario(self):
        """
        Previously failing scenario should now work for mixed products.
        """
        product = Product(
            id="P104",
            name="Battery-Powered Glass Decorative Lamp",
            weight=4.5,
            volume=0.012,
            product_type=ProductType.MIXED
        )
        order = Order(order_id="O104", products=[product])
        
        # This should NOT raise an exception
        options = self.service.calculate_shipping_options(order)
        
        # Should have valid shipping options
        assert len(options) >= 1, "Mixed products should have at least one valid shipping method"
        
        # Should include ground-based transport
        from src.models import TransportMode
        transport_modes = [opt.transport_mode for opt in options]
        assert TransportMode.GROUND in transport_modes or TransportMode.PRIORITY_GROUND in transport_modes
        
        # Should NOT include air transport (hazardous constraint)
        assert TransportMode.AIR not in transport_modes
        
        # Should have volumetric cost due to fragile nature
        assert any(opt.volumetric_cost > 0 for opt in options), \
            "Fragile items should incur volumetric cost for reinforced packaging"
    
    def test_get_recommended_for_mixed_product(self):
        """
        Getting recommended shipping for mixed product should return cheapest ground option.
        """
        product = Product(
            id="P105",
            name="Electronic Glass Photo Frame",
            weight=1.2,
            volume=0.004,
            product_type=ProductType.MIXED
        )
        order = Order(order_id="O105", products=[product])
        
        # This should return the cheapest valid option, not throw exception
        recommended = self.service.get_recommended_shipping(order)
        
        assert recommended is not None
        assert recommended.total_cost > 0
        
        # Should be a ground-based transport
        from src.models import TransportMode
        assert recommended.transport_mode in [TransportMode.GROUND, TransportMode.PRIORITY_GROUND]
    
    def test_heavy_product_uses_freight(self):
        """Products over 50kg should use freight transport."""
        product = Product(
            id="P106",
            name="Industrial Equipment",
            weight=80.0,
            volume=0.2,
            product_type=ProductType.NORMAL
        )
        order = Order(order_id="O106", products=[product])
        
        options = self.service.calculate_shipping_options(order)
        
        # Should only have freight option
        assert len(options) == 1
        from src.models import TransportMode
        assert options[0].transport_mode == TransportMode.FREIGHT