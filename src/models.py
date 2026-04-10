"""
Pydantic models for InventoryGym-v1 OpenEnv environment
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import random
from datetime import datetime, timedelta


class Warehouse(BaseModel):
    """Warehouse state"""
    id: int
    name: str
    inventory: float
    capacity: float
    holding_cost_per_unit: float
    location: str


class Order(BaseModel):
    """Pending order in transit"""
    id: int
    origin_warehouse: int
    dest_warehouse: int
    quantity: float
    steps_remaining: int
    cost: float


class Action(BaseModel):
    """Agent action: order replenishment from supplier"""
    dest_warehouse: int
    quantity: float
    priority: str = "normal"  # "normal" or "expedited" (costs extra)


class InventoryObservation(BaseModel):
    """Current state of inventory system"""
    warehouses: List[Dict[str, Any]]
    pending_orders: List[Dict[str, Any]]
    forecasted_demand: List[Dict[str, Any]]
    current_step: int
    total_cost: float
    last_action: Optional[str] = None


class ResetResponse(BaseModel):
    """OpenEnv reset response"""
    observation: InventoryObservation


class StepResponse(BaseModel):
    """OpenEnv step response"""
    observation: InventoryObservation
    reward: float
    done: bool


def generate_demand_patterns(num_warehouses: int, num_steps: int) -> Dict[int, List[float]]:
    """Generate realistic demand patterns with seasonality and trends."""
    demand_patterns = {}
    
    for warehouse_id in range(num_warehouses):
        base_demand = random.uniform(150, 400)
        trend = random.uniform(-0.3, 0.3)  # Linear trend
        seasonality_period = random.choice([7, 14, 30])
        
        demands = []
        for step in range(num_steps + 100):
            season_factor = 1.0 + 0.4 * (1.0 if (step % seasonality_period) < seasonality_period / 2 else -0.5)
            noise = random.gauss(0, base_demand * 0.15)
            demand = max(50, base_demand + trend * step + noise * season_factor)
            demands.append(demand)
        
        demand_patterns[warehouse_id] = demands
    
    return demand_patterns


def initialize_warehouses(num_warehouses: int) -> List[Warehouse]:
    """Initialize warehouse network."""
    warehouses = []
    locations = ["North", "South", "East", "West", "Central"]
    
    for i in range(num_warehouses):
        warehouse = Warehouse(
            id=i,
            name=f"Warehouse-{chr(65+i)}",
            inventory=random.uniform(800, 1500),
            capacity=3000,
            holding_cost_per_unit=0.5,
            location=locations[min(i, len(locations)-1)]
        )
        warehouses.append(warehouse)
    
    return warehouses