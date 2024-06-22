from abc import ABC, abstractmethod
from typing import Optional

from ..backend import get_backend
from ..convert import ObjectInfo
from ..storage import *


class BaseToolTip(ABC):
    """
    .. versionadded:: 1.2

    Used to display a nickname tooltip based on ``ObjectInfo.nickname`` attribute.
    It's triggered on ``enter_event`` after ``timeout_ms`` milliseconds and disappears on ``leave_event``.
    """

    def __init__(
        self,
        widget,
        timeout_ms: int = 500,
    ):
        self.backend = get_backend()
        self.toplevel = self.backend.toplevel(widget)
        self.backend.style().configure(
            style="tooltip.TLabel",  # ttkbootstrap compatibility
            background="white",
        )
        self.label = self.backend.label(self.toplevel, style="tooltip.TLabel", wraplength=1000)
        self.schedule_id = None
        self._widget = widget
        self.timeout_ms = timeout_ms
        self.label.pack()
        self.toplevel.pack_propagate(True)
        self._hide_tooltip()
        self.toplevel.overrideredirect(True)
        self.toplevel.attributes('-topmost', True)

    def _schedule(self, event):
        if not (value := self._get_value()):
            return

        self.label.config(text=str(value)[:3000])
        if self.timeout_ms:
            self.schedule_id = self.toplevel.after(self.timeout_ms, lambda: self._show_tooltip(event))
        else:
            self.toplevel.after_idle(lambda: self._show_tooltip(event))

    def _cancel_schedule(self, event):
        if self.schedule_id:
            self.toplevel.after_cancel(self.schedule_id)
            self.schedule_id = None

        self._hide_tooltip()

    def _show_tooltip(self, event):
        self.toplevel.geometry("")
        self.toplevel.deiconify()
        self._update_pos(event)
        self._widget.bind("<Motion>", self._update_pos)

    def _update_pos(self, event):
        geo = self.toplevel.geometry().split('+')[0]
        x, y = self.toplevel.winfo_pointerxy()
        self.toplevel.geometry(f'{geo}+{x + 10}+{y + 10}')

    def _hide_tooltip(self):
        self.toplevel.withdraw()

    @abstractmethod
    def _get_value(self) -> Optional[ObjectInfo]:
        pass


class ListboxTooltip(BaseToolTip):
    def __init__(self, widget, timeout_ms: int = 500):
        super().__init__(widget, timeout_ms)
        self._widget.bind("<<ListboxSelect>>", self._schedule)
        self._widget.bind("<Leave>", self._cancel_schedule)
        self.start_y = 0

    def _get_value(self):
        selection = self._widget.curselection()
        if len(selection) != 1:
            return
        value = self._widget.get(selection[0])
        return str(value)

    def _show_tooltip(self, event):
        self.start_y = self.toplevel.winfo_pointery()
        super()._show_tooltip(event)

    def _update_pos(self, event):
        super()._update_pos(event)
        if abs(self.start_y - self.toplevel.winfo_pointery()) > 10:
            self._cancel_schedule(event)


class ComboboxTooltip(BaseToolTip):
    def __init__(self, widget, timeout_ms: int = 500):
        super().__init__(widget, timeout_ms)
        self._widget.bind("<Enter>", self._schedule)
        self._widget.bind("<Leave>", self._cancel_schedule)

    def _get_value(self):
        value = self._widget.get()
        return str(value)
