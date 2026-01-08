"""Constraint validators for shipping methods."""

from typing import List, Set
from src.models import Order, TransportMode


class ConstraintValidator:
    """
    Validates which transport modes are available for an order.
    
    This fixes the regression introduced in v2.0 where building candidates additively
    caused MIXED products (hazardous + fragile) to lose valid ground transport options.
    """
    
    MAX_STANDARD_WEIGHT = 50.0  # kg
    
    @staticmethod
    def get_available_transport_modes(order: Order) -> List[TransportMode]:
        """
        Determine which transport modes are valid for the given order.
        
        Fixed logic (v2.0.1):
        - Start with the full set of standard modes and remove forbidden ones (subtractive)
        - Freight is only returned if the order exceeds MAX_STANDARD_WEIGHT
        - Fragile items do not *remove* ground options; they may influence priority but
          should not eliminate valid transport modes when combined with hazardous constraints
        """
        # Step 1: Weight constraint - heavy items must use freight
        if order.total_weight() > ConstraintValidator.MAX_STANDARD_WEIGHT:
            return [TransportMode.FREIGHT]
        
        # Step 2: Start with all standard modes
        allowed = {
            TransportMode.AIR,
            TransportMode.GROUND,
            TransportMode.PRIORITY_GROUND
        }
        
        # Step 3: Apply hazardous constraint (forbid AIR)
        if order.has_hazardous():
            allowed.discard(TransportMode.AIR)
        
        # Step 4: Fragile items may prefer AIR, but do not remove other options
        # (No action needed here; preference can be applied at recommendation stage.)
        
        # Return allowed modes as a list
        return list(allowed)
