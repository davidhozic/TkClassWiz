from typing import TypeVar, Any
from enum import Flag

from ..doc import doc_category
from ..deprecation import *
from ..utilities import *
from ..convert import *
from ..dpi import *

from ..storage import *

from .frame_base import *

import tkinter as tk


__all__ = ("NewObjectFrameFlag",)

T = TypeVar("T", ComboBoxObjects, ListBoxScrolled, ListBoxObjects)


@doc_category("Object frames")
class NewObjectFrameFlag(NewObjectFrameBase):
    """
    Frame for use inside the ObjectEditWindow that allows definition of enum flags.

    Parameters
    ------------
    class_: Flag
        The class we are defining for.
    return_widget: T
        The widget to insert the ObjectInfo into after saving.
    parent: TopLevel
        The parent window.
    old_data: Flag
        The old_data gui data.
    check_parameters: bool
        Check parameters (by creating the real object) upon saving.
        This is ignored if editing a function instead of a class.
    allow_save: bool
        If False, will open in read-only mode.
    """
    def __init__(
        self,
        class_: Flag,
        return_widget: T,
        parent: Any = None,
        old_data: Flag = None,
        check_parameters: bool = True,
        allow_save=True
    ):
        super().__init__(class_, return_widget, parent, old_data, check_parameters, allow_save)

        dpi_5 = dpi_scaled(5)
        dpi_10 = dpi_scaled(5)
        self.backend.label(self.frame_main, text="Current value").pack(anchor=tk.W)
        w = PyObjectScalar(self.frame_main)
        w.pack(fill=tk.X, pady=dpi_5)

        self.backend.separator(self.frame_main).pack(fill=tk.X, pady=dpi_10)

        self.backend.label(self.frame_main, text="Modify").pack(anchor=tk.W)
        combo_select = ComboBoxObjects(self.frame_main, width=max(map(len, map(str, list(class_)))))
        combo_select["values"] = list(class_)
        combo_select.pack(anchor=tk.W, pady=dpi_5)
        bnt_add_flag = self.backend.button(self.frame_main, text="Add flag", command=lambda: self._update_flag(combo_select.get(), True))
        bnt_add_flag.pack(anchor=tk.W)
        bnt_remove_flag = self.backend.button(self.frame_main, text="Remove flag", command=lambda: self._update_flag(combo_select.get(), False))
        bnt_remove_flag.pack(anchor=tk.W)

        self.storage_widget = w
        if old_data is not None:
            self.load(old_data)

        self.remember_gui_data()

    @gui_except()
    def _update_flag(self, flag: Flag, set: bool):
        if isinstance(flag, str):
            raise ValueError(
                f"No valid flag selected! Current selection: '{flag}'\n"
                f"Allowed values: {list(map(str, iter(self.class_)))}"
            )

        old_value = self.storage_widget.get()
        if old_value is None:
            old_value = flag

        if set:
            new_value = old_value | flag
        else:
            new_value = old_value & (~flag)

        self.storage_widget.set(new_value)

    def load(self, old_data: Flag):
        self.storage_widget.set(old_data)
        self.old_gui_data = old_data

    def get_gui_data(self):
        return self.storage_widget.get()

    def to_object(self) -> Flag:
        value = self.storage_widget.get()
        if isinstance(value, str):
            raise ValueError(f"Cannot directly input string '{value}'")

        if value is None:
            value = self.class_(0)

        return value
