from abc import ABC, abstractmethod
from typing import Any
from .base import *


class BackendBase(ABC):
    """
    Base class for backends.
    """
    @abstractmethod
    def message_box(self):
        "Returns the messagebox class."

    def file_dialog(self) -> type[Any]:
        "Returns the file dialog class."

    @abstractmethod
    def frame(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent frame."

    @abstractmethod
    def label(self, *args, **kwargs) -> Any:
        """Creates a Tkinter-equivalent label."""

    @abstractmethod
    def separator(self, *args, **kwargs) -> Any:
        """Creates a Tkinter-equivalent separator."""

    @abstractmethod
    def button(self, *args, **kwargs) -> Any:
        """Creates a Tkinter-equivalent button."""

    @abstractmethod
    def menu_button(self, *args, **kwargs) -> Any:
        """Creates a Tkinter-equivalent menu-button."""

    @abstractmethod
    def menu(self, *args, **kwargs) -> Any:
        """Creates a Tkinter-equivalent menu."""

    @abstractmethod
    def spinbox(self, *args, **kwargs) -> Any:
        """Creates a Tkinter-equivalent spinbox."""

    @abstractmethod
    def toplevel(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent toplevel."

    @abstractmethod
    def style(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent style."

    @abstractmethod
    def boolean_var(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent boolean variable."

    @abstractmethod
    def checkbutton(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent boolean Checkbutton."

    @abstractmethod
    def entry(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent entry."

    @abstractmethod
    def scrollbar(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent scrollbar."

    @abstractmethod
    def hinted_entry(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent hinted entry."

    @abstractmethod
    def object_scalar(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent object scalar."

    @abstractmethod
    def text(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent text."

    @abstractmethod
    def listbox(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent listbox."

    @abstractmethod
    def scrolled_listbox(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent scrolled listbox."

    @abstractmethod
    def combobox(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent combobox."

    @abstractmethod
    def combo_edit_frame(self, *args, **kwargs) -> Any:
        "Creates a Tkinter-equivalent combo edit frame"
