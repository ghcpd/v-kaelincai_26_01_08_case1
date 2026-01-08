"""Constraint validators for shipping methods (FIXED v2.0.1)."""

from typing import List
from src.models import Order, TransportMode


class ConstraintValidator:
    """
    Validates which transport modes are available for an order.

    FIX: Restored a baseline-then-filter approach to avoid missing
    valid ground-based transport options for mixed (hazardous+fragile)
    products. This keeps the fragile optimization as a priority hint
    but ensures all valid modes are considered.
    """

    MAX_STANDARD_WEIGHT = 50.0  # kg

    @staticmethod
    def get_available_transport_modes(order: Order) -> List[TransportMode]:
        """
        Determine which transport modes are valid for the given order.

        FIXED LOGIC (v2.0.1):
        - If overweight -> FREIGHT only
        - Start with the baseline set of standard modes
        - Remove modes forbidden by constraints (e.g., AIR if hazardous)
        - Fragile items may *prefer* AIR but do NOT remove other valid modes
        """
        # Step 1: Weight constraint (heavy items require freight)
        if order.total_weight() > ConstraintValidator.MAX_STANDARD_WEIGHT:
            return [TransportMode.FREIGHT]

        # Step 2: Start from baseline allowed standard modes
        allowed = {
            TransportMode.AIR,
            TransportMode.GROUND,
            TransportMode.PRIORITY_GROUND,
        }

        # Step 3: Apply hazardous constraint - remove AIR when hazardous
        if order.has_hazardous():
            allowed.discard(TransportMode.AIR)

        # Note: Fragile items do not remove any modes; they may affect
        # prioritization or cost (handled elsewhere).

        return list(allowed) if allowed else []
