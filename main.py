from agents.planner_agent import PlannerAgent
from core.agent_manager import AgentManager
from dotenv import load_dotenv
import json
import time
import logging
import sys
from core.google_adk_manager import GoogleADKManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# -------------------------
# 🟢 Manual Goal Execution
# -------------------------
def run_manual():
    """Run the system with a predefined goal."""
    try:
        user_goal = "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed."
        logger.info(f"Starting manual execution with goal: {user_goal}")
        
        planner = PlannerAgent()
        task_plan = planner.plan(user_goal)
        logger.info(f"Planned tasks: {task_plan}")

        manager = AgentManager(task_plan)
        final_result = manager.execute()

        logger.info("Execution completed successfully")
        print("\n✅ Final Result:\n", final_result.get("delay_analysis", "No delay_analysis key found"))
    except Exception as e:
        logger.error(f"Error in manual execution: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")

# -------------------------
# 📱 ADK Device Execution
# -------------------------
def run_adk_tasks():
    """Run ADK-specific tasks."""
    logger.info("Starting ADK device execution")
    print("\n=== ADK Device Execution ===")
    
    try:
        # Initialize planner and agent manager
        planner = PlannerAgent()
        task_plan = planner.plan("Connect to Android device")
        agent_manager = AgentManager(task_plan)
        
        # Connect to device
        print("\n🔌 Connecting to device...")
        result = agent_manager.execute()
        if result.get("status") != "success":
            logger.error("Failed to connect to device")
            print("❌ Failed to connect to device")
            return
        logger.info("Successfully connected to device")
        print("✅ Connected to device")
        
        # Send test data and receive response
        print("\n📤 Sending test data...")
        result = agent_manager.execute(input_data={
            "action": "send",
            "data": "Hello from ADK!"
        })
        
        if result.get("status") == "success":
            logger.info("Data sent successfully")
            print("✅ Data sent successfully")
            if "received_data" in result:
                print(f"📥 Received response: {result['received_data']}")
        elif result.get("status") == "warning":
            logger.warning("Data sent but no response received")
            print("⚠️ Data sent but no response received")
            print("Trying to receive data separately...")
            
            # Try to receive data separately
            result = agent_manager.execute(input_data={"action": "receive"})
            if result.get("status") == "success":
                logger.info("Successfully received data")
                print(f"📥 Received response: {result['data']}")
            else:
                logger.error("No response received")
                print("❌ No response received")
        else:
            logger.error(f"Error sending data: {result.get('message')}")
            print(f"❌ Error: {result.get('message')}")
        
        # Close connection
        print("\n🔌 Closing connection...")
        result = agent_manager.execute(input_data={"action": "close"})
        if result.get("status") == "success":
            logger.info("Connection closed successfully")
            print("✅ Connection closed")
        else:
            logger.error(f"Error closing connection: {result.get('message')}")
            print(f"❌ Error closing connection: {result.get('message')}")
            
    except Exception as e:
        logger.error(f"Error in ADK execution: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")

# -------------------------
# 🧪 Evaluation Runner
# -------------------------
def run_evaluations():
    """Run evaluation test cases."""
    try:
        logger.info("Starting evaluation run")
        with open("evals/test_cases.json", "r") as f:
            evals = json.load(f)

        for case in evals:
            logger.info(f"Evaluating goal: {case['goal']}")
            print(f"\n🔍 Evaluating goal: {case['goal']}")

            planner = PlannerAgent()
            task_order = planner.plan(case["goal"])
            print(f"Planned tasks: {task_order}")

            agent_manager = AgentManager(task_order)
            result = agent_manager.execute()

            missing = [k for k in case["expected_keys"] if k not in result]
            if not missing:
                logger.info("Evaluation passed")
                print("✅ Eval Passed")
            else:
                logger.warning(f"Evaluation failed. Missing keys: {missing}")
                print(f"❌ Eval Failed. Missing keys: {missing}")
                
    except FileNotFoundError:
        logger.error("Test cases file not found")
        print("❌ Error: Test cases file not found")
    except json.JSONDecodeError:
        logger.error("Invalid JSON in test cases file")
        print("❌ Error: Invalid JSON in test cases file")
    except Exception as e:
        logger.error(f"Error in evaluation: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")

# -------------------------
# 🏁 Entry Point
# -------------------------
def main():
    """Main entry point for the application."""
    try:
        print("\nChoose mode:")
        print("1: Manual")
        print("2: ADK Tasks")
        print("3: Evaluations")
        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            run_manual()
        elif choice == "2":
            run_adk_tasks()
        elif choice == "3":
            run_evaluations()
        else:
            logger.warning(f"Invalid choice: {choice}")
            print("Invalid choice!")
            
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        print("\nProgram interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
