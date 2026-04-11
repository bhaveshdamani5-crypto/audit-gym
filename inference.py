import asyncio
import os
from typing import List
from openai import OpenAI
from src.env import InventoryGymEnv
from src.models import Action

# Configuration
TASK_NAME = os.getenv("TASK_NAME", "inventory-hard")
BENCHMARK = "InventoryGym-v1"
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
MAX_STEPS = 100
TEMPERATURE = 0.7
MAX_TOKENS = 100

# Task configurations
TASK_CONFIGS = {
    "inventory-easy": {"num_warehouses": 1, "num_steps": 50, "lead_time": 5, "inventory_penalty_factor": 1.0},
    "inventory-medium": {"num_warehouses": 3, "num_steps": 100, "lead_time": 3, "inventory_penalty_factor": 1.5},
    "inventory-hard": {"num_warehouses": 5, "num_steps": 100, "lead_time": 2, "inventory_penalty_factor": 2.0}
}

config = TASK_CONFIGS.get(TASK_NAME, TASK_CONFIGS["inventory-hard"])
SUCCESS_SCORE_THRESHOLD = 0.6

SYSTEM_PROMPT = """
You are a supply chain optimization expert managing a multi-warehouse inventory network.

Your goal: Minimize costs while meeting customer demand across all warehouses.

State information provided each step:
- Current inventory levels at each warehouse
- Pending orders and their arrival times
- Forecasted demand for next 5 steps
- Running total cost

Action: Place a replenishment order
Format: "order <warehouse_id> <quantity> [priority]"
Example: "order 0 500" or "order 2 300 expedited"

Constraints:
- Each warehouse has a 3000 unit capacity
- Standard orders take 2-3 steps to arrive (lead time)
- Expedited orders arrive next step but cost 20% more
- Holding cost: 0.5 per unit per step (expensive!)
- Stockout penalty: -0.3 per unmet unit

Strategy:
1. Monitor forecasted demand for each warehouse
2. Track pending orders and their ETAs
3. Order enough to meet demand but avoid over-stocking
4. Balance between holding costs and stockout penalties
5. Use expedited orders strategically during spikes

Optimize for: High fulfillment rate + Low total cost
"""

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: str = None):
    done_str = "true" if done else "false"
    error_str = error if error else "null"
    print(f"[STEP] step={step} action={action!r} reward={reward:.2f} done={done_str} error={error_str}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list):
    success_str = "true" if success else "false"
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={success_str} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

def get_model_message(client: OpenAI, step: int, observation, last_reward: float, history: list) -> str:
    # Format observation for LLM
    warehouses_info = "\n".join([
        f"Warehouse {w['id']}: {w['inventory']:.0f}/{w['capacity']} units (utilization: {w['utilization']:.1%})"
        for w in observation.warehouses
    ])
    
    pending_info = "None"
    if observation.pending_orders:
        pending_info = "\n".join([
            f"Order {o['id']}: {o['quantity']:.0f} units to Warehouse {o['dest_warehouse']} (arrives in {o['steps_remaining']} steps)"
            for o in observation.pending_orders
        ])
    
    forecast_info = "\n".join([
        f"Warehouse {f['warehouse_id']}: {f['next_5_steps']}"
        for f in observation.forecasted_demand
    ])
    
    history_context = "\n".join(history[-3:]) if history else "None"
    
    user_prompt = f"""
Step: {step}
Last reward: {last_reward:.2f}
Total cost so far: ${observation.total_cost:.2f}

Current Inventory:
{warehouses_info}

Pending Orders:
{pending_info}

5-Step Demand Forecast:
{forecast_info}

Recent History:
{history_context}

Decide your next ordering action:
"""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else "order 0 250"
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "order 0 250"

async def run_single_task(task_id: str, task_config: dict, client: OpenAI) -> tuple:
    """Run a single task and return (success, steps, score, rewards)"""
    env = InventoryGymEnv(**task_config)
    
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    
    try:
        result = await env.reset()
        last_reward = 0.0
        max_steps = task_config.get('num_steps', 100)
        
        for step in range(1, max_steps + 1):
            if result.done:
                break
            
            # Parse warehouse and quantity from action
            action_text = get_model_message(client, step, result.observation, last_reward, history)
            
            # Simple parser: "order <warehouse> <quantity> [priority]"
            parts = action_text.lower().split()
            warehouse_id = 0
            quantity = 250
            priority = "normal"
            
            try:
                if "order" in action_text.lower():
                    if len(parts) >= 3:
                        warehouse_id = int(parts[1])
                        quantity = float(parts[2])
                        if len(parts) > 3:
                            priority = parts[3]
            except (ValueError, IndexError):
                pass
            
            action = Action(dest_warehouse=warehouse_id, quantity=quantity, priority=priority)
            result = await env.step(action)
            
            reward = result.reward or 0.0
            done = result.done
            
            rewards.append(reward)
            steps_taken = step
            last_reward = reward
            
            log_step(step=step, action=action_text, reward=reward, done=done, error=None)
            history.append(f"Step {step}: {action_text} -> reward {reward:.2f}")
            
            if done:
                break
        
        # Final scoring
        final_state = await env.state()
        score = final_state.get('fulfillment_rate', 0.0) * 0.6 + (1.0 - min(final_state.get('total_cost', 1e9) / 50000, 1.0)) * 0.4
        score = max(0.0, min(1.0, score))
        success = score >= SUCCESS_SCORE_THRESHOLD
    
    finally:
        try:
            await env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error: {e}", flush=True)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    
    return (success, steps_taken, score, rewards)

async def main() -> None:
    """Run all three tasks: easy, medium, hard"""
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    # Task order matching openenv.yaml definitions
    task_order = ["inventory-easy", "inventory-medium", "inventory-hard"]
    
    # Allow override via environment variable for single-task runs
    single_task = os.getenv("TASK_NAME", None)
    if single_task and single_task in TASK_CONFIGS:
        task_order = [single_task]
    
    for task_id in task_order:
        if task_id in TASK_CONFIGS:
            task_config = TASK_CONFIGS[task_id]
            await run_single_task(task_id, task_config, client)

if __name__ == "__main__":
    asyncio.run(main())