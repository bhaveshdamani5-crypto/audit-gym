import asyncio
import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

# Load local .env file if it exists
load_dotenv()
from src.env import InventoryGymEnv
from src.models import Action

# Configuration from Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")

TASK_NAME = os.getenv("TASK_NAME", "inventory-medium")
BENCHMARK = "InventoryGym-v1"

# Task Mapping
CONFIGS = {
    "inventory-easy": {"num_warehouses": 1, "num_steps": 50, "lead_time": 5},
    "inventory-medium": {"num_warehouses": 3, "num_steps": 100, "lead_time": 4},
    "inventory-hard": {"num_warehouses": 5, "num_steps": 100, "lead_time": 3}
}

config = CONFIGS.get(TASK_NAME, CONFIGS["inventory-medium"])
MAX_STEPS = config["num_steps"]
SUCCESS_SCORE_THRESHOLD = 0.8 

SYSTEM_PROMPT = """
You are a Lead Supply Chain Strategist managing a multi-node warehouse network.
GOAL: Maintain Service Level > 92% across all nodes while minimizing operational costs.

COMMANDS:
1. 'order <dest_id> <qty> [priority]' -> Replenish from Global Supplier.
2. 'transfer <from_id> <to_id> <qty> [priority]' -> Transship between warehouses.

PRIORITY: 'normal' (standard lead time) or 'expedited' (1-cycle delivery, high cost).

STRICT RESPONSE FORMAT: <command> <args...>
Example: 'order 0 500 expedited' or 'transfer 2 0 300 normal'
"""

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: str = "null"):
    done_str = "true" if done else "false"
    error_str = error if error else "null"
    print(f"[STEP] step={step} action={action!r} reward={reward:.2f} done={done_str} error={error_str}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float], task: str):
    success_str = "true" if success else "false"
    clamped_score = max(0.01, min(0.99, score))
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] task={task} success={success_str} steps={steps} score={clamped_score:.2f} rewards={rewards_str}", flush=True)

async def main():
    if not API_KEY:
        log_end(False, 0, 0.001, [], TASK_NAME)
        return

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = InventoryGymEnv(**config)
    
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    rewards = []
    steps_taken = 0
    success = False
    score = 0.0

    try:
        reset_resp = await env.reset()
        obs = reset_resp.observation

        for step in range(1, MAX_STEPS + 1):
            try:
                state_summary = {
                    "cycle": obs.current_step,
                    "service_level": f"{obs.service_level:.1%}",
                    "nodes": obs.warehouses,
                    "forecast": obs.forecasted_demand,
                    "pending": obs.pending_orders,
                    "status": obs.last_action
                }
                
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Current State: {json.dumps(state_summary)}"}
                    ],
                    max_tokens=60,
                    temperature=0.1
                )
                action_text = response.choices[0].message.content.strip().lower()
            except Exception as e:
                action_text = "order 0 0"

            # Parse action logic for order and transfer
            parts = action_text.split()
            dest_id, origin_id, qty, priority = 0, -1, 0.0, "normal"
            
            try:
                if "order" in parts:
                    dest_id = int(parts[1])
                    qty = float(parts[2])
                    if len(parts) > 3: priority = parts[3] if parts[3] in ["normal", "expedited"] else "normal"
                elif "transfer" in parts:
                    origin_id = int(parts[1])
                    dest_id = int(parts[2])
                    qty = float(parts[3])
                    if len(parts) > 4: priority = parts[4] if parts[4] in ["normal", "expedited"] else "normal"
            except:
                pass

            action = Action(dest_warehouse=dest_id, origin_warehouse=origin_id, quantity=qty, priority=priority)
            step_resp = await env.step(action)
            obs = step_resp.observation
            
            reward = step_resp.reward
            rewards.append(reward)
            steps_taken = step
            
            log_step(step=step, action=action_text, reward=reward, done=step_resp.done)

            if step_resp.done:
                break

        final_state = await env.state()
        from src.grader import grade_easy, grade_medium, grade_hard
        if TASK_NAME == "inventory-easy": score = grade_easy(final_state)
        elif TASK_NAME == "inventory-medium": score = grade_medium(final_state)
        else: score = grade_hard(final_state)
        
        success = score >= 0.7 

    finally:
        await env.close()
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards, task=TASK_NAME)

if __name__ == "__main__":
    import json
    asyncio.run(main())