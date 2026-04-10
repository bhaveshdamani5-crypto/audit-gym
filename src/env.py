import asyncio
from typing import List, Dict, Any
from .models import (
    Warehouse, Order, Action, InventoryObservation, 
    ResetResponse, StepResponse, generate_demand_patterns, initialize_warehouses
)


class InventoryGymEnv:
    """
    Multi-warehouse inventory management environment.
    Agent decides when and how much to order for each warehouse.
    Strategic tension between holding costs and stockout penalties.
    """
    
    def __init__(self, num_warehouses=1, num_steps=100, lead_time=3, inventory_penalty_factor=1.0):
        self.num_warehouses = num_warehouses
        self.num_steps = num_steps
        self.lead_time = lead_time  # Steps for order to arrive
        self.inventory_penalty_factor = inventory_penalty_factor  # Difficulty: higher = more expensive
        
        self.current_step = 0
        self.warehouses: List[Warehouse] = []
        self.demand_patterns: Dict[int, List[float]] = {}
        self.pending_orders: List[Order] = []
        self.order_id_counter = 0
        self.total_cost = 0.0
        self.last_action = None
        self.total_demand_met = 0.0
        self.total_demand = 0.0

    async def reset(self) -> ResetResponse:
        """Initialize environment for new episode."""
        self.current_step = 0
        self.order_id_counter = 0
        self.total_cost = 0.0
        self.last_action = None
        self.total_demand_met = 0.0
        self.total_demand = 0.0
        self.pending_orders = []
        
        # Initialize warehouses
        self.warehouses = initialize_warehouses(self.num_warehouses)
        
        # Generate demand patterns
        self.demand_patterns = generate_demand_patterns(self.num_warehouses, self.num_steps)
        
        obs = self._get_obs()
        return ResetResponse(observation=obs)

    async def step(self, action: Action) -> StepResponse:
        """
        Process one step of inventory management.
        Agent orders stock, demand is fulfilled, costs are calculated.
        """
        self.current_step += 1
        reward = 0.0
        self.last_action = None
        
        # Process agent's order
        if action.quantity > 0 and action.dest_warehouse < len(self.warehouses):
            order_cost = action.quantity * (1.2 if action.priority == "expedited" else 1.0)
            self.total_cost += order_cost
            reward -= order_cost * 0.01  # Cost penalty
            
            order = Order(
                id=self.order_id_counter,
                origin_warehouse=-1,  # Supplier
                dest_warehouse=action.dest_warehouse,
                quantity=action.quantity,
                steps_remaining=self.lead_time if action.priority == "normal" else 1,
                cost=order_cost
            )
            self.pending_orders.append(order)
            self.order_id_counter += 1
            self.last_action = f"Order {action.quantity:.0f} units to Warehouse-{chr(65+action.dest_warehouse)}"
        
        # Advance pending orders
        arrived_orders = []
        for order in self.pending_orders[:]:
            order.steps_remaining -= 1
            if order.steps_remaining <= 0:
                # Order arrives
                self.warehouses[order.dest_warehouse].inventory += order.quantity
                arrived_orders.append(order)
                self.pending_orders.remove(order)
        
        # Process demand for each warehouse
        for warehouse_id, warehouse in enumerate(self.warehouses):
            demand = self.demand_patterns[warehouse_id][self.current_step]
            self.total_demand += demand
            
            # Fulfill demand if possible
            fulfilled = min(warehouse.inventory, demand)
            self.total_demand_met += fulfilled
            warehouse.inventory -= fulfilled
            
            # Reward for meeting demand
            fulfillment_rate = fulfilled / demand if demand > 0 else 1.0
            reward += fulfillment_rate * 0.5
            
            # Penalty for unmet demand (stockout)
            stockout = max(0, demand - fulfilled)
            reward -= stockout * 0.3
            
            # Holding cost (penalize excess inventory)
            holding_cost = warehouse.inventory * warehouse.holding_cost_per_unit * self.inventory_penalty_factor
            self.total_cost += holding_cost
            reward -= holding_cost * 0.01
            
            # Bonus for good inventory management (not too high, not too low)
            optimal_level = demand * self.lead_time * 1.5
            excess = max(0, warehouse.inventory - optimal_level)
            if excess > 0:
                reward -= excess * 0.001  # Small penalty for over-stocking
            
            # Reward for staying in good range
            if 0.3 * optimal_level < warehouse.inventory < 0.8 * optimal_level:
                reward += 0.05
        
        done = self.current_step >= self.num_steps
        obs = self._get_obs()
        
        return StepResponse(observation=obs, reward=reward, done=done)

    async def state(self) -> Dict[str, Any]:
        """Return current state metrics."""
        total_inventory = sum(w.inventory for w in self.warehouses)
        fulfillment_rate = self.total_demand_met / self.total_demand if self.total_demand > 0 else 0.0
        
        return {
            "step": self.current_step,
            "total_inventory": total_inventory,
            "total_cost": self.total_cost,
            "fulfillment_rate": fulfillment_rate,
            "pending_orders": len(self.pending_orders),
            "avg_warehouse_inventory": total_inventory / len(self.warehouses) if self.warehouses else 0
        }

    def _get_obs(self) -> InventoryObservation:
        """Get current observation."""
        warehouses_data = [
            {
                "id": w.id,
                "name": w.name,
                "inventory": round(w.inventory, 2),
                "capacity": w.capacity,
                "utilization": round(w.inventory / w.capacity, 3),
                "location": w.location
            }
            for w in self.warehouses
        ]
        
        pending_data = [
            {
                "id": o.id,
                "dest_warehouse": o.dest_warehouse,
                "quantity": round(o.quantity, 2),
                "steps_remaining": o.steps_remaining
            }
            for o in self.pending_orders
        ]
        
        # Forecast next 5 steps of demand
        forecasted = []
        for wid in range(self.num_warehouses):
            future_demand = [
                round(self.demand_patterns[wid][self.current_step + i], 2)
                for i in range(1, 6)
                if self.current_step + i < len(self.demand_patterns[wid])
            ]
            forecasted.append({"warehouse_id": wid, "next_5_steps": future_demand})
        
        return InventoryObservation(
            warehouses=warehouses_data,
            pending_orders=pending_data,
            forecasted_demand=forecasted,
            current_step=self.current_step,
            total_cost=round(self.total_cost, 2),
            last_action=self.last_action
        )

    @classmethod
    async def from_docker_image(cls, image_name: str):
        return cls()

    async def close(self):
        pass