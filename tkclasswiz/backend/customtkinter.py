"""
CustomTkinter backend for TkClassWizard.
"""
from typing import Union, List, Any, Callable
from contextlib import suppress

from ..convert import ObjectInfo, convert_to_dict, convert_from_dict
from ..utilities import gui_confirm_action
from ..doc import doc_category
from .base import BackendBase

import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import tkinter as tk
import customtkinter as ctk
import pickle
import base64



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


@doc_category("Storage widgets")
class PyObjectScalar(ctk.CTkFrame):
    """
    Represents a single storage widget for a Python object.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.element = None
        self.display = ctk.CTkEntry(self, state="readonly")
        self.display.pack(fill=tk.BOTH, expand=True)

    def get(self) -> object:
        """
        Returns the stored Python object (or None if not set).
        """
        return self.element

    def set(self, value: object):
        """
        Sets the Python object as the widget's value.
        """
        self.display.configure(state="active")
        self.display.delete("0", tk.END)
        self.display.insert(tk.END, str(value))
        self.display.configure(state="readonly")
        self.element = value


@doc_category("Storage widgets")
class Text(tk.Text):
    """
    Modified version of :class`tkinter.Text`, which replaces the original
    ``get`` method to contain no parameters and instead return the entire text stripped.
    This is for compatibility with other storage widgets.
    """
    def get(self) -> str:
        "Returns entire text stripped."
        return super().get("1.0", tk.END).strip()


@doc_category("Storage widgets")
class ListBoxObjects(tk.Listbox):
    """
    Modified version of :class:`tkinter.Listbox`, which:

    - Allows copy-paste and also sets the standard keyboard shortcuts for it
    - Implements the ``current`` method for compatibility with :class:`tkclasswiz.storage.ComboBoxObjects`
    - Overwrites the ``get`` method to return the original objects instead of text
    - Modifies the ``insert`` method to insert original objects instead of text
    """
    def __init__(self, *args, **kwargs):
        self._original_items = []
        super().__init__(*args, **kwargs)
        self.configure(selectmode=tk.EXTENDED)
        self.bind("<Control-c>", lambda e: self.save_to_clipboard())
        self.bind("<BackSpace>", lambda e: self.delete_selected())
        self.bind("<Delete>", lambda e: self.delete_selected())
        self.bind("<Control-v>", lambda e: self.paste_from_clipboard())

    def current(self) -> int:
        "Returns index of the first currently selected element or -1 if none selected."
        selection = self.curselection()
        return selection[0] if len(selection) else -1

    def get(self, first: int = 0, last: int = None) -> list:
        """
        Returns elements from ``first`` to ``last`` (not included).
        """
        slice_range = slice(first, last)
        return self._original_items[slice_range]

    def insert(self, index: Union[str, int], *elements: Union[str, float]) -> None:
        """
        Inserts ``elements`` to ``index``. The ``index`` must be a numerical index or tkinter.END ('end').
        """
        _ret = super().insert(index, *elements)
        if isinstance(index, str):
            index = len(self._original_items) if index == "end" else 0

        old_data = self._original_items[index:]
        self._original_items[index:] = list(elements) + old_data

        return _ret

    def delete(self, *indexes: int) -> None:
        """
        Delete elements that have the index in ``indexes``
        """
        def create_ranges():
            start_i = indexes[0]
            len_indexes = len(indexes)
            for i in range(1, len_indexes):
                if indexes[i] > indexes[i - 1] + 1:  # Current index more than 1 bigger than previous
                    to_yield = start_i, indexes[i - 1]
                    yield to_yield

                    # After element is erased, all items' indexes get shifted to the left
                    # from the deleted item forward (right) -> Need to shift our list of indexes also.
                    for j in range(i, len_indexes):
                        indexes[j] -= (to_yield[1] - to_yield[0] + 1)

                    start_i = indexes[i]

            yield start_i, indexes[-1]

        if indexes[-1] == "end":
            indexes = range(indexes[0], len(self._original_items))

        indexes = sorted(list(indexes))
        for range_ in create_ranges():
            super().delete(*range_)
            del self._original_items[range_[0]:range_[1] + 1]

    def count(self) -> int:
        """
        Returns the amount of elements inside the internal list.
        """
        return len(self._original_items)

    @gui_confirm_action()
    def delete_selected(self):
        """
        Deletes selected elements.
        """
        sel: List[int] = self.curselection()
        if len(sel):
            self.delete(*sel)
        else:
            Messagebox.show_error("Empty list!", "Select atleast one item!", parent=self)

    def clear(self) -> None:
        """
        Deletes all the elements inside the internal list.
        """
        super().delete(0, tk.END)
        self._original_items.clear()

    def save_to_clipboard(self):
        """
        Saves selection to clipboard.
        """
        selection = self.curselection()
        if len(selection):
            object_: Union[ObjectInfo, Any] = self.get()[min(selection):max(selection) + 1]
            to_clipboard = convert_to_dict(object_ if len(selection) > 1 else object_[0])
            to_clipboard = pickle.dumps(to_clipboard)
            to_clipboard = base64.b64encode(to_clipboard).decode('ascii')
            self.clipboard_clear()
            self.clipboard_append(to_clipboard)
        else:
            Messagebox.show_error("Empty list!", "Select atleast one item!", parent=self)

        return "break"

    def paste_from_clipboard(self):
        """
        Paste elements from clipboard.
        """
        value = self.clipboard_get()
        with suppress(Exception):
            value = convert_from_dict(pickle.loads(base64.b64decode(value)))

        if isinstance(value, list):
            self.insert(tk.END, *value)
        else:
            self.insert(tk.END, value)

        return "break"

    def move(self, index: int, direction: int):
        """
        Move a element inside the list box around.

        Parameters
        --------------
        index: int
            Index of the element to move.
        direction: int
            To move forward pass 1, to move backwards pass -1.
        """
        if direction == -1 and index == 0 or direction == 1 and index == len(self._original_items) - 1:
            return

        value = self._original_items[index]
        self.delete(index)
        index += direction
        self.insert(index, value)
        self.selection_set(index)

    def move_selection(self, direction: int):
        """
        Moves the selected element up inside the list box.
        Pass ``direction`` value 1 if you want to move forward, or -1 for backwards.
        """
        if len(selection := self.curselection()) == 1:
            self.move(selection[0], direction)
        else:
            Messagebox.show_error("Selection error", "Select ONE item!", parent=self)


@doc_category("Storage widgets")
class ListBoxScrolled(ctk.CTkFrame):
    """
    A scrollable version of :class:`tkclasswiz.storage.ListBoxObjects`.
    All the methods are the same as :class:`tkclasswiz.storage.ListBoxObjects`.
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master)
        listbox = ListBoxObjects(self, *args, **kwargs)
        self.listbox = listbox

        listbox.pack(side="left", fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        scrollbar.configure(command=listbox.yview)

        listbox.configure(yscrollcommand=scrollbar.set)

    def __getattr__(self, name: str):
        """
        Getter method that only get's called if the current
        implementation does not have the requested attribute.
        """
        return getattr(self.listbox, name)


@doc_category("Storage widgets")
class ComboBoxObjects(ttk.Combobox):
    """
    Modified version of :class:`tkinter.Combobox`, which:

    - Allows copy-paste and also sets the standard keyboard shortcuts for it
    - Overwrites the ``get`` method to return the original objects instead of text
    - Modifies the ``insert`` method to insert original objects instead of text
    """
    def __init__(self, *args, **kwargs):
        self._original_items = []
        super().__init__(*args, **kwargs)
        self.bind("<Control-c>", lambda e: self.save_to_clipboard())
        self.bind("<Control-v>", lambda e: self.paste_from_clipboard())

    def save_to_clipboard(self):
        """
        Saves selected element to Clipboard.
        """
        to_clipboard = base64.b64encode(pickle.dumps(convert_to_dict(self.get()))).decode('ascii')
        self.clipboard_clear()
        self.clipboard_append(to_clipboard)
        return "break"

    def paste_from_clipboard(self):
        value = self.clipboard_get()
        with suppress(Exception):
            value = convert_from_dict(pickle.loads(base64.b64decode(value)))

        if value not in self._original_items:
            self.insert(tk.END, value)

        self.current(self._original_items.index(value))
        return "break"

    def get(self) -> Any:
        "Returns selected element"
        index = self.current()
        if isinstance(index, int) and index >= 0:
            return self._original_items[index]

        return super().get()

    def delete(self, index: int) -> None:
        """
        Removes the element at ``index``.
        """
        self._original_items.pop(index)
        super().delete(index)

    def insert(self, index: Union[int, str], element: Any) -> None:
        """
        Insert the ``element`` to the spot at ``index``.
        """
        if index == tk.END:
            self._original_items.append(element)
        else:
            self._original_items.insert(index, element)

        self._update_internal()

    def count(self) -> int:
        "Returns number of elements inside the ComboBox"
        return len(self._original_items)

    def set_values(self, values: list):
        self._original_items = values
        self._update_internal()

    def get_values(self):
        return self._original_items

    def _update_internal(self):
        "Updates internal Tkinter's combobox."
        self["values"] = [str(x)[:200] for x in self._original_items]


@doc_category("Storage widgets")
class ComboEditFrame(ttk.Frame):
    """
    Frame, which combines :class:`tkclasswiz.storage.ComboBoxObjects` and an edit button.
    The edit button will open an object edit window / wizard and load in the old object (ObjectInfo) data.

    Parameters
    ----------------
    edit_method: Callable
        Function that opens the object edit window.
        This should either be :py:meth:`tkclasswiz.object_frame.window.ObjectEditWindow.open_object_edit_frame`,
        :py:meth:`tkclasswiz.object_frame.frame_base.NewObjectFrameBase.new_object_frame` or 
        a function that calls one of the previous 2 methods - this can be used to eg. load extra values into
        :class:`tkclasswiz.object_frame.frame_base.NewObjectFrameStruct`'s comboboxes by passing in the 
        ``additional_values`` mapping.

    values: list[Any]
        List of values that the combobox will have.
    master: Optional[:class:`tkinter.Widget`]
        The master widget.
    args
        Extra positional arguments to pass to :class:`tkinter.Frame``
    kwargs
        Extra keyword arguments to pass to :class:`tkinter.Frame``
    """
    def __init__(
        self,
        edit_method: Callable,
        values: List[Any] = [],
        master=None,
        *args,
        **kwargs
    ):
        super().__init__(*args, master=master, **kwargs)
        combo = ComboBoxObjects(self)
        ttk.Button(self, text="Edit", command=self._edit).pack(side="right")
        combo.pack(side="left", fill=tk.X, expand=True)
        self.combo = combo
        self.edit_method = edit_method
        self.set_values(values)

    def set_values(self, values: list):
        "Sets the combobox values to ``values``."
        self.combo.set_values(values)
        self.combo.current(0)

    def get_values(self):
        "Returns the combobox's values."
        return self.combo.get_values()

    def _edit(self):
        selection = self.combo.current()
        if selection >= 0:
            object_: ObjectInfo = self.combo.get()
            self.edit_method(
                object_.class_,
                self.combo,
                old_data=object_,
            )
        else:
            Messagebox.show_error("Empty list!", "Select atleast one item!")


class FrameWrapper(ctk.CTkFrame):
    def __init__(self, padding=None, **kwargs):
        super().__init__(**kwargs)
        self.padding = padding

    def pack(self, **kwargs):
        padding = self.padding or (kwargs.get("padx", 0), kwargs.get("pady", 0))
        if padding is None:
            padding = (0, 0)

        kwargs["padx"] = padding[0]
        kwargs["pady"] = padding[1]
        super().pack(**kwargs)


class BackendCustomTkinter(BackendBase):
    def message_box(self):
        return Messagebox

    def file_dialog(self):
        return filedialog

    def frame(self, **kwargs):
        return FrameWrapper(**kwargs)

    def label(self, **kwargs):
        if "style" in kwargs:
            del kwargs["style"]

        return ctk.CTkLabel(**kwargs)

    def separator(self, **kwargs):
        return ttk.Separator(**kwargs)

    def button(self, **kwargs):
        return ctk.CTkButton(**kwargs)

    def menu_button(self, **kwargs):
        return tk.Menubutton(**kwargs)

    def menu(self, **kwargs):
        return tk.Menu(**kwargs)

    def spinbox(self, **kwargs):
        return ttk.Spinbox(**kwargs)

    def toplevel(self, **kwargs):
        return tk.Toplevel(**kwargs)

    def style(self, **kwargs):
        return ttk.Style(**kwargs)

    def boolean_var(self, **kwargs):
        return tk.BooleanVar(**kwargs)

    def checkbutton(self, **kwargs):
        return tk.Checkbutton(**kwargs)

    def entry(self, **kwargs):
        return ttk.Entry(**kwargs)

    def scrollbar(self, **kwargs):
        return ttk.Scrollbar(**kwargs)

    def hinted_entry(self, **kwargs):
        hint = kwargs.pop("hint")
        return ctk.CTkEntry(**kwargs, placeholder_text=hint)

    def object_scalar(self, **kwargs):
        return PyObjectScalar(**kwargs)

    def text(self, **kwargs):
        return Text(**kwargs)

    def listbox(self, **kwargs):
        return ListBoxObjects(**kwargs)

    def scrolled_listbox(self, **kwargs):
        return ListBoxScrolled(**kwargs)

    def combobox(self, **kwargs):
        return ComboBoxObjects(**kwargs)

    def combo_edit_frame(self, **kwargs):
        return ComboEditFrame(**kwargs)
