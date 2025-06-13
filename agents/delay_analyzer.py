from agents.base_agent import BaseAgent

class DelayAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("DelayAnalyzerAgent")

    def run(self, input_data):
        weather = input_data.get("weather", {})
        condition = weather.get("weather", [{}])[0].get("main", "")
        delay_possible = condition in ["Rain", "Storm", "Snow"]
        input_data["delay_analysis"] = f"Delay likely: {delay_possible} based on condition: {condition}"
        return input_data
