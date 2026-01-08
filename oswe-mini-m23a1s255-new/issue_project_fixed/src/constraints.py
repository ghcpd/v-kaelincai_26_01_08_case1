"""Constraint validators for shipping methods. (fixed)

Root cause: when an order was both fragile and hazardous the code added
`AIR` for fragile then removed it for hazardous but only added `GROUND`
as a fallback — missing `PRIORITY_GROUND`.

Fix: ensure hazardous orders allow both ground-based services and do not
remove valid ground options when `AIR` was discarded. Preserve fragile
optimization (AIR preference) but do not make it exclusive.
"""

from typing import List, Set
from src.models import Order, TransportMode


class ConstraintValidator:
    """
    Validates which transport modes are available for an order.
    """

    MAX_STANDARD_WEIGHT = 50.0  # kg

    @staticmethod
    def get_available_transport_modes(order: Order) -> List[TransportMode]:
        """
        Determine which transport modes are valid for the given order.

        Behavior (fixed):
        - Heavy items (> MAX_STANDARD_WEIGHT) -> FREIGHT only
        - Hazardous items -> prohibit AIR, allow ground-based services
        - Fragile items -> prefer AIR but do not remove other valid modes
        """
        # Overweight -> freight only (short-circuit)
        if order.total_weight() > ConstraintValidator.MAX_STANDARD_WEIGHT:
            return [TransportMode.FREIGHT]

        # Start from an explicit baseline of ground-capable modes so that
        # mixed combinations always have ground options available.
        candidates: Set[TransportMode] = {
            TransportMode.GROUND,
            TransportMode.PRIORITY_GROUND,
        }

        # Fragile items may *prefer* AIR (optimization) but that should not
        # remove ground-based options.
        if order.has_fragile() and not order.has_hazardous():
            # Only add AIR if hazardous constraint does not apply
            candidates.add(TransportMode.AIR)

        # Hazardous items cannot use AIR — ensure AIR is not present and
        # keep ground-based options available (both standard and priority).
        if order.has_hazardous():
            candidates.discard(TransportMode.AIR)
            candidates.update({TransportMode.GROUND, TransportMode.PRIORITY_GROUND})

        # If no special constraints applied, also allow AIR as an option
        if not order.has_fragile() and not order.has_hazardous():
            candidates.update({TransportMode.AIR, TransportMode.GROUND, TransportMode.PRIORITY_GROUND})

        return list(candidates) if candidates else []
