"""Constraint validators for shipping methods."""

from typing import List, Set
from src.models import Order, TransportMode


class ConstraintValidator:
    """
    Validates which transport modes are available for an order.
    
    VERSION 2.0.1 CHANGES:
    - Fixed regression bug in mixed product constraint validation
    - Restored correct logic for combined hazardous + fragile products
    """
    
    MAX_STANDARD_WEIGHT = 50.0  # kg
    
    @staticmethod
    def get_available_transport_modes(order: Order) -> List[TransportMode]:
        """
        Determine which transport modes are valid for the given order.
        
        FIXED LOGIC (v2.0.1):
        - Start with ground-based options as baseline
        - Add AIR only if no hazardous items present
        - Heavy items require FREIGHT
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
        
        # Step 2: Start with ground-based options as baseline
        candidates = {TransportMode.GROUND, TransportMode.PRIORITY_GROUND}
        
        # Step 3: Add AIR if no hazardous items
        if not order.has_hazardous():
            candidates.add(TransportMode.AIR)
        
        return list(candidates) if candidates else []