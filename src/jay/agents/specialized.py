from .base_agent import BaseAgent

class EngineeringAgent(BaseAgent):
    def __init__(self):
        super().__init__("Engineering Agent")

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("Research Agent")

class GrowthAgent(BaseAgent):
    def __init__(self):
        super().__init__("Growth Agent")

class OperationsAgent(BaseAgent):
    def __init__(self):
        super().__init__("Operations Agent")
