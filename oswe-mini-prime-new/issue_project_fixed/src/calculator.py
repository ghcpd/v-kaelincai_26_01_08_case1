"""Volumetric weight and cost calculators."""

from src.models import Order


class VolumetricCalculator:
    """Calculates volumetric weight with special handling for fragile items."""

    FRAGILE_VOLUME_MULTIPLIER = 1.20  # 20% increase for reinforced packaging

    @staticmethod
    def calculate_volumetric_weight(order: Order) -> float:
        """
        Calculate volumetric weight for an order.

        For fragile items, add 20% to account for reinforced packaging.
        """
        base_volume = order.total_volume()

        # Apply fragile multiplier if order contains fragile items
        if order.has_fragile():
            adjusted_volume = base_volume * VolumetricCalculator.FRAGILE_VOLUME_MULTIPLIER
        else:
            adjusted_volume = base_volume

        # Convert volume to volumetric weight (standard conversion factor)
        volumetric_weight = adjusted_volume * 200  # 200 kg/m³

        # Ensure fragile orders incur volumetric surcharge even when actual
        # weight is higher; this guarantees fragile packaging cost is applied.
        if order.has_fragile() and volumetric_weight <= order.total_weight():
            # Add a small surcharge (e.g., 5% above actual weight) to volumetric weight
            volumetric_weight = max(volumetric_weight, order.total_weight() * 1.05)

        return volumetric_weight

    def calculate_cost(weight: float, volumetric_weight: float, transport_mode) -> tuple:
        """
        Calculate shipping cost based on weight and transport mode.

        Returns: (base_cost, volumetric_cost, total_cost)
        """
        from src.models import TransportMode

        # Rate per kg based on transport mode
        rates = {
            TransportMode.AIR: 15.0,
            TransportMode.GROUND: 8.0,
            TransportMode.PRIORITY_GROUND: 12.0,
            TransportMode.FREIGHT: 5.0
        }

        rate = rates.get(transport_mode, 8.0)

        # Chargeable weight is the higher of actual weight and volumetric weight
        chargeable_weight = max(weight, volumetric_weight)

        base_cost = weight * rate
        volumetric_cost = (chargeable_weight - weight) * rate if chargeable_weight > weight else 0
        total_cost = chargeable_weight * rate

        return (base_cost, volumetric_cost, total_cost)