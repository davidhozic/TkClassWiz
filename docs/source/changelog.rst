========================
Changelog
========================
.. |BREAK_CH| replace:: **[Breaking change]**

.. |POTENT_BREAK_CH| replace:: **[Potentially breaking change]**

.. |UNRELEASED| replace:: **[Not yet released]**


Glossary
======================
.. glossary::

    |BREAK_CH|
        Means that the change will break functionality from previous version.

    |POTENT_BREAK_CH|
        The change could break functionality from previous versions but only if it
        was used in a certain way.

    |UNRELEASED|
      These changes have not been yet released.

---------------------
Releases
---------------------

v1.5.0
=====================
- Added an asterisk (*) to mandatory parameters.

v1.4.10
=====================
- Fixed string casting sometimes being cast to a list type.


v1.4.8 / v1.4.9
=====================
- Fixed :class:`tkclasswiz.convert.convert_objects_to_script` function:
  
  - not being able to convert global enums (or enum flags).
  - duplicated import strings.

- Fixed flags not definable as flags when editing list-like objects.
- Fixed tooltip style not adjusting when using ttkbootstrap.
  E. g., in dark mode only the text was updated, but background was still the same. 
- Fixed the Python3.10+ Union type (``A | B``) not being detected as an union type.
- Fixed UnionType import error.


v1.4.7
===================
- Fixed incorrect item being removed (at incorrect index) when editing an object.
- Fixed :class:`tkclasswiz.storage.ListBoxObjects` still selecting the old value when a new value
  was inserted. Now only the added value is selected.


v1.4.6
================
- Fixed some parameter name lengths not being accommodated for.


v1.4.5
================
- Further generic type fixes
- Fixed type deprecations to also consider subclasses


v1.4.4
================
- Fixed generic types under iterable types expansion.


v1.4.3
================
- Fixed an error when a subclass's generic accepts less types than the original.


v1.4.2
================
- Fixed issue with typing conversion.


v1.4.1
================
- Fixed scaling (padding) issues


v1.4.0
================
- Definition of enums and literal values inside iterable types.
- Ability to register deprecated parameters.
- Ability to define :class:`enum.Flag` like flags.


v1.3.1
================
- Fixed :func:`tkclasswiz.convert.convert_objects_to_script` not including enum imports.


v1.3.0
================
- The types will now have their subscripted type displayed alongside them.
- Custom repr display of structured objects via
  :py:meth:`tkclasswiz.convert.ObjectInfo.register_repr` method.

v1.2.3
================
- Fixed annotations not getting obtained for function definitions.


v1.2.2
================
- Fixed incorrect ``Union`` processing if it was used in a ``List`` annotation.


v1.2.1
================
- Replaced raw usage of ``.__annotations__`` with :func:`typing.get_typehints`.


v1.2.0
================
- Added the ability of nicknaming structured objects.
- Generic types support (Parametric types)
- :ref:`Type aliasing`
- Object nicknaming
- Tooltip when hovering over fields, which shows the full value.
- |BREAK_CH| Minimal Python version bumped to Python 3.9


v1.1.1
================
- Fixed template export on view-only mode, where the template exported wrong type.
- Fixed abstract classes, defined with ``__metaclass__ = ABCMeta``, not being treated as abstract.  


v1.1.0
================
- :ref:`Abstract classes` (those that directly inherit :class:`abc.ABC`) are no longer
  definable through TkClassWizard.
- :ref:`Polymorphism` support


v1.0.1
=================
- Fixed a bug where the window didn't close and couldn't be closed
  if an exception was raised when trying to define a class without annotations, and there
  were no previously opened frames.


v1.0.0
=================
- Initial release
