"""Data models for shipping system."""

from enum import Enum
from typing import List
from dataclasses import dataclass


class ProductType(Enum):
    """Product classification types."""
    NORMAL = "normal"
    HAZARDOUS = "hazardous"  # Batteries, sprays, etc.
    FRAGILE = "fragile"      # Glass, ceramics, etc.
    MIXED = "mixed"          # Both hazardous and fragile (e.g., battery-powered glass lamp)


class TransportMode(Enum):
    """Available transport modes."""
    AIR = "air"
    GROUND = "ground"
    FREIGHT = "freight"
    PRIORITY_GROUND = "priority_ground"  # NEW: Added in v2.0


@dataclass
class Product:
    """Represents a product in an order."""
    id: str
    name: str
    weight: float  # in kg
    volume: float  # in cubic meters
    product_type: ProductType
    
    def is_hazardous(self) -> bool:
        """Check if product is hazardous."""
        return self.product_type in [ProductType.HAZARDOUS, ProductType.MIXED]
    
    def is_fragile(self) -> bool:
        """Check if product is fragile."""
        return self.product_type in [ProductType.FRAGILE, ProductType.MIXED]


@dataclass
class Order:
    """Represents a customer order."""
    order_id: str
    products: List[Product]
    
    def total_weight(self) -> float:
        """Calculate total weight of the order."""
        return sum(p.weight for p in self.products)
    
    def total_volume(self) -> float:
        """Calculate total volume of the order."""
        return sum(p.volume for p in self.products)
    
    def has_hazardous(self) -> bool:
        """Check if order contains any hazardous products."""
        return any(p.is_hazardous() for p in self.products)
    
    def has_fragile(self) -> bool:
        """Check if order contains any fragile products."""
        return any(p.is_fragile() for p in self.products)


@dataclass
class ShippingMethod:
    """Represents a shipping method with calculated cost."""
    transport_mode: TransportMode
    base_cost: float
    volumetric_cost: float
    total_cost: float
    estimated_days: int