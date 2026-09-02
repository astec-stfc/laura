"""
Cascading attribute access for nested Pydantic models.

This mixin enables transparent access to nested model attributes:
    quad.k1l  # instead of quad.magnetic.field_integral.k1l
    elem.maxI  # instead of elem.electrical.maxI

This is a convenience layer that searches nested models for matching attribute names.
"""

from typing import Type, List, Tuple, Union, Any, get_args, get_origin
from pydantic import BaseModel
import types


class CascadingAccessMixin:
    """
    Mixin that adds transparent cascading attribute access to nested Pydantic models.

    When an attribute is not found directly on the model, this searches recursively
    through nested models to find a matching attribute name.

    Usage:
        class Element(CascadingAccessMixin, BaseModel):
            ...

        # Then access nested attributes directly:
        element.k1l  # searches: element.magnetic.field_integral.k1l
    """

    def _resolve_attribute_path(self, attr_name: str) -> List[Tuple[str, ...]]:
        """
        Resolve attribute name to its full path in nested models.

        Returns:
            List of tuples representing paths to the attribute.
            E.g., [('magnetic', 'field_integral', 'k1l')]

        Raises:
            AttributeError if attribute not found or is ambiguous.
        """
        return self._find_field_paths(attr_name, self.__class__)

    @classmethod
    def _find_field_paths(
        cls: Type["CascadingAccessMixin"],
        attr_name: str,
        current_model: Type[BaseModel],
        current_path: Tuple[str, ...] = (),
    ) -> List[Tuple[str, ...]]:
        """
        Recursively search for attribute in model structure.

        Searches:
        1. Direct fields matching attr_name
        2. Nested Pydantic models (Union types unwrapped)
        3. Properties on the class

        Args:
            attr_name: Attribute name to find
            current_model: Model class to search
            current_path: Current traversal path (for recursion)

        Returns:
            List of all paths where attr_name was found
        """
        paths = []

        # Search direct fields
        if hasattr(current_model, "model_fields"):
            for field_name, field_info in current_model.model_fields.items():
                new_path = current_path + (field_name,)

                # Direct field match
                if field_name == attr_name:
                    paths.append(new_path)

                # Recurse into nested models
                field_annotation = field_info.annotation
                origin = get_origin(field_annotation)

                # Handle Union/Optional types
                is_union = origin is Union or isinstance(
                    field_annotation, types.UnionType
                )
                if is_union:
                    args = get_args(field_annotation)
                    for arg in args:
                        if arg is not type(None):
                            try:
                                if isinstance(arg, type) and issubclass(arg, BaseModel):
                                    paths.extend(
                                        cls._find_field_paths(attr_name, arg, new_path)
                                    )
                            except TypeError:
                                pass
                else:
                    try:
                        if isinstance(field_annotation, type) and issubclass(
                            field_annotation, BaseModel
                        ):
                            paths.extend(
                                cls._find_field_paths(
                                    attr_name, field_annotation, new_path
                                )
                            )
                    except TypeError:
                        pass

        # Search class-level properties
        for name, attr in vars(current_model).items():
            if isinstance(attr, property) and name == attr_name:
                paths.append(current_path + (name,))

        return paths

    def _get_nested_attribute(self, path: Tuple[str, ...]) -> Any:
        """Access nested attribute by path."""
        value = self
        for step in path:
            if value is None:
                raise AttributeError(
                    f"Cannot access '{step}' on None value at path '{'.'.join(path)}'"
                )
            value = getattr(value, step)
        return value

    def _set_nested_attribute(self, path: Tuple[str, ...], value: Any) -> None:
        """Set nested attribute by path."""
        target_model = self

        # Traverse to parent of target
        for step in path[:-1]:
            target_model = getattr(target_model, step)
            if target_model is None:
                raise AttributeError(
                    f"Cannot set attribute at path '{'.'.join(path)}': "
                    f"intermediate value is None"
                )

        setattr(target_model, path[-1], value)

    def __getattr__(self, name: str) -> Any:
        """
        Transparent cascading attribute access.

        Looks for attribute in nested models if not found directly.

        Raises:
            AttributeError if attribute not found, is ambiguous, or name is private
        """
        # Avoid recursion on private/internal attributes
        if name.startswith("_"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

        paths = self._resolve_attribute_path(name)

        if not paths:
            raise AttributeError(
                f"'{self.__class__.__name__}' object and its nested models "
                f"have no attribute '{name}'"
            )

        if len(paths) > 1:
            path_strings = [f"'{'.'.join(p)}'" for p in paths]
            raise AttributeError(
                f"Attribute '{name}' is ambiguous. Found at: {', '.join(path_strings)}. "
                f"Access explicitly (e.g., `element.magnetic.k1l`)."
            )

        return self._get_nested_attribute(paths[0])

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Transparent cascading attribute setting.

        If attribute is not a direct field, searches nested models.

        Raises:
            AttributeError if attribute not found, is ambiguous, or name is private
        """
        cls = self.__class__

        # Let Pydantic handle direct fields and internal attributes
        if name in cls.model_fields or name.startswith("_"):
            super().__setattr__(name, value)
            return

        # Try cascading lookup
        try:
            paths = self._resolve_attribute_path(name)
        except Exception:
            super().__setattr__(name, value)
            return

        if not paths:
            super().__setattr__(name, value)
            return

        if len(paths) > 1:
            path_strings = [f"'{'.'.join(p)}'" for p in paths]
            raise AttributeError(
                f"Attribute '{name}' is ambiguous. Found at: {', '.join(path_strings)}. "
                f"Access explicitly (e.g., `element.magnetic.k1l`)."
            )

        self._set_nested_attribute(paths[0], value)
