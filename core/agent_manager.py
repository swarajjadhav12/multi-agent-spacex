from agents.spacex_agent import SpaceXAgent
from agents.weather_agent import WeatherAgent
from agents.delay_analyzer import DelayAnalyzerAgent
from agents.adk_agent import ADKAgent
from agents.planner_agent import PlannerAgent

class AgentManager:
    """Manages the execution of agents and their interactions."""
    
    def __init__(self, task_plan):
        """Initialize the agent manager with a task plan."""
        self.task_plan = task_plan
        self.shared_data = {}
        
    def get_agent_instance(self, agent_name):
        """Get an instance of the specified agent."""
        agents = {
            "PlannerAgent": PlannerAgent,
            "ADKAgent": ADKAgent
        }
        
        if agent_name not in agents:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        return agents[agent_name]()
        
    def execute(self, input_data=None):
        """Execute the current task plan."""
        for agent_name in self.task_plan:
            agent = self.get_agent_instance(agent_name)
            max_attempts = 3
            attempt = 1
            
            while attempt <= max_attempts:
                try:
                    print(f"[{agent_name}] Attempt {attempt} with input: {input_data}")
                    output = agent.run(input_data)
                    
                    if output:
                        return output
                        
                except Exception as e:
                    print(f"Error executing {agent_name}: {str(e)}")
                    if attempt == max_attempts:
                        return {"status": "error", "message": str(e)}
                        
                attempt += 1
                
        return {"status": "error", "message": "No output from any agent"}
