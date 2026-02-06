from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Returns: { "score": float, "label": str, "details": Any, ... }
        """
        pass
