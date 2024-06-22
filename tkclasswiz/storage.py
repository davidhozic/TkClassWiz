"""
Modules contains storage container widgets.
"""
from typing import Union, Any, List, Iterable, Callable

from .utilities import gui_confirm_action
from .convert import ObjectInfo
from .doc import doc_category
from .backend import get_backend

import tkinter as tk


__all__ = (
    "Text",
    "ListBoxObjects",
    "ListBoxScrolled",
    "ComboBoxObjects",
    "ComboEditFrame",
    "HintedEntry",
    "PyObjectScalar",
)


class _NoClipBoard:
    pass


class GLOBAL:
    clipboard = _NoClipBoard


@doc_category("Storage widgets")
class HintedEntry:
    """
    A hinted tkinter.ttk.Entry.
    The entry accepts the parameter ``hint`` (The hinting text which will be displayed in gray)
    and the original tkinter.ttk.Entry parameters.
    """
    def __init__(self, hint: str, *args, **kwargs):
        self.backend = get_backend()
        self.entry = self.backend.entry(*args, **kwargs)
        self.hint = hint
        self._set_hint()
        self.entry.bind("<FocusIn>", self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)

    def get(self) -> str:
        if str(self.entry["foreground"]) == "gray":
            return ''

        return self.entry.get()

    def pack(self, *args, **kwargs):
        return self.entry.pack(*args, **kwargs)

    def insert(self, *args, **kwargs) -> None:
        state = self.entry.cget("state")
        self.entry.config(state="enabled")
        if str(self.entry["foreground"]) == "gray":
            self.entry.delete('0', tk.END)

        _ret = self.entry.insert(*args, **kwargs)
        self.entry["foreground"] = "black"
        self.entry.config(state=state)
        return _ret

    def _set_hint(self):
        self.insert('0', self.hint)
        self.entry["foreground"] = "gray"

    def _focus_in(self, event):
        if str(self.entry["foreground"]) == "gray":
            self.entry["foreground"] = 'black'
            self.entry.delete('0', tk.END)

    def _focus_out(self, event):
        if not self.entry.get():
            self._set_hint()


@doc_category("Storage widgets")
class PyObjectScalar:
    """
    Represents a single storage widget for a Python object.
    """
    def __init__(self, *args, **kwargs) -> None:
        self.backend = get_backend()
        self.frame = self.backend.frame(*args, **kwargs)
        self.element = None
        self.display = self.backend.entry(self.frame, state="readonly")
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
        self.display.config(state="active")
        self.display.delete("0", tk.END)
        self.display.insert(tk.END, str(value))
        self.display.config(state="readonly")
        self.element = value

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)


