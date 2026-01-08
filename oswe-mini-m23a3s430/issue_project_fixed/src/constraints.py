"""Constraint validators for shipping methods."""

from typing import List, Set
from src.models import Order, TransportMode


class ConstraintValidator:
    """
    Validates which transport modes are available for an order.
    
    VERSION 2.0 CHANGES:
    - Introduced new Priority Ground service
    - Refactored to use TransportMode abstraction
    - Added optimization logic for fragile items
    """
    
    MAX_STANDARD_WEIGHT = 50.0  # kg
    
    @staticmethod
    def get_available_transport_modes(order: Order) -> List[TransportMode]:
        """
        Determine which transport modes are valid for the given order.
        
        NEW LOGIC (v2.0):
        - Check each constraint type and build up candidate list
        - Fragile items prefer AIR to reduce vibration time
        - Hazardous items prohibit AIR
        - Overweight items require FREIGHT
        """
        # Start with all available modes in v2.0
        all_modes = [
            TransportMode.AIR,
            TransportMode.GROUND,
            TransportMode.PRIORITY_GROUND,
            TransportMode.FREIGHT
        ]
        
        # Track candidates as we apply constraints
        candidates = set()
        
        # Step 1: Check weight constraint first
        if order.total_weight() > ConstraintValidator.MAX_STANDARD_WEIGHT:
            # Heavy items must use freight
            candidates = {TransportMode.FREIGHT}
            return list(candidates)
        
        # Step 2: Fragile items prefer AIR
        if order.has_fragile():
            # Fragile items should use AIR to minimize transit time and vibration
            candidates.add(TransportMode.AIR)
        
        # Step 3: Check hazardous constraint
        if order.has_hazardous():
            # Hazardous items CANNOT use air transport
            candidates.discard(TransportMode.AIR)
            
            # Ensure ground-based options are available for hazardous items
            # NOTE: v2.0 bug: previously only GROUND was added which omitted PRIORITY_GROUND
            candidates.update({TransportMode.GROUND, TransportMode.PRIORITY_GROUND})
        
        # Step 4: If no specific constraints applied, allow all standard modes
        if not candidates:
            candidates = {
                TransportMode.AIR,
                TransportMode.GROUND,
                TransportMode.PRIORITY_GROUND
            }
        
        return list(candidates) if candidates else []