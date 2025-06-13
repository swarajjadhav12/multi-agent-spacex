from agents.base_agent import BaseAgent

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="PlannerAgent")

    def plan(self, goal: str) -> list:
        """
        Parses the user goal and returns a list of agent names in order.
        """
        tasks = []

        if "SpaceX" in goal:
            tasks.append("SpaceXAgent")

        if "delay" in goal:
            tasks.append("WeatherAgent")
            tasks.append("DelayAnalyzerAgent")

        elif "weather" in goal:
            tasks.append("WeatherAgent")

        return tasks
