from abc import ABC, abstractmethod
from typing import Optional

class BaseStepRunner(ABC):
    @abstractmethod
    def config(self, step_config: dict, workdir: str = "/", retries: int = 3) -> Optional[str]:
        pass
