#!/usr/bin/env python3
"""
InventoryGym-v1 Hugging Face Space - Interactive Streamlit UI
Demonstrates OpenEnv environment for supply chain optimization
"""

import streamlit as st
import asyncio
from src.env import InventoryGymEnv
from src.models import Action
from src.grader import grade_easy, grade_medium, grade_hard

# Helper function to run async code in Streamlit
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# Page config
st.set_page_config(
    page_title="InventoryGym-v1",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF6B6B;
    }
    .success-box {
        background-color: #f0fdf4;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #22c55e;
    }
    .info-box {
        background-color: #f0f9ff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #0284c7;
    }
    .header-title {
        color: #1f2937;
        font-size: 2.5em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'env_state' not in st.session_state:
    st.session_state.env_state = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'total_reward' not in st.session_state:
    st.session_state.total_reward = 0.0
if 'history' not in st.session_state:
    st.session_state.history = []

# Header
st.markdown('<p class="header-title">� InventoryGym-v1: Supply Chain Intelligence</p>', unsafe_allow_html=True)
st.markdown("**An OpenEnv environment for multi-warehouse inventory optimization**")
st.divider()

# Sidebar navigation
with st.sidebar:
    st.markdown("### 📋 Navigation")
    page = st.radio("Select Section:", 
        ["🏠 Home", "📚 OpenEnv Spec", "📊 Task Levels", "🎮 Environment Info"])

# ============ HOME PAGE ============
if page == "🏠 Home":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### What is InventoryGym-v1?")
        st.write("""
        InventoryGym is a real-world OpenEnv environment for training AI agents to optimize 
        multi-warehouse inventory management. Agents must balance two competing objectives:
        
        **The Challenge:** Minimize costs while maximizing demand fulfillment
        
        - 📈 **Holding costs**: Every unit in inventory costs money per step
        - 📉 **Stockout penalties**: Unmet demand loses sales
        - ⏱️ **Lead times**: Orders take 2-5 steps to arrive
        - 🎯 **Multi-location**: Coordinate across 1-5 warehouses
        """)
        
        st.markdown("### Why This Matters")
        st.info("""
        Unlike classification tasks, agents don't learn a single "right answer."
        They learn to **discover the Pareto frontier** between cost and service:
        - Random agent: 30% fulfillment, $50k cost → score 0.15
        - Smart agent: 95% fulfillment, $12k cost → score 0.90+
        
        **Learning emerges naturally through trade-off discovery.**
        """)
    
    with col2:
        st.markdown("### 📊 Key Metrics")
        st.metric("Warehouses", "1-5", delta="Per Task")
        st.metric("Demand Pattern", "Non-stationary", delta="Seasonal + Trend")
        st.metric("Episode Length", "50-100", delta="Steps")

# ============ OPENENV SPEC ============
elif page == "📚 OpenEnv Spec":
    st.markdown("### 📚 Full OpenEnv Specification")
    
    tab1, tab2, tab3 = st.tabs(["🔹 Models", "🔄 Methods", "📡 Config"])
    
    with tab1:
        st.markdown("#### Pydantic Models")
        st.code("""
class Action(BaseModel):
    dest_warehouse: int
    quantity: float
    priority: str  # "normal" or "expedited"

class InventoryObservation(BaseModel):
    warehouses: List[Dict]
    pending_orders: List[Dict]
    forecasted_demand: List[Dict]
    current_step: int
    total_cost: float

class ResetResponse(BaseModel):
    observation: InventoryObservation

class StepResponse(BaseModel):
    observation: InventoryObservation
    reward: float
    done: bool
        """, language="python")
    
    with tab2:
        st.markdown("#### Core Methods")
        st.code("""
async reset() -> ResetResponse
async step(action: Action) -> StepResponse
async state() -> Dict[str, Any]
        """, language="python")
    
    with tab3:
        st.markdown("#### openenv.yaml")
        st.code("""
name: InventoryGym
version: v1
models:
  - src.models.Action
  - src.models.InventoryObservation
environment: src.env:InventoryGymEnv
        """, language="yaml")

# ============ TASK LEVELS ============
elif page == "📊 Task Levels":
    st.markdown("### 📊 Task Difficulty Levels")
    
    tasks = [
        {"name": "Easy", "warehouses": 1, "lead": 5, "steps": 50},
        {"name": "Medium", "warehouses": 3, "lead": 3, "steps": 100},
        {"name": "Hard", "warehouses": 5, "lead": 2, "steps": 100}
    ]
    
    cols = st.columns(3)
    for i, task in enumerate(tasks):
        with cols[i]:
            st.metric(task["name"], f"{task['warehouses']} warehouse(s)")
            st.metric("Lead Time", f"{task['lead']} steps")
            st.metric("Episode", f"{task['steps']} steps")

# ============ ENVIRONMENT INFO ============
elif page == "🎮 Environment Info":
    st.markdown("### 🎮 Environment Architecture")
    
    st.markdown("#### Reward Function")
    st.code("""
Fulfillment:     +0.5 × (fulfilled / demand)
Stockout penalty: -0.3 × unmet_demand
Holding cost:    -0.01 × inventory
    """)
    
    st.markdown("#### Expected Performance")
    st.dataframe({
        "Model": ["Random", "GPT-3.5", "GPT-4", "Reasoning"],
        "Easy": ["0.20", "0.60", "0.82", "0.92"],
        "Medium": ["0.10", "0.45", "0.72", "0.85"],
        "Hard": ["0.05", "0.35", "0.60", "0.78+"]
    })

st.divider()
st.caption("InventoryGym-v1 | OpenEnv Hackathon | Multi-warehouse Inventory Optimization")
    st.markdown("### 🎮 Interactive Environment Explorer")
    st.write("Test the OpenEnv environment with manual actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Task Configuration")
        difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])
        
        config_map = {
            "Easy": {"num_total": 100, "num_fraud": 1, "num_red_herring": 5, "max_steps": 50},
            "Medium": {"num_total": 500, "num_fraud": 3, "num_red_herring": 25, "max_steps": 100},
            "Hard": {"num_total": 1000, "num_fraud": 5, "num_red_herring": 50, "max_steps": 200}
        }
        config = config_map[difficulty]
        
        # Display config details
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Transactions", config["num_total"])
        col_b.metric("Frauds", config["num_fraud"])
        col_c.metric("Red Herrings", config["num_red_herring"])
    
    with col2:
        st.markdown("#### Episode Control")
        if st.button("🔄 Reset Environment", use_container_width=True):
            st.session_state.env_state = config
            st.session_state.current_step = 0
            st.session_state.total_reward = 0.0
            st.session_state.history = []
            st.success("✅ Environment reset!")
    
    if st.session_state.env_state:
        st.divider()
        
        st.markdown("#### ➡️ Take an Action")
        action_type = st.selectbox("Action Type", ["Query", "Verify", "Flag"])
        
        if action_type == "Query":
            field = st.selectbox("Field", ["amount"])
            operator = st.selectbox("Operator", [">", "<"])
            value = st.number_input("Value", value=5000.0)
            action_msg = f"query {field} {operator} {value}"
        elif action_type == "Verify":
            tx_id = st.number_input("Transaction ID", min_value=0, value=0)
            action_msg = f"verify id {tx_id}"
        else:  # Flag
            tx_id = st.number_input("Transaction ID to Flag", min_value=0, value=0)
            action_msg = f"flag id {tx_id}"
        
        if st.button("Execute Action", use_container_width=True, type="primary"):
            st.info(f"Action: {action_msg}")
            st.caption("Demo mode - showing sample execution")

