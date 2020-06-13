from abc import ABC, abstractmethod
from typing import Any


class StorageManager(ABC):

    @abstractmethod
    def get(self, username: str) -> Any:
        pass

    @abstractmethod
    def set(self, username: str, value: Any):
        pass

    @abstractmethod
    def delete(self, username: str):
        pass


