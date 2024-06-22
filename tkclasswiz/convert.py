"""
Modules contains definitions related to GUI object transformations.
"""
from __future__ import annotations
from typing import Any, Union, List, Generic, TypeVar, Mapping, Optional, Callable
from contextlib import suppress
from inspect import signature
from enum import Enum

from .utilities import import_class
from .extensions import extendable
from .cache import cache_result
from .annotations import *
from .aliasing import *
from .doc import doc_category

import datetime as dt
import warnings
import decimal


__all__ = (
    "ObjectInfo",
    "convert_to_objects",
    "convert_to_object_info",
    "convert_to_dict",
    "convert_from_dict",
    "convert_objects_to_script",
    "_convert_to_objects_cached",
)

TClass = TypeVar("TClass")


CONVERSION_ATTR_TO_PARAM = {
    dt.timezone: {
        "offset": lambda timezone: timezone.utcoffset(None),
        "name": lambda timezone: timezone.tzname(None)
    },
}


@doc_category("Conversion")
def register_object_objectinfo_rule(cls: type, mapping: Optional[dict] = {}, **kwargs):
    """
    Used for adding new conversion rules when converting from Python objects
    into abstract ObjectInfo objects (GUI objects).

    These rules will be used when calling the ``convert_to_object_info`` function.

    If rules for ``cls`` do not exist, the conversion function will assume parameters
    are located under the same attribute name.

    A neat way to avoid registering custom conversion rules, is to store the attributes either under
    the same name as the parameter, or store them under a different name and create a ``@property``
    getter which has the same name as the parameter.

    Parameters
    ------------
    mapping: Optional[Dict[str, Union[Callable[[T], Any]], str]]
        Mapping mapping the parameter name to attribute from which to obtain the value.
        Values of mapping can also be a getter function, that accepts the object as parameter.
    kwargs: Optional[Unpack[str, Union[Callable[[T], Any]], str]]
        Keyword arguments mapping parameter name to attribute names from which to obtain the value.
        Values of mapping can also be a getter function, that accepts the object as parameter.

    Example
    ----------
    .. code-block:: python

        class FILE:
            def __init__(self, filename: str):
                self.fullpath = filename

        register_object_objectinfo_rule(
            FILE,
            filename="fullpath"
        )

        # Timezone
        import datetime
        register_object_objectinfo_rule(
            datetime.timezone,
            offset=lambda timezone: timezone.utcoffset(None)
        )
    """

    if cls not in CONVERSION_ATTR_TO_PARAM:
        CONVERSION_ATTR_TO_PARAM[cls] = {}

    CONVERSION_ATTR_TO_PARAM[cls].update(**kwargs, **mapping)


@doc_category("Conversion")
def get_object_objectinfo_rule_map(cls: type) -> dict:
    """
    Returns the conversion mapping for ``cls``

    Returns
    ----------
    Dict[str, Union[Callable[[T], Any]], str]
        Mapping of parameter name to the attribute name or getter function.
    """
    return CONVERSION_ATTR_TO_PARAM.get(cls, {})


