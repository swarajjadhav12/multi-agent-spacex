from agents.spacex_agent import SpaceXAgent
from agents.weather_agent import WeatherAgent
from agents.delay_analyzer import DelayAnalyzerAgent

class AgentManager:
    def __init__(self, task_plan: list, max_retries: int = 1):
        """
        Initializes the AgentManager with a plan and shared data buffer.
        """
        self.task_plan = task_plan
        self.shared_data = None
        self.max_retries = max_retries

    def get_agent_instance(self, agent_name: str):
        """
        Returns an instance of the requested agent.
        """
        agents = {
            "SpaceXAgent": SpaceXAgent,
            "WeatherAgent": WeatherAgent,
            "DelayAnalyzerAgent": DelayAnalyzerAgent,
        }
        if agent_name in agents:
            return agents[agent_name]()
        else:
            raise ValueError(f"Unknown agent: {agent_name}")

    def execute(self):
        """
        Executes the agents in sequence, enriching data at each step.
        Retries an agent if it fails to produce output.
        """
        for agent_name in self.task_plan:
            agent = self.get_agent_instance(agent_name)
            attempt = 0
            output = None

            while attempt <= self.max_retries:
                print(f"[{agent.name}] Attempt {attempt + 1} with input: {self.shared_data}")
                output = agent.run(self.shared_data)
                if output is not None:
                    break
                print(f"[{agent.name}] Warning: No output. Retrying...")
                attempt += 1

            if output is None:
                raise RuntimeError(f"{agent.name} failed after {self.max_retries + 1} attempts.")

            self.shared_data = output

        return self.shared_data
