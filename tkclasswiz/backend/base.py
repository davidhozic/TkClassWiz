from typing import Any
from abc import ABC, abstractmethod


class BackendBase(ABC):
    """
    Base class for backends.
    """
    @abstractmethod
    def frame(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent frame."

    @abstractmethod
    def message_box(self, *args, **kwargs) -> Any:
        "Returns the messagebox class."