@extendable
@doc_category("Conversion")
class ObjectInfo(Generic[TClass]):
    """
    A GUI object that represents real objects.
    The GUI only knows how to work with ObjectInfo objects, iterables and primitive-like types.

    **NOTE**: If the class has any password like fields, they can be specified by
    the class ``__passwords__`` attribute, which is an iterable of strings.

    Parameters
    -----------------
    class_: type
        Real object's type.
    data: dict
        Dictionary mapping to real object's parameters
    nickname: Optional[str]
        Add a nickname to the defined object for easier
        recognition.
    """
    CHARACTER_LIMIT = 150
    custom_display_map: dict[type, Callable] = {}

    def __init__(
        self,
        class_,
        data: Mapping,
        nickname: Optional[str] = None,
    ) -> None:
        self.class_ = class_
        self.data = data
        self.nickname = nickname
        self.__hash = 0
        self._repr = None

    @extendable
    def __eq__(self, _value: object) -> bool:
        if isinstance(_value, ObjectInfo):
            return self.class_ is _value.class_ and self.data == _value.data

        return False

    def __hash__(self) -> int:
        if not self.__hash:
            try:
                self.__hash = hash(self.data)
            except TypeError:
                self.__hash = -1

        return self.__hash

    def __repr__(self) -> str:
        if self._repr is not None:
            return self._repr

        repr_get = ObjectInfo.custom_display_map.get(self.class_, self._repr_default)
        _ret = repr_get(self)

        self._repr = _ret
        return _ret
    
    @staticmethod
    def _repr_default(object_info: ObjectInfo) -> str:
        _ret: List[str] = []
        if object_info.nickname:
            _ret += f"({object_info.nickname}) "

        name = get_aliased_name(object_info.class_)
        if name is not None:
            name += f'({object_info.class_.__name__})'
        else:
            name = object_info.class_.__name__

        _ret +=  name + "("
        private_params = set()
        if hasattr(object_info.class_, "__passwords__"):
            private_params = private_params.union(object_info.class_.__passwords__)

        for k, v in object_info.data.items():
            if len(_ret) > object_info.CHARACTER_LIMIT:
                break

            if isinstance(v, str):
                if k in private_params:
                    v = len(v) * '*'  # Hide password types

                v = f'"{v}"'
            else:
                v = str(v)

            _ret += f"{k}={v}, "

        _ret: str = ''.join(_ret)
        _ret = _ret.rstrip(", ") + ")"
        if len(_ret) > object_info.CHARACTER_LIMIT:
            _ret = _ret[:object_info.CHARACTER_LIMIT] + "...)"

        return _ret

    @classmethod
    def register_repr(cls, class_: type, repr: Callable[[ObjectInfo], str], inherited: bool = False):
        """
        Registers a custom __repr__ (string representation of object) function.
        The function must as a single parameter accept the ``ObjectInfo`` instance
        being represented as a string.

        Parameters
        ------------
        class_: type
            The class for which this custom ``repr`` is being register.
        repr: Callable[[ObjectInfo], str]
            The function that will provide custom ``__repr__``.
            As a parameter it accepts the ``ObjectInfo`` object.
            It returns a :class:`str` (string).
        inherited: bool
            Boolean flag. Setting it to True will register repr for inherited members as well.
            Defaults to False.
        """
        cls.custom_display_map[class_] = repr
        if inherited:
            for type_ in class_.__subclasses__():
                cls.register_repr(type_, repr, True)

@cache_result(max=1024)
@doc_category("Conversion")
def convert_objects_to_script(object: Union[ObjectInfo, list, tuple, set, str]):
    """
    Converts ObjectInfo objects into equivalent Python code.
    """
    object_data = []
    import_data = []

    if isinstance(object, ObjectInfo):
        object_str = f"{object.class_.__name__}(\n    "
        attr_str = []
        for attr, value in object.data.items():
            value, import_data_ = convert_objects_to_script(value)
            import_data.extend(import_data_)
            attr_str.append(f"{attr}={value},\n")

        import_data.append(f"from {object.class_.__module__} import {object.class_.__name__}")
        object_str += "    ".join(''.join(attr_str).splitlines(True)) + ")"
        object_data.append(object_str)

    elif isinstance(object, (list, tuple, set)):
        _list_data = ["[\n"]
        for element in object:
            object_str, import_data_ = convert_objects_to_script(element)
            _list_data.append(object_str + ",\n")
            import_data.extend(import_data_)

        _list_data = "    ".join(''.join(_list_data).splitlines(keepends=True)) + "]"
        object_data.append(_list_data)

    elif isinstance(object, Enum):
        type_name = type(object).__name__
        import_data.append(f"from {object.__module__} import {type_name}")
        object_name = object._name_
        if not object_name:
            name = f"{type_name}({object._value_})"
        else:
            name = ' | '.join(map(lambda name: f"{type_name}.{name}", object_name.split('|')))

        object_data.append(name)

    else:
        if isinstance(object, str):
            object = object.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
            object_data.append(f'"{object}"')
        else:
            object_data.append(str(object))

    return ",".join(object_data).strip(), sorted(set(import_data), key=lambda x: len(x), reverse=True)


