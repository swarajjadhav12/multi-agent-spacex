from agents.planner_agent import PlannerAgent
from core.agent_manager import AgentManager
from dotenv import load_dotenv
import json

load_dotenv()

# -------------------------
# 🟢 Manual Goal Execution
# -------------------------
def run_manual():
    user_goal = "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed."
    planner = PlannerAgent()
    task_plan = planner.plan(user_goal)
    print("Planned tasks:", task_plan)

    manager = AgentManager(task_plan)
    final_result = manager.execute()

    print("\n✅ Final Result:\n", final_result.get("delay_analysis", "No delay_analysis key found"))


# -------------------------
# 🧪 Evaluation Runner
# -------------------------
def run_evaluations():
    with open("evals/test_cases.json", "r") as f:
        evals = json.load(f)

    for case in evals:
        print(f"\n🔍 Evaluating goal: {case['goal']}")

        planner = PlannerAgent()
        task_order = planner.plan(case["goal"])  # ← FIXED LINE
        print(f"Planned tasks: {task_order}")

        agent_manager = AgentManager(task_order)
        result = agent_manager.execute()

        missing = [k for k in case["expected_keys"] if k not in result]
        if not missing:
            print("✅ Eval Passed")
        else:
            print(f"❌ Eval Failed. Missing keys: {missing}")


# -------------------------
# 🏁 Entry Point
# -------------------------
if __name__ == "__main__":
    run_manual()         # Run manual example
    run_evaluations()    # Run evals from test_cases.json
