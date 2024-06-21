"""
Backend package.
Allows different libraries to work with TkClassWizard.
"""
from .base import BackendBase
from .tkinter import BackendTkinter

__all__ = ("set_backend", "get_backend")


BACKEND_MAP = {
    "tkinter": BackendTkinter
}

class GLOBAL:
    backend: BackendBase = BackendTkinter()

def set_backend(backend: str):
    "Changes the backend corresponding to ``backend`` string."
    GLOBAL.backend = BACKEND_MAP[backend]()


def get_backend() -> BackendBase:
    "Returns the current backend object"
    return GLOBAL.backend