@extendable
@cache_result(16_384)
@doc_category("Conversion")
def convert_to_object_info(object_: object, **kwargs):
    """
    Converts an object into ObjectInfo.

    Parameters
    ---------------
    object_: object
        The object to convert.
    """
    def _convert_object_info(object_, object_type, attrs):
        data_conv = {}
        for k, v in attrs.items():
            with suppress(Exception):
                if callable(v):
                    value = v(object_)
                else:
                    value = getattr(object_, v)

                # Check if object is a singleton that is not builtin.
                # Singletons should not be stored as they would get recreated causing issues on save -> load.
                type_value = type(value)
                with suppress(ValueError):  # Some don't have a signature
                    if type_value.__name__ not in __builtins__ and not len(signature(type_value).parameters):
                        continue

                if value is object_:
                    data_conv[k] = value
                else:
                    data_conv[k] = convert_to_object_info(value, **kwargs)

        ret = ObjectInfo(object_type, data_conv)
        return ret

    def get_conversion_map(object_type):
        attrs = CONVERSION_ATTR_TO_PARAM.get(object_type)
        if attrs is None:
            attrs = {k:k for k in get_annotations(object_type)}

        attrs.pop("return", None)
        return attrs

    object_type = type(object_)
    if object_type in {int, float, str, bool, decimal.Decimal, type(None)} or isinstance(object_, Enum):
        if object_type is decimal.Decimal:
            object_ = float(object_)

        return object_

    if isinstance(object_, (set, list, tuple)):
        object_ = [convert_to_object_info(value, **kwargs) for value in object_]
        return object_
    
    if isinstance(object_, dict):
        return ObjectInfo(
            dict,
            {k: convert_to_object_info(v, **kwargs) for k, v in object_.items()},
        )


    attrs = get_conversion_map(object_type)
    return _convert_object_info(object_, object_type, attrs)


@cache_result()
def _convert_to_objects_cached(*args, **kwargs):
    return convert_to_objects(*args, **kwargs)


@doc_category("Conversion")
def convert_to_objects(
    d: Union[ObjectInfo, dict, list],
) -> Union[object, dict, List]:
    """
    Converts :class:`ObjectInfo` instances into actual objects,
    specified by the ObjectInfo.class\ _ attribute.

    Parameters
    -----------------
    d: ObjectInfo | list[ObjectInfo] | dict
        The object(s) to convert. Can be an ObjectInfo object, a list of ObjectInfo objects or a dictionary that is a
        mapping of ObjectInfo parameters.
    cached: bool
        If True items will be returned from cache. ONLY USE FOR IMMUTABLE USE.
    """
    def convert_object_info():
        data_conv = {
            k:
            convert_to_objects(v)
            if isinstance(v, (list, tuple, set, ObjectInfo, dict)) else v
            for k, v in d.data.items()
        }

        new_obj = d.class_(**data_conv)
        return new_obj

    if isinstance(d, (list, tuple, set)):
        return [convert_to_objects(item) for item in d]
    if isinstance(d, ObjectInfo):
        return convert_object_info()
    if isinstance(d, dict):
        return {k: convert_to_objects(v) for k, v in d.items()}

    return d


@cache_result()
@doc_category("Conversion")
def convert_to_dict(d: Union[ObjectInfo, List[ObjectInfo], Any]):
    """
    Converts ObjectInfo into dictionary representation.
    """
    if isinstance(d, ObjectInfo):
        data_conv = {k: convert_to_dict(v) for k, v in d.data.items()}
        return {"type": f"{d.class_.__module__}.{d.class_.__name__}", "data": data_conv, "nickname": d.nickname}

    if isinstance(d, list):
        return [convert_to_dict(x) for x in d]

    if issubclass((type_d := type(d)), Enum):
        return {"type": f"{type_d.__module__}.{type_d.__name__}", "value": d.value}

    return d


@cache_result()
@doc_category("Conversion")
def convert_from_dict(d: Union[dict, List[dict], Any]) -> ObjectInfo:
    """
    Converts previously converted dict back to ObjectInfo.
    """
    if isinstance(d, list):
        result = [convert_from_dict(item) for item in d]
        return result

    if isinstance(d, dict):
        type_ = import_class(d["type"])

        if "value" in d:  # Enum type or a single value type
            return type_(d["value"])

        annotations = get_annotations(type_)
        data = {}
        for k, v in d["data"].items():
            if k in annotations:
                data[k] = convert_from_dict(v)
            else:
                warnings.warn(f"Parameter {k} does not exist in {type_}, ignoring.")

        return ObjectInfo(type_, data, d.get('nickname'))

    return d
