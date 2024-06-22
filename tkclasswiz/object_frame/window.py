from typing import get_origin
from inspect import isclass, isfunction
from collections.abc import Sequence, Set
from enum import Flag

from .frame_number import *
from .frame_iterable import *
from .frame_string import *
from .frame_struct import *
from .frame_base import *
from .frame_flag import *

from ..utilities import gui_except, issubclass_noexcept
from ..extensions import extendable
from ..backend import get_backend
from ..doc import doc_category
from ..dpi import dpi_scaled

import tkinter as tk


__all__ = (
    "ObjectEditWindow",
)


@extendable
@doc_category("Object window")
class ObjectEditWindow:
    """
    Top level window for creating and editing new objects.
    """
    def __init__(self, *args, **kwargs):
        self.backend = backend = get_backend()
        self.toplevel = backend.toplevel(*args, **kwargs)
        self._closed = False
        dpi_5 = dpi_scaled(5)

        # Elements
        self.opened_frames: list[NewObjectFrameBase] = []
        self.frame_main = backend.frame(self.toplevel, padding=(dpi_5, dpi_5))
        self.frame_toolbar = backend.frame(self.toplevel, padding=(dpi_5, dpi_5))
        backend.button(self.frame_toolbar, text="Close", command=self.close_object_edit_frame).pack(side="left")
        backend.button(self.frame_toolbar, text="Save", command=self.save_object_edit_frame).pack(side="left")

        self.frame_toolbar.pack(expand=False, fill=tk.X)
        self.frame_main.pack(expand=True, fill=tk.BOTH)
        self.frame_main.rowconfigure(0, weight=1)
        self.frame_main.columnconfigure(0, weight=1)

        var = backend.boolean_var(value=True)
        backend.checkbutton(
            self.frame_toolbar,
            text="Keep on top",
            variable=var,
            command=lambda: self.attributes("-topmost", var.get()),
        ).pack(side="right")
        self.toplevel.attributes("-topmost", var.get())

        # Window initialization
        NewObjectFrameBase.set_origin_window(self)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.close_object_edit_frame)

    @property
    def closed(self) -> bool:
        return self._closed

    def open_object_edit_frame(
        self,
        class_,
        return_widget,
        old_data = None,
        check_parameters: bool = True,
        allow_save: bool = True,
        **kwargs
    ):
        """
        Opens new frame for defining an object.
        Parameters are the same as for NewObjectFrameBase.

        Parameters
        ------------
        class_: Any
            The class we are defining for.
        return_widget: Any
            The widget to insert the ObjectInfo into after saving.
        old_data: Any
            The old_data gui data.
        check_parameters: bool
            Check parameters (by creating the real object) upon saving.
            This is ignored if editing a function instead of a class.
        allow_save: bool
            If False, will open in read-only mode.
        """
        frame = self._create_and_add_frame(class_, return_widget, old_data, check_parameters, allow_save, kwargs)
        if frame is None and not self.opened_frames:
            self.toplevel.destroy()
            self._closed = True

    @gui_except()
    def _create_and_add_frame(
        self,
        class_: type,
        return_widget,
        old_data,
        check_parameters: bool,
        allow_save: bool,
        kwargs
    ):
        frame: NewObjectFrameBase
        class_origin = get_origin(class_) or class_  # Remove any Generic type subscriptions

        if issubclass_noexcept(class_origin, Flag):
            frame_class = NewObjectFrameFlag
        elif issubclass_noexcept(class_origin, str):
            frame_class = NewObjectFrameString
        elif issubclass_noexcept(class_origin, (int, float, complex)):
            frame_class = NewObjectFrameNumber
        elif issubclass_noexcept(class_origin, (Sequence, Set)):
            frame_class = NewObjectFrameIterable
        else:
            frame_class = NewObjectFrameStruct

        self.opened_frames.append(
            frame := frame_class(
                class_,
                return_widget,
                old_data=old_data,
                check_parameters=check_parameters,
                allow_save=allow_save,
                parent=self.frame_main,
                **kwargs
            )
        )

        if len(self.opened_frames) > 1:
            self.opened_frames[-2].pack_forget()

        frame.pack(fill=tk.BOTH, expand=True)
        frame.update_window_title()
        self.set_default_size_y()

        return frame

    def close_object_edit_frame(self):
        self.opened_frames[-1].close_frame()

    def save_object_edit_frame(self):
        self.opened_frames[-1].save()

    def clean_object_edit_frame(self):
        self.opened_frames.pop().destroy()
        opened_frames_len = len(self.opened_frames)

        if opened_frames_len:
            frame = self.opened_frames[-1]
            frame.pack(fill=tk.BOTH, expand=True)  # (row=0, column=0)
            frame.update_window_title()
            self.set_default_size_y()
        else:
            self._closed = True
            self.toplevel.destroy()

    def set_default_size_y(self):
        "Sets window Y size to default"
        self.toplevel.update()
        self.toplevel.geometry(f"{self.toplevel.winfo_width()}x{self.toplevel.winfo_reqheight()}")
