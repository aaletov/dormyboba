from abc import ABC, abstractmethod
from enum import Enum

class CommandType(Enum):
    INTERMEDIATE = 1
    TERMINATE = 2

class Command(ABC):
    @abstractmethod
    def kind() -> CommandType:
        pass