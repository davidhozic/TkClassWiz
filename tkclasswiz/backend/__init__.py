"""
Backend package.
Allows different libraries to work with TkClassWizard.
"""
from .customtkinter import BackendCustomTkinter
from .tkinter import BackendTkinter
from .base import BackendBase


__all__ = ("set_backend", "get_backend")


BACKEND_MAP = {
    "customtkinter": BackendCustomTkinter,
    "tkinter": BackendTkinter,
}

class GLOBAL:
    backend: BackendBase = BackendTkinter()

def set_backend(backend: str):
    "Changes the backend corresponding to ``backend`` string."
    GLOBAL.backend = BACKEND_MAP[backend]()


def get_backend() -> BackendBase:
    "Returns the current backend object"
    return GLOBAL.backend
