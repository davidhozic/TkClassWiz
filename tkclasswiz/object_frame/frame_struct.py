from typing import get_args, get_origin, Iterable, Union, Literal, Dict, Tuple
from functools import partial
from enum import Enum, Flag


from ..convert import *
from ..dpi import *
from ..utilities import *
from ..storage import *
from ..extensions import extendable
from ..annotations import get_annotations, convert_types
from ..deprecation import *
from ..doc import doc_category

from .frame_base import *
from .tooltip import ComboboxTooltip

import tkinter as tk
import inspect
import copy
import json


__all__ = (
    "NewObjectFrameStruct",
    "NewObjectFrameStructView",
)


@extendable
@doc_category("Object frames")
class NewObjectFrameStruct(NewObjectFrameBase):
    """
    Frame for inside the :class:`ObjectEditWindow` that allows object definition.

    Parameters
    -------------
    class_: Any
        The class we are defining for.
    return_widget: ComboBoxObjects | ListBoxScrolled
        The widget to insert the ObjectInfo into after saving.
    parent: TopLevel
        The parent window.
    old_data: ObjectInfo
        The old_data ObjectInfo object to edit.
    check_parameters: bool
        Check parameters (by creating the real object) upon saving.
        This is ignored if editing a function instead of a class.
    allow_save: bool
        If False, will open in read-only mode.
    additional_values: Dict[str, Any]
        A mapping of additional values to be inserted into corresponding field.
    """
    def __new__(cls, *args, **kwargs):
        if kwargs.get("allow_save", True):
            obj = super().__new__(NewObjectFrameStruct)
        else:
            obj = super().__new__(NewObjectFrameStructView)

        return obj

    def __init__(
        self,
        class_,
        return_widget: Union[ComboBoxObjects, ListBoxScrolled],
        parent = None,
        old_data: ObjectInfo = None,
        check_parameters: bool = True,
        allow_save = True,
        additional_values: dict = {},
        _annotations_override: dict = None,
    ):
        super().__init__(class_, return_widget, parent, old_data, check_parameters,allow_save)
        self._map: Dict[str, Tuple[ComboBoxObjects, Iterable[type]]] = {}
        dpi_5 = dpi_scaled(5)
        dpi_5_h = dpi_5 // 2

        if not (annotations := _annotations_override or get_annotations(class_)):
            raise TypeError("This object cannot be edited.")

        # Template
        @gui_except(window=self)
        def save_template():
            filename = self.backend.file_dialog().asksaveasfilename(filetypes=[("JSON", "*.json")], parent=self)
            if filename == "":
                return

            json_data = convert_to_dict(self.to_object(ignore_checks=True))

            if not filename.endswith(".json"):
                filename += ".json"

            with open(filename, "w", encoding="utf-8") as file:
                json.dump(json_data, file, indent=2)

            self.backend.message_box().show_info("Finished", f"Saved to {filename}", parent=self)

        @gui_except(window=self)
        def load_template():
            filename = self.backend.file_dialog().askopenfilename(filetypes=[("JSON", "*.json")], parent=self)
            if filename == "":
                return

            with open(filename, "r", encoding="utf-8") as file:
                json_data: dict = json.loads(file.read())
                object_info = convert_from_dict(json_data)
                # Get class_ attribute if we have the ObjectInfo type, if not just compare the actual type
                if object_info.class_ is not self.class_:
                    raise TypeError(
                        f"The selected template is not a {self.class_.__name__} template.\n"
                        f"The requested template is for type: {object_info.class_.__name__}!"
                    )

                self.load(object_info)

        bnt_menu_template = self.backend.menu_button(self.frame_toolbar, text="Template")
        menu = self.backend.menu(bnt_menu_template)
        menu.add_command(label="Load template", command=load_template)
        menu.add_command(label="Save template", command=save_template)
        bnt_menu_template.configure(menu=menu)
        bnt_menu_template.pack(side="left")

        # Nickname entry
        self.entry_nick = HintedEntry(
            "Object nickname",
            self.frame_main,
            state="normal" if self.allow_save else "disabled"
        )
        self.entry_nick.pack(anchor=tk.W, padx=dpi_5_h, pady=dpi_5)
        annotations_depr = {k:v for k,v in annotations.items() if is_deprecated(class_, k)}
        for k in annotations_depr:
            del annotations[k]

        self._create_fields(annotations, additional_values, self.frame_main)
        if annotations_depr:
            self.backend.separator(self.frame_main).pack(fill=tk.X, pady=dpi_5)
            self.backend.label(self.frame_main, text="Deprecated", font=("TkDefaultFont", 10)).pack(anchor=tk.W)
            self._create_fields(annotations_depr, additional_values, self.frame_main)

        if old_data is not None:  # Edit
            self.load(old_data)

        self.remember_gui_data()

    def _create_fields(self, annotations: dict[str, type], additional_values: dict, frame):
        dpi_5 = dpi_scaled(5)
        dpi_5h = dpi_5 // 2

        labels: list = []

        # Get parameters with default values.
        # This is used for adding an asterisk to parameters without a default (mandatory parameters).
        signature = inspect.signature(self.class_)
        param_defaults = set([k for k, v in signature.parameters.items() if v.default is not v.empty])

        for (k, v) in annotations.items():
            # Init widgets
            entry_types = convert_types(v)
            frame_annotated = self.backend.frame(frame)
            frame_annotated.pack(fill=tk.BOTH, expand=True, pady=dpi_5)

            text = k
            if k not in param_defaults:  # Parameter is mandatory
                text = f'* {text}'

            label = self.backend.label(frame_annotated, text=text)
            labels.append(label)
            label.pack(side="left")

            # Storage widget with the tooltip for displaying
            # nicknames on ObjectInfo instances
            w = combo = ComboBoxObjects(frame_annotated)
            ComboboxTooltip(w.combo)

            bnt_new_menu = self.backend.menu_button(frame_annotated, text="New")
            menu_new = self.backend.menu(bnt_new_menu)
            bnt_new_menu.configure(menu=menu_new)

            deprecated_param_types = set(t for t in entry_types if is_deprecated(self.class_, k, t))
            normal_types = [t for t in entry_types if t not in deprecated_param_types]
            any_filled = self._fill_field_values(k, normal_types, menu_new, combo, additional_values)

            if deprecated_param_types:
                menu_depr = self.backend.menu(menu_new)
                menu_new.add_cascade(label=">Deprecated", menu=menu_depr)
                any_filled = self._fill_field_values(
                    k,
                    list(deprecated_param_types),
                    menu_depr,
                    combo,
                    additional_values
                ) or any_filled

            bnt_edit = self.backend.button(
                frame_annotated,
                text="🖋️",
                width=3,
                command=partial(self._edit_selected, k, w)
            )

            bnt_copy_paste = self.backend.menu_button(frame_annotated, text="C/P")
            copy_menu = self.backend.menu(bnt_copy_paste)
            copy_menu.add_command(label="Copy", command=combo.save_to_clipboard)
            copy_menu.add_command(label="Paste", command=combo.paste_from_clipboard)
            bnt_copy_paste.configure(menu=copy_menu)

            if not (any_filled and self.allow_save):
                bnt_new_menu.configure(state="disabled")

            bnt_copy_paste.pack(side="right", padx=dpi_5h)
            bnt_edit.pack(side="right", padx=dpi_5h)
            bnt_new_menu.pack(side="right", padx=dpi_5h)
            combo.pack(fill=tk.X, side="right", expand=True, padx=dpi_5h)
            self._map[k] = (w, entry_types)

        max_width = max(label.winfo_reqwidth() for label in labels) // 5
        for label in labels:
            label.config(width=max_width)

    def _fill_field_values(
        self,
        k: str,
        entry_types: list,
        menu,
        combo: ComboBoxObjects,
        additional_values: dict
    ):
        "Fill ComboBox values based on types in ``entry_types`` and create New <object_type> buttons"
        any_filled = False
        for entry_type in entry_types:
            if get_origin(entry_type) is Literal:
                values = get_args(entry_type)
                combo["values"] = values
                # tkvalid.add_option_validation(combo, values)
            elif entry_type is bool:
                combo.insert(tk.END, True)
                combo.insert(tk.END, False)
                # tkvalid.add_option_validation(combo, ["True", "False", ''])
            elif issubclass_noexcept(entry_type, Enum) and not issubclass_noexcept(entry_type, Flag):
                combo["values"] = values = [en for en in entry_type]
                # tkvalid.add_option_validation(combo, list(map(str, values)) + [''])
            elif entry_type is type(None):
                if bool not in entry_types:
                    combo.insert(tk.END, None)
            else:  # Type not supported, try other types
                any_filled = True
                if self.allow_save:
                    menu.add_command(
                        label=f"New {self.get_cls_name(entry_type, args=True)}",
                        command=partial(self.new_object_frame, entry_type, combo)
                    )

        # Additional values to be inserted into ComboBox
        for value in additional_values.get(k, []):
            combo.insert(tk.END, value)

        # The class of last list like type. Needed when "Edit selected" is used
        # since we don't know what type it was
        return any_filled

    @extendable
    def load(self, old_data: ObjectInfo):
        data = old_data.data
        for attr, (widget, types_) in self._map.items():
            if attr not in data:
                continue

            val = data[attr]

            if val not in widget.get_values():
                widget.insert(tk.END, val)

            widget.current(widget.get_values().index(val))

        if old_data.nickname:
            self.entry_nick.insert('0', old_data.nickname)

        self.old_gui_data = old_data

    @extendable
    def to_object(self, *, ignore_checks = False) -> ObjectInfo:
        """
        Converts GUI data into an ObjectInfo abstraction object.

        Parameters
        ------------
        ignore_checks: bool
            Don't check the correctness of given parameters.
        """
        map_ = {}
        widget: ComboBoxObjects
        for attr, (widget, types_) in self._map.items():
            value = widget.get()
            # Either it's a string needing conversion or a Literal constant not to be converted
            if isinstance(value, str):
                if not value:
                    continue

                try:
                    value = self.cast_type(value, types_)
                except TypeError as exc:
                    # Perhaps it's a valid literal:
                    literal_types = self.filter_literals(types_)
                    if not literal_types:
                        raise

                    self.check_literals(value, literal_types)

            map_[attr] = value

        class_ = get_origin(self.class_) or self.class_
        nickname = self.entry_nick.get() or None
        object_ = ObjectInfo(class_, map_, nickname)  # Abstraction of the underlying object
        if (
            not ignore_checks and
            self.check_parameters and
            (inspect.isclass(class_))  # Only check objects
        ):
            # Cache the object created for faster
            _convert_to_objects_cached(object_)  # Tries to create instances to check for errors

        return object_

    def get_gui_data(self) -> dict:
        values = {}
        for attr, (widget, types_) in self._map.items():
            value = widget.get()
            if isinstance(value, str) and not value:  # Ignore empty values
                continue

            if isinstance(value, (list, tuple, set)):  # Copy lists else the values would change in the original state
                value = copy.copy(value)

            values[attr] = value

        return values

    @gui_except()
    def _edit_selected(self, key: str, combo: ComboBoxObjects):
        selection = combo.get()

        # Convert selection to any of the allowed types.
        # This is used for casting manually typed values (which are strings) into appropriate types
        # Eg. if a number is manually typed in and Edit button is clicked, this would result in a string type
        # edit request, which is not really the intend. The intend is to edit a number in this example.
        if isinstance(selection, str):
            selection = self.cast_type(selection, self._map[key][1])

        if isinstance(selection, ObjectInfo):
            return self.new_object_frame(selection.class_, combo, old_data=selection)
        else:
            type_sel = type(selection)
            for t in convert_types(get_annotations(self.class_)[key]):
                if (get_origin(t) or t) == type_sel:
                    type_ = t
                    break
            else:
                type_ = None

            return self.new_object_frame(type_, combo, old_data=selection)


class NewObjectFrameStructView(NewObjectFrameStruct):
    """
    Same as :class:`NewObjectFrameStruct`, but creates a wrapper Viewer class, which's attributes automatically
    get mapped as annotations, which the :class:`NewObjectFrameStruct` knows how to handle.
    """
    def __init__(self, class_, *args, **kwargs):
        old_data: ObjectInfo = kwargs["old_data"]
        annotations = {k: v.class_ if isinstance(v, ObjectInfo) else type(v) for k, v in old_data.data.items()}
        super().__init__(class_, *args, **kwargs, _annotations_override=annotations)

    @gui_except()
    def _edit_selected(self, key: str, combo: ComboBoxObjects):
        selection = combo.get()

        # Convert selection to any of the allowed types.
        # This is used for casting manually typed values (which are strings) into appropriate types
        # Eg. if a number is manually typed in and Edit button is clicked, this would result in a string type
        # edit request, which is not really the intend. The intend is to edit a number in this example.
        if isinstance(selection, str):
            selection = self.cast_type(selection, self._map[key][1])

        if isinstance(selection, ObjectInfo):
            return self.new_object_frame(selection.class_, combo, old_data=selection)
        else:
            return self.new_object_frame(type(selection), combo, old_data=selection)
