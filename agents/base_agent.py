class BaseAgent:
    def __init__(self, name):
        self.name = name

    def run(self, input_data):
        raise NotImplementedError("Each agent must implement the `run()` method.")
