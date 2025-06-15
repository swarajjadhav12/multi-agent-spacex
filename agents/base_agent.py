from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all agents in the system.
    
    This abstract class defines the interface that all agents must implement.
    It provides basic functionality and enforces a consistent structure across agents.
    
    Attributes:
        name (str): The name of the agent
    """
    
    def __init__(self, name: str) -> None:
        """Initialize the base agent.
        
        Args:
            name (str): The name of the agent
        """
        self.name = name
    
    @abstractmethod
    def run(self, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the agent's main logic.
        
        Args:
            input_data (Optional[Dict[str, Any]]): Input data for the agent to process
            
        Returns:
            Dict[str, Any]: The result of the agent's execution
            
        Raises:
            NotImplementedError: If the method is not implemented by a subclass
        """
        raise NotImplementedError("Each agent must implement the `run()` method.")