# ============ API & OPENENV SPEC ============
elif page == "📚 API & OpenEnv Spec":
    st.markdown("### 📚 OpenEnv API Documentation")
    st.write("Complete OpenEnv specification and Swagger-like API reference")
    
    # Tabs for API sections
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Models", "🔄 Methods", "📡 OpenENV Spec", "💬 Messages"])
    
    with tab1:
        st.markdown("#### 🔹 Pydantic Models")
        
        st.markdown("**Action** - Agent's command")
        st.json({
            "message": "query amount > 5000"
        })
        
        st.markdown("**Observation** - Environment state")
        st.json({
            "transactions": [
                {"id": 0, "amount": 1500.5, "date": "2026-04-01", "description": "Transaction 0", "verified": False, "extra_info": ""}
            ],
            "step_count": 0,
            "echoed_message": "query amount > 5000"
        })
        
        st.markdown("**ResetResponse & StepResponse**")
        st.json({
            "observation": {"transactions": [], "step_count": 0, "echoed_message": ""},
            "reward": 0.10,
            "done": False
        })
    
    with tab2:
        st.markdown("#### 🔄 Core Methods")
        
        st.code("""
async reset() -> ResetResponse
    Initialize environment, return initial observation
    
async step(action: Action) -> StepResponse
    Execute action, return (observation, reward, done)
    
async state() -> Dict[str, Any]
    Get current environment state (flagged counts, step count)
        """, language="python")
    
    with tab3:
        st.markdown("#### 📡 OpenENV Specification")
        st.code("""name: AuditGym
version: v1
description: Forensic audit environment
models:
  - src.models.Action
  - src.models.Observation
  - src.models.ResetResponse
  - src.models.StepResponse
environment: src.env:AuditGymEnv
        """, language="yaml")
    
    with tab4:
        st.markdown("#### 💬 Message Format")
        st.write("**Natural Language Commands:**")
        st.code("""
# Query: Filter transactions
"query amount > 5000"
"query amount < 0"

# Verify: Get cross-reference
"verify id 0"
"verify id 123"

# Flag: Mark as fraudulent
"flag id 0"
"flag id 25"
        """)

