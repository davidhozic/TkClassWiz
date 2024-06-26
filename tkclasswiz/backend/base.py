from abc import ABC, abstractmethod
from typing import Any, Protocol

from .base import *

import tkinter as tk



class Widget(Protocol):
    """
    A Tkinter-like widget.
    """
    def pack(**kwargs):
        ...

    def pack_forget(**kwargs):
        ...

    def destroy(**kwargs):
        ...


class Messagebox(Widget):
    "Class for showing infos / warnings / errors and asking questions through a dialog."
    def yesnocancel(self, title: str, message: str, parent: Widget):
        """
        Asks a yes / no / cancel question.

        Parameters
        -----------
        title: str
            The window title.
        message: str
            The question message.
        parent: Widget
            The parent / master of the window.
        """

    def show_error(self, title: str, message: str, parent: Widget):
        """
        Displays an error window.

        Parameters
        -----------
        title: str
            The window title.
        message: str
            The window message.
        parent: Widget
            The parent / master of the window.
        """

    def show_info(self, title: str, message: str, parent: Widget):
        """
        Displays an info window.

        Parameters
        -----------
        title: str
            The window title.
        message: str
            The window message.
        parent: Widget
            The parent / master of the window.
        """


class FileDialog(Widget):
    "Class for opening files."
    @staticmethod
    def askopenfile(mode: str = 'r', **options):
        ...

    @staticmethod
    def askopenfilename(**options) -> str:
        ...

    @staticmethod
    def asksaveasfilename(**options) -> str:
        ...

    @staticmethod
    def asksaveasfile(**options):
        ...


class Frame(Widget):
    ...


class Toplevel(Widget):
    def title(**kwargs):
        ...


class PyObjectScalar(Widget):
    ...


class Button(Widget):
    ...


class BackendBase(ABC):
    """
    Base class for backends.
    """
    @abstractmethod
    def message_box(self) -> Messagebox:
        "Returns the messagebox class."

    def file_dialog(self) -> FileDialog:
        "Returns the file dialog class."

    @abstractmethod
    def frame(self, **kwargs) -> Frame:
        "Creates a Tkinter-equivalent frame."

    @abstractmethod
    def label(self, **kwargs) -> Widget:
        """Creates a Tkinter-equivalent label."""

    @abstractmethod
    def separator(self, **kwargs) -> Widget:
        """Creates a Tkinter-equivalent separator."""

    @abstractmethod
    def button(self, **kwargs) -> Button:
        """Creates a Tkinter-equivalent button."""

    @abstractmethod
    def menu_button(self, **kwargs) -> Widget:
        """Creates a Tkinter-equivalent menu-button."""

    @abstractmethod
    def menu(self, **kwargs) -> Widget:
        """Creates a Tkinter-equivalent menu."""

    @abstractmethod
    def spinbox(self, **kwargs) -> Widget:
        """Creates a Tkinter-equivalent spinbox."""

    @abstractmethod
    def toplevel(self, **kwargs) -> Toplevel:
        "Creates a Tkinter-equivalent toplevel."

    @abstractmethod
    def style(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent style."

    @abstractmethod
    def boolean_var(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent boolean variable."

    @abstractmethod
    def checkbutton(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent boolean Checkbutton."

    @abstractmethod
    def entry(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent entry."

    @abstractmethod
    def scrollbar(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent scrollbar."

    @abstractmethod
    def hinted_entry(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent hinted entry."

    @abstractmethod
    def object_scalar(self, **kwargs) -> PyObjectScalar:
        "Creates a Tkinter-equivalent object scalar."

    @abstractmethod
    def text(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent text."

    @abstractmethod
    def listbox(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent listbox."

    @abstractmethod
    def scrolled_listbox(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent scrolled listbox."

    @abstractmethod
    def combobox(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent combobox."

    @abstractmethod
    def combo_edit_frame(self, **kwargs) -> Widget:
        "Creates a Tkinter-equivalent combo edit frame"
