"""Constraint validators for shipping methods."""

from typing import List, Set
from src.models import Order, TransportMode


class ConstraintValidator:
    """
    Validates which transport modes are available for an order.
    
    VERSION 2.0.1 CHANGES (FIXED):
    - Fixed regression in mixed product handling
    - Now correctly returns both GROUND and PRIORITY_GROUND for hazardous+fragile items
    - Uses intersection-based logic when multiple constraints apply simultaneously
    """
    
    MAX_STANDARD_WEIGHT = 50.0  # kg
    
    @staticmethod
    def get_available_transport_modes(order: Order) -> List[TransportMode]:
        """
        Determine which transport modes are valid for the given order.
        
        FIXED LOGIC (v2.0.1):
        - Use intersection-based approach for handling multiple constraints
        - When both hazardous and fragile constraints apply, find modes that satisfy both
        - This ensures mixed products return ground-based options
        """
        # Step 1: Check weight constraint first
        if order.total_weight() > ConstraintValidator.MAX_STANDARD_WEIGHT:
            # Heavy items must use freight only
            return [TransportMode.FREIGHT]
        
        # For non-heavy items, limit to standard modes
        all_modes = {
            TransportMode.AIR,
            TransportMode.GROUND,
            TransportMode.PRIORITY_GROUND
        }
        
        # Step 2: Apply hazardous constraint (remove prohibited modes)
        allowed_by_hazardous = all_modes.copy()
        if order.has_hazardous():
            allowed_by_hazardous.discard(TransportMode.AIR)
        
        # Step 3: Apply fragile constraint (select preferred modes)
        allowed_by_fragile = all_modes.copy()
        if order.has_fragile():
            # Fragile items prefer AIR, but if not available, allow ground options
            # This is important for mixed products
            pass  # All modes are acceptable for fragile, but AIR is preferred
        
        # Step 4: Combine constraints using intersection
        # If no fragile constraint, use hazardous filtering
        if order.has_fragile() and order.has_hazardous():
            # MIXED case: Must satisfy BOTH constraints
            # Hazardous removes AIR, so we get ground-based options
            candidates = allowed_by_hazardous & allowed_by_fragile
        elif order.has_hazardous():
            # Only hazardous: Use hazardous filtering
            candidates = allowed_by_hazardous
        elif order.has_fragile():
            # Only fragile: Prefer AIR, but all modes available
            candidates = allowed_by_fragile
        else:
            # No constraints: All standard modes available
            candidates = {
                TransportMode.AIR,
                TransportMode.GROUND,
                TransportMode.PRIORITY_GROUND
            }
        
        return list(candidates) if candidates else []