# ============ TASK LEVELS ============
elif page == "📊 Task Levels":
    st.markdown("### 📊 Progressive Difficulty Levels")
    
    tasks = [
        {
            "name": "Easy",
            "icon": "🟢",
            "transactions": 100,
            "frauds": 1,
            "red_herrings": 5,
            "max_reward": 0.95,
            "difficulty": "Beginner - Single fraud in small dataset"
        },
        {
            "name": "Medium",
            "icon": "🟡",
            "transactions": 500,
            "frauds": 3,
            "red_herrings": 25,
            "max_reward": 2.85,
            "difficulty": "Intermediate - Multiple frauds with many red herrings"
        },
        {
            "name": "Hard",
            "icon": "🔴",
            "transactions": 1000,
            "frauds": 5,
            "red_herrings": 50,
            "max_reward": 4.75,
            "difficulty": "Advanced - Complex fraud detection scenario"
        }
    ]
    
    for task in tasks:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric(f"{task['icon']} {task['name']}", task['difficulty'].split('-')[0])
            col2.metric("Transactions", task['transactions'])
            col3.metric("Frauds Hidden", task['frauds'])
            col4.metric("Red Herrings", task['red_herrings'])
            
            st.write(f"**Task:** {task['difficulty']}")
            st.write(f"**Max Achievable Reward:** {task['max_reward']:.2f}")
            
            # Reward breakdown
            st.markdown("""
            **Reward Structure:**
            - ✅ Correct fraud flag: +0.95
            - ✅ Correct clear: +0.70
            - ❌ False positive: +0.05 (penalty)
            - ❌ Step penalty: -0.02
            - 🔍 Query info: +0.10
            """)

# ============ LIVE DEMO ============
elif page == "🎯 Live Demo":
    st.markdown("### 🎯 Live Environment Demo")
    st.write("Watch the environment in action with a sample episode")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        difficulty = st.selectbox("Demo Difficulty", ["Easy", "Medium", "Hard"], key="demo_difficulty")
        
        demo_config = {
            "Easy": {"num_total": 100, "num_fraud": 1, "num_red_herring": 5, "max_steps": 10},
            "Medium": {"num_total": 500, "num_fraud": 3, "num_red_herring": 25, "max_steps": 15},
            "Hard": {"num_total": 1000, "num_fraud": 5, "num_red_herring": 50, "max_steps": 20}
        }
        config = demo_config[difficulty]
    
    with col2:
        st.metric("Demo Mode", f"{difficulty} Task", delta="Safe Execution")
    
    if st.button("▶️ Run Demo Episode", use_container_width=True, type="primary"):
        st.info("🎬 Running demo episode...")
        
        # Create environment
        env = AuditGymEnv(**config)
        
        # Run demo
        result = run_async(env.reset())
        total_reward = 0.0
        step = 0
        
        # Demo actions
        demo_actions = [
            "query amount > 5000",
            f"verify id 0",
            f"flag id 0",
            "query amount < 0",
        ]
        
        progress_bar = st.progress(0)
        demo_container = st.container(border=True)
        
        for action_msg in demo_actions[:config["max_steps"]]:
            step += 1
            
            result = run_async(env.step(Action(message=action_msg)))
            reward = result.reward
            total_reward += reward
            
            with demo_container:
                col_step, col_action, col_reward = st.columns([1, 3, 1])
                col_step.write(f"**Step {step}**")
                col_action.write(f"`{action_msg}`")
                col_reward.write(f"{reward:+.2f}" + ("🟢" if reward > 0 else "🔴"))
            
            progress_bar.progress(min(step / config["max_steps"], 1.0))
            
            if result.done:
                break
        
        # Final stats
        st.divider()
        st.success(f"✅ Demo Complete! Total Reward: {total_reward:.2f}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Final Reward", f"{total_reward:.2f}")
        col2.metric("Steps Taken", step)
        
        state = run_async(env.state())
        col3.metric("Frauds Flagged", state['flagged_frauds'])
        
        # Grading
        if difficulty == "Easy":
            score = grade_easy(state)
        elif difficulty == "Medium":
            score = grade_medium(state)
        else:
            score = grade_hard(state)
        
        st.metric("Final Score", f"{score:.2%}", delta=f"{score - 0.5:.2%}" if score > 0.5 else f"{score:.2%}")
        
        run_async(env.close())

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
AuditGym-v1 | OpenEnv Hackathon | 🔍 Forensic Fraud Detection Environment
</div>
""", unsafe_allow_html=True)