@doc_category("Storage widgets")
class Text:
    """
    Modified version of :class`tkinter.Text`, which replaces the original
    ``get`` method to contain no parameters and instead return the entire text stripped.
    This is for compatibility with other storage widgets.
    """
    def __init__(self, *args, **kwargs) -> None:
        self.backend = get_backend()
        self.text = self.backend.text(*args, **kwargs)

    def get(self) -> str:
        "Returns entire text stripped."
        return self.text.get("1.0", tk.END).strip()
    
    def pack(self, *args, **kwargs):
        return self.text.pack(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.text.insert(*args, **kwargs)

@doc_category("Storage widgets")
class ListBoxObjects:
    """
    Modified version of :class:`tkinter.Listbox`, which:

    - Allows copy-paste and also sets the standard keyboard shortcuts for it
    - Implements the ``current`` method for compatibility with :class:`tkclasswiz.storage.ComboBoxObjects`
    - Overwrites the ``get`` method to return the original objects instead of text
    - Modifies the ``insert`` method to insert original objects instead of text
    """
    def __init__(self, *args, **kwargs):
        self.backend = get_backend()
        self.listbox = self.backend.listbox(*args, **kwargs)
        self.listbox.configure(selectmode=tk.EXTENDED)

        self._original_items = []
        self.listbox.bind("<Control-c>", lambda e: self.save_to_clipboard())
        self.listbox.bind("<BackSpace>", lambda e: self.delete_selected())
        self.listbox.bind("<Delete>", lambda e: self.delete_selected())
        self.listbox.bind("<Control-v>", lambda e: self.paste_from_clipboard())

    def current(self) -> int:
        "Returns index of the first currently selected element or -1 if none selected."
        selection = self.listbox.curselection()
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
        _ret = self.listbox.insert(index, *elements)
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
            self.listbox.delete(*range_)
            del self._original_items[range_[0]:range_[1] + 1]

    def count(self) -> int:
        """
        Returns the amount of elements inside the internal list.
        """
        return len(self._original_items)

    @gui_confirm_action("listbox")
    def delete_selected(self):
        """
        Deletes selected elements.
        """
        sel: List[int] = self.listbox.curselection()
        if len(sel):
            self.delete(*sel)
        else:
            self.backend.message_box().show_error("Empty list!", "Select atleast one item!", parent=self.listbox)

    def clear(self) -> None:
        """
        Deletes all the elements inside the internal list.
        """
        self.listbox.delete(0, tk.END)
        self._original_items.clear()

    def save_to_clipboard(self):
        """
        Saves selection to clipboard.
        """
        selection = self.listbox.curselection()
        if len(selection):
            object_: Union[ObjectInfo, Any] = self.get()[min(selection):max(selection) + 1]
            GLOBAL.clipboard = object_ if len(selection) > 1 else object_[0]
        else:
            self.backend.message_box().show_error("Empty list!", "Select atleast one item!", parent=self.listbox)

    def paste_from_clipboard(self):
        """
        Paste elements from clipboard.
        """
        if GLOBAL.clipboard is _NoClipBoard:
            return  # Clipboard empty

        if isinstance(GLOBAL.clipboard, Iterable):
            self.insert(tk.END, *GLOBAL.clipboard)
        else:
            self.insert(tk.END, GLOBAL.clipboard)

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
        self.listbox.selection_set(index)

    def move_selection(self, direction: int):
        """
        Moves the selected element up inside the list box.
        Pass ``direction`` value 1 if you want to move forward, or -1 for backwards.
        """
        if len(selection := self.curselection()) == 1:
            self.move(selection[0], direction)
        else:
            self.backend.message_box().show_error("Selection error", "Select ONE item!", parent=self.listbox)

    def yview(self, *args, **kwargs):
        return self.listbox.yview(*args, **kwargs)
    
    def pack(self, *args, **kwargs):
        return self.listbox.pack(*args, **kwargs)
    
    def config(self, *args, **kwargs):
        return self.listbox.config(*args, **kwargs)
    
    def select_clear(self, *args, **kwargs):
        self.listbox.select_clear(*args, **kwargs)
    
    def selection_set(self, *args, **kwargs):
        self.listbox.selection_set(*args, **kwargs)

    def curselection(self):
        return self.listbox.curselection()


@doc_category("Storage widgets")
class ListBoxScrolled:
    """
    A scrollable version of :class:`tkclasswiz.storage.ListBoxObjects`.
    All the methods are the same as :class:`tkclasswiz.storage.ListBoxObjects`.
    """
    def __init__(self, parent, *args, **kwargs):
        self.backend = get_backend()
        self.frame = self.backend.frame(parent)
        listbox = ListBoxObjects(self.frame, *args, **kwargs)
        self.listbox = listbox

        listbox.pack(side="left", fill=tk.BOTH, expand=True)

        scrollbar = self.backend.scrollbar(self.listbox.listbox)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        scrollbar.config(command=listbox.yview)

        listbox.config(yscrollcommand=scrollbar.set)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def save_to_clipboard(self):
        return self.listbox.save_to_clipboard()

    def paste_from_clipboard(self):
        return self.listbox.paste_from_clipboard()
    
    def delete_selected(self):
        return self.listbox.delete_selected()

    def get(self, *args, **kwargs):
        return self.listbox.get(*args, **kwargs)

    def count(self):
        return self.listbox.count()
    
    def insert(self, *args, **kwargs):
        return self.listbox.insert(*args, **kwargs)
    
    def select_clear(self, *args, **kwargs):
        return self.listbox.select_clear(*args, **kwargs)
    
    def selection_set(self, *args, **kwargs):
        return self.listbox.selection_set(*args, **kwargs)
    
    def curselection(self):
        return self.listbox.curselection()

    def current(self):
        return self.listbox.current()

    def delete(self, *indexes: int):
        return self.listbox.delete(*indexes)


@doc_category("Storage widgets")
class ComboBoxObjects:
    """
    Modified version of :class:`tkinter.Combobox`, which:

    - Allows copy-paste and also sets the standard keyboard shortcuts for it
    - Overwrites the ``get`` method to return the original objects instead of text
    - Modifies the ``insert`` method to insert original objects instead of text
    """
    def __init__(self, *args, **kwargs):
        self._original_items = []
        self.backend = get_backend()
        self.combo = self.backend.combobox(*args, **kwargs)

    def _update_combo(self):
        self.combo["values"] = [str(x)[:200] for x in self._original_items]

    def save_to_clipboard(self):
        """
        Saves selected element to Clipboard.
        """
        GLOBAL.clipboard = self.get()

    def paste_from_clipboard(self):
        "Paste element(s) from clipboard."
        value = GLOBAL.clipboard
        if value is _NoClipBoard:
            return
        
        if value not in self._original_items:
            self.insert(tk.END, value)
        
        self.combo.current(self._original_items.index(value))

    def set_values(self, values: list):
        """
        Sets the values of internal Combobox to ``values``.
        """
        self._original_items = values
        self._update_combo()

    def get_values(self) -> list:
        """
        Returns all the values inside the internal Combobox.
        """
        return self._original_items

    def get(self) -> Any:
        "Returns selected element"
        index = self.combo.current()
        if isinstance(index, int) and index >= 0:
            return self._original_items[index]

        return self.combo.get()

    def delete(self, index: int) -> None:
        """
        Removes the element at ``index``.
        """
        self._original_items.pop(index)
        self._update_combo()

    def insert(self, index: Union[int, str], element: Any) -> None:
        """
        Insert the ``element`` to the spot at ``index``.
        """
        if index == tk.END:
            self._original_items.append(element)
        else:
            self._original_items.insert(index, element)

        self._update_combo()

    def current(self, *args, **kwargs):
        return self.combo.current(*args, **kwargs)

    def count(self) -> int:
        "Returns number of elements inside the ComboBox"
        return len(self._original_items)
    
    def pack(self, *args, **kwargs):
        self.combo.pack(*args, **kwargs)


@doc_category("Storage widgets")
class ComboEditFrame:
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
        self.backend = get_backend()
        self.frame = self.backend.frame(*args, master=master, **kwargs)
        combo = ComboBoxObjects(self.frame)
        self.backend.button(self, text="Edit", command=self._edit).pack(side="right")
        combo.pack(side="left", fill=tk.X, expand=True)
        self.combo = combo
        self.edit_method = edit_method
        self.set_values(values)

    def set_values(self, values: List[Any] = []):
        "Sets the combobox values to ``values``."
        self.combo["values"] = values
        self.combo.current(0)

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
            self.backend.message_box().show_error("Empty list!", "Select atleast one item!")
