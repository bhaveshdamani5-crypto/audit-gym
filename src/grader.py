"""
Grader functions for evaluating agent performance on InventoryGym tasks.
Each grader returns a score between 0.0 and 1.0 based on final performance.
"""


def grade_easy(state):
    """
    Grade easy task: Single warehouse, predictable demand, long lead times.
    Easy for agents to learn basic ordering patterns.
    """
    return _grade_inventory_task(
        total_cost=state.get('total_cost', 1e9),
        fulfillment_rate=state.get('fulfillment_rate', 0.0),
        cost_budget=5000.0,  # Expected cost for baseline agent
        min_fulfillment=0.90
    )


def grade_medium(state):
    """
    Grade medium task: 3 warehouses, variable demand, medium lead times.
    Requires learning to coordinate orders across locations.
    """
    return _grade_inventory_task(
        total_cost=state.get('total_cost', 1e9),
        fulfillment_rate=state.get('fulfillment_rate', 0.0),
        cost_budget=12000.0,
        min_fulfillment=0.85
    )


def grade_hard(state):
    """
    Grade hard task: 5 warehouses, seasonal demand, short lead times.
    Requires sophisticated forecasting and multi-warehouse coordination.
    """
    return _grade_inventory_task(
        total_cost=state.get('total_cost', 1e9),
        fulfillment_rate=state.get('fulfillment_rate', 0.0),
        cost_budget=30000.0,
        min_fulfillment=0.80
    )


def _grade_inventory_task(total_cost, fulfillment_rate, cost_budget, min_fulfillment):
    """
    Compute composite score based on:
    - Fulfillment rate (0.6 weight): How much demand was met
    - Cost efficiency (0.4 weight): How low costs were relative to budget
    
    Normalized to 0.0-1.0 range.
    """
    # Fulfillment score: linear from min_fulfillment to 1.0
    if fulfillment_rate >= 1.0:
        fulfillment_score = 1.0
    elif fulfillment_rate >= min_fulfillment:
        fulfillment_score = 0.5 + 0.5 * (fulfillment_rate - min_fulfillment) / (1.0 - min_fulfillment)
    else:
        fulfillment_score = 0.5 * (fulfillment_rate / min_fulfillment)
    
    # Cost efficiency score: lower cost is better
    cost_efficiency = min(1.0, cost_budget / max(total_cost, 1.0))
    
    # Composite score with weights
    score = 0.6 * fulfillment_score + 0.4 * cost_efficiency
    
    return max(0.0, min(1.0, score))