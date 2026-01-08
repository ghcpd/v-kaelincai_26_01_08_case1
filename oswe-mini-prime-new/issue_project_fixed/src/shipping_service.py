"""Main shipping service for calculating shipping options."""

from typing import List
from src.models import Order, ShippingMethod, TransportMode
from src.constraints import ConstraintValidator
from src.calculator import VolumetricCalculator
from src.exceptions import NoValidShippingMethodFoundException


class ShippingService:
    """Service for determining available shipping methods and costs."""

    # Estimated delivery days for each transport mode
    DELIVERY_ESTIMATES = {
        TransportMode.AIR: 1,
        TransportMode.PRIORITY_GROUND: 2,
        TransportMode.GROUND: 5,
        TransportMode.FREIGHT: 7
    }

    def calculate_shipping_options(self, order: Order) -> List[ShippingMethod]:
        """
        Calculate all available shipping options for an order.

        Returns a list of ShippingMethod objects sorted by cost.
        Raises NoValidShippingMethodFoundException if no valid methods exist.
        """
        # Step 1: Validate constraints to get available transport modes
        available_modes = ConstraintValidator.get_available_transport_modes(order)

        if not available_modes:
            raise NoValidShippingMethodFoundException(
                f"No valid shipping method found for order {order.order_id}. "
                f"Order has hazardous={order.has_hazardous()}, fragile={order.has_fragile()}, "
                f"weight={order.total_weight()}kg"
            )

        # Step 2: Calculate costs for each available mode
        shipping_options = []
        total_weight = order.total_weight()
        volumetric_weight = VolumetricCalculator.calculate_volumetric_weight(order)

        for mode in available_modes:
            base_cost, volumetric_cost, total_cost = VolumetricCalculator.calculate_cost(
                total_weight, 
                volumetric_weight, 
                mode
            )

            shipping_method = ShippingMethod(
                transport_mode=mode,
                base_cost=base_cost,
                volumetric_cost=volumetric_cost,
                total_cost=total_cost,
                estimated_days=self.DELIVERY_ESTIMATES.get(mode, 5)
            )
            shipping_options.append(shipping_method)

        # Step 3: Sort by total cost (cheapest first)
        shipping_options.sort(key=lambda x: x.total_cost)

        return shipping_options

    def get_recommended_shipping(self, order: Order) -> ShippingMethod:
        """
        Get the recommended (cheapest) shipping method for an order.

        Raises NoValidShippingMethodFoundException if no valid methods exist.
        """
        options = self.calculate_shipping_options(order)
        return options[0]  # First option is cheapest due to sorting