from typing import List, Dict, Any
from agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """Agent responsible for planning the execution order of other agents based on user goals.
    
    This agent analyzes the user's goal and determines which agents need to be executed
    and in what order to achieve the desired outcome.
    
    Attributes:
        name (str): The name of the agent (PlannerAgent)
    """
    
    def __init__(self) -> None:
        """Initialize the planner agent."""
        super().__init__(name="PlannerAgent")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the planner agent's logic.
        
        Args:
            input_data (Dict[str, Any]): Input data containing the user's goal
            
        Returns:
            Dict[str, Any]: A dictionary containing the planned tasks
            
        Raises:
            KeyError: If the input_data is missing the required 'goal' key
        """
        if 'goal' not in input_data:
            raise KeyError("Input data must contain a 'goal' key")
            
        tasks = self.plan(input_data['goal'])
        return {"tasks": tasks}
    
    def plan(self, goal: str) -> List[str]:
        """Parse the user goal and determine the required agent execution order.
        
        Args:
            goal (str): The user's goal to be achieved
            
        Returns:
            List[str]: A list of agent names in the order they should be executed
            
        Note:
            The planner recognizes several keywords to determine which agents to include:
            - ADK-related: "connect", "device", "send", "receive", "data"
            - SpaceX-related: "SpaceX"
            - Weather-related: "weather", "delay"
        """
        if not goal:
            logger.warning("Empty goal provided to planner")
            return []
            
        tasks = []
        goal_lower = goal.lower()
        
        # Check for ADK-related tasks
        if any(word in goal_lower for word in ["connect", "device"]):
            tasks.append("ADKAgent")
            
        if any(word in goal_lower for word in ["send", "data"]):
            tasks.append("ADKAgent")
            
        if any(word in goal_lower for word in ["receive", "data"]):
            tasks.append("ADKAgent")

        # Check for SpaceX-related tasks
        if "SpaceX" in goal:
            tasks.append("SpaceXAgent")

        # Check for weather and delay analysis tasks
        if "delay" in goal_lower:
            tasks.append("WeatherAgent")
            tasks.append("DelayAnalyzerAgent")
        elif "weather" in goal_lower:
            tasks.append("WeatherAgent")

        logger.info(f"Planned tasks for goal '{goal}': {tasks}")
        return tasks
