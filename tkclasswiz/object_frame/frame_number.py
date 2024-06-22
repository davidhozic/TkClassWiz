
from typing import Union, Any

from .frame_base import *
from ..extensions import extendable
from ..doc import doc_category

import tkinter as tk


__all__ = (
    "NewObjectFrameNumber",
)


@extendable
@doc_category("Object frames")
class NewObjectFrameNumber(NewObjectFrameBase):
    """
    Frame for use inside the ObjectEditWindow that allows definition of numerical data.

    Parameters
    -----------
    class_: Any
        The class we are defining for.
    return_widget: Any
        The widget to insert the ObjectInfo into after saving.
    parent: TopLevel
        The parent window.
    old_data: Any
        The old_data gui data.
    check_parameters: bool
        Check parameters (by creating the real object) upon saving.
        This is ignored if editing a function instead of a class.
    allow_save: bool
        If False, will open in read-only mode.
    """
    def __init__(
        self,
        class_: Any,
        return_widget: Any,
        parent: NewObjectFrameBase = None,
        old_data: Any = None,
        check_parameters: bool = True,
        allow_save: bool = True
    ):
        super().__init__(class_, return_widget, parent, old_data, check_parameters, allow_save)
        self.storage_widget = self.backend.spinbox(self.frame_main, from_=-9999, to=9999)
        self.storage_widget.pack(fill=tk.X)

        if old_data is not None:  # Edit
            self.load(old_data)

        self.remember_gui_data()

    def load(self, old_data: Union[int, float]):
        self.storage_widget.set(old_data)
        self.old_gui_data = old_data

    def get_gui_data(self) -> Union[int, float]:
        return self.return_widget.get()

    def to_object(self):
        return self.cast_type(self.storage_widget.get(), [self.class_])
