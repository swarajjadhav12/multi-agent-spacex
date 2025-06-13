from agents.base_agent import BaseAgent
import requests

class SpaceXAgent(BaseAgent):
    def __init__(self):
        super().__init__("SpaceXAgent")

    def run(self, input_data):
        # Fetch next SpaceX launch info
        response = requests.get("https://api.spacexdata.com/v4/launches/next")
        data = response.json()
        return {
            "name": data["name"],
            "launchpad": data["launchpad"],
            "date_utc": data["date_utc"]
        }
