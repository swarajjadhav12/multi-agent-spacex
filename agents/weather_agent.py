from agents.base_agent import BaseAgent
import requests
import os
from dotenv import load_dotenv
load_dotenv()

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__("WeatherAgent")
        self.api_key = os.getenv("OPENWEATHER_API_KEY")

    def run(self, input_data):
        # Here we fake the location for simplicity
        lat, lon = 28.5623, -80.5774  # Kennedy Space Center
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        input_data["weather"] = data
        return input_data
