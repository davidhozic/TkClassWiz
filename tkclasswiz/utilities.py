"""
Utility module.
"""
from typing import Any, Callable, Tuple
from functools import wraps, partialmethod

from .doc import doc_category, DOCUMENTATION_MODE
from .backend import get_backend

import importlib


__all__ = (
    "import_class",
    "gui_except",
    "gui_confirm_action",
    "issubclass_noexcept",
)


@doc_category("Utilities")
def import_class(path: str) -> type:
    """
    Imports the class provided by it's ``path``.
    """
    path = path.split(".")
    module_path, class_name = '.'.join(path[:-1]), path[-1]
    try:
        module = importlib.import_module(module_path)
    except Exception as exc:  # Fall back for older versions, try to import from package instead of module
        module_path = module_path.split('.')[0]
        module = importlib.import_module(module_path)

    class_ = getattr(module, class_name)
    return class_


@doc_category("Utilities")
def gui_except(window = None):
    """
    Function that returns a decorator.
    The decorator returns a callable wrapper object.

    When the wrapper is called, it calls the original callee, and in case an exception is raised,
    the exception is displayed through a popup window.
    If no exception is raised, the callee's result is returned.


    Parameters
    --------------
    window: Optional[Any]
        Optional parent widget, if not provided, the owner of callee method will be used.

    Example
    ----------

    .. code-block:: python
    
        class MyWindow(tk.TopLevel):
            
            @gui_except()
            def raise_exceptions(self):
                raise ValueError("Test")
    """
    def decorator(fnc: Callable):
        if DOCUMENTATION_MODE:
            return fnc

        @wraps(fnc, updated=[])
        class wrapper:
            def __init__(self, instance = None) -> None:
                self.inst = instance
            
            def __get__(self, instance, cls = None):
                return wrapper(instance)
            
            def __call__(self, *args: Any, **kwargs: Any) -> Any:
                parent = window or self.inst
                try:
                    if self.inst is not None:
                        args = (self.inst, *args)

                    return fnc(*args, **kwargs)
                except Exception as exc:
                    get_backend().message_box().show_error(f"Exception in {fnc.__name__}", str(exc), parent=parent)

        return wrapper()

    return decorator


@doc_category("Utilities")
def gui_confirm_action(parent = None):
    """
    Function that returns a decorator.
    The decorator returns a callable wrapper object.

    When the wrapper is called, the user is asked to confirm the action and if the user confirms,
    the original function is called and the wrapper returns the result.
    If action is cancelled, None is returned by the wrapper.

    Parameters
    --------------
    parent: Optional[Any]
        Optional parent widget, if not provided, the owner of callee method will be used.


    Example
    -----------

    .. code-block:: python

        class Database(tk.Widget):
            @gui_confirm_action()
            def delete_database(self):
                print("Deleting database")
    """
    def _gui_confirm_action(fnc: Callable):
        if DOCUMENTATION_MODE:
            return fnc

        class wrapper:
            def __init__(self, bind = None) -> None:
                self.bind = bind

            def __call__(self, *args, **kwargs):
                if isinstance(parent, str):
                    parent_ = getattr(self.bind, parent)
                else:
                    parent_ = parent or self.bind

                result = get_backend().message_box().yesnocancel("Confirm", "Are you sure?", parent=parent_)

                if self.bind is not None:
                    args = (self.bind, *args)  # self, *args

                if result:
                    return fnc(*args, **kwargs)
                
            def __get__(self, instance, cls = None):
                return wrapper(instance)

        return wrapper()

    return _gui_confirm_action


@doc_category("Utilities")
def issubclass_noexcept(cls: type, bases: Tuple[type]):
    """
    Same as :func:`inspect.issubclass`, but instead of raising an exception
    when the second argument is not a class, it returns False.
    """
    try:
        return issubclass(cls, bases)
    except Exception:
        return False
