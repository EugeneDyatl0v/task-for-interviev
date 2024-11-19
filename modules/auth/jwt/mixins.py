from modules.auth.jwt.dataclasses import EditableField


class EditableMixin:
    """Mixin for classes related to mutable fields."""

    editable = True

    def get_editable_fields(self, session_model) -> EditableField:
        pass


class ConstMixin:
    """Mixin for classes related to immutable fields"""

    editable = False
