"""
Tkinter backend for tkclasswiz.
"""
from .base import BackendBase

import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import tkinter as tk


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
    def message_box(self):
        return Messagebox

    def file_dialog(self):
        return filedialog

    def frame(self, *args, **kwargs):
        return ttk.Frame(*args, **kwargs)

    def label(self, *args, **kwargs):
        return ttk.Label(*args, **kwargs)
    
    def separator(self, *args, **kwargs):
        return ttk.Separator(*args, **kwargs)

    def button(self, *args, **kwargs):
        return ttk.Button(*args, **kwargs)

    def menu_button(self, *args, **kwargs):
        return ttk.Menubutton(*args, **kwargs)

    def menu(self, *args, **kwargs):
        return tk.Menu(*args, **kwargs)

    def spinbox(self, *args, **kwargs):
        return ttk.Spinbox(*args, **kwargs)

    def toplevel(self, *args, **kwargs):
        return tk.Toplevel(*args, **kwargs)
    
    def style(self, *args, **kwargs):
        return ttk.Style(*args, **kwargs)

    def boolean_var(self, *args, **kwargs):
        return tk.BooleanVar(*args, **kwargs)

    def checkbutton(self, *args, **kwargs):
        return tk.Checkbutton(*args, **kwargs)
