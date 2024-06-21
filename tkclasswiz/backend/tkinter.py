"""
Tkinter backend for tkclasswiz.
"""
from .base import BackendBase

import tkinter.messagebox as messagebox
import tkinter.ttk as ttk


class Messagebox:
    """
    Wrapper for some of Messagebox methods, that offers compatibility between
    ttk and ttkbootstrap.
    """
    def _process_kwargs(kwargs):
        if "master" in kwargs:
            kwargs['parent'] = kwargs["master"]
            del kwargs["master"]

    @classmethod
    def yesnocancel(cls, title: str, message: str, **kwargs):
        cls._process_kwargs(kwargs)
        return messagebox.askyesnocancel(title, message, **kwargs)

    @classmethod
    def show_error(cls, title: str, message: str, **kwargs):
        cls._process_kwargs(kwargs)
        messagebox.showerror(title, message, **kwargs)

    @classmethod
    def show_info(cls, title: str, message: str, **kwargs):
        cls._process_kwargs(kwargs)
        messagebox.showinfo(title, message, **kwargs)


class BackendTkinter(BackendBase):
    def frame(self, *args, **kwargs):
        return ttk.Frame(*args, **kwargs)

    def message_box(self, *args, **kwargs):
        return Messagebox
