"""
A JWT class fields for the dynamically filling the JWT payload.
"""
from abc import ABC, abstractmethod
from typing import Any

from database import Session

from modules.auth.jwt.dataclasses import EditableField
from modules.auth.jwt.mixins import ConstMixin, EditableMixin

from sqlalchemy import select
from sqlalchemy.orm import selectinload


class JWTAbstractField(ABC):
    """Abstract base class for JWT fields."""

    @property
    @abstractmethod
    def value(self, *args, **kwargs):
        """General getter of the field value."""


class JWTArgsField(JWTAbstractField):
    """
    Parent class for a JWT field created from a specific object.

    Attributes:
        field (str): name of the required object field.
    """

    def __init__(self, session_field_name, field):
        self.session_field_name = session_field_name
        self.field = field
        self._value = None

    @property
    def value(self) -> Any:
        """
        Returns the value of the field of the passed object
        (the value of the corresponding field for JWT).
        """
        return self._value

    async def set_value(self, obj: Any) -> None:
        """General getter of the field value."""
        self._value = getattr(obj, self.field)


class JWTArgsConstField(ConstMixin, JWTArgsField):
    """
    Immutable JWT field created from a specific object.
    """


class JWTArgsEditableField(EditableMixin, JWTArgsField):
    """
    Mutable JWT field created from a specific object.
    """

    def get_editable_fields(self, session_model) -> EditableField:
        return EditableField(
            model=session_model,
            field_out=self.field,
            session_field_name=self.session_field_name,
            field_in=None
        )


class JWTModelField(JWTAbstractField):
    """
    Parent class for a JWT field created from a model.

    Attributes:
        model (db.Model): current model;
        session_field_name (str): name of the Session field
            related to the model;
        field_in (str): the name of the field by which we are
            looking for a specific model record;
        field_out (str): the name of the field that we need
            in this entry for the JWT field;
        multiple (bool): flag to determine a field with many objects;
        user_property(bool): flag to determine is the field
                             a property of User;
    """

    def __init__(
        self,
        model,
        session_field_name,
        field_in,
        field_out,
        multiple=False,
        user_property=False,
        relation_field=None
    ):
        self.model = model
        self.session_field_name = session_field_name
        self.field_in = field_in
        self.field_out = field_out
        self._value = None
        self.multiple = multiple
        self.user_property = user_property
        self.relation_field = relation_field

    @property
    def value(self) -> Any:
        """
        Returns the value of the field of the passed object
        (the value of the corresponding field for JWT).
        """
        return self._value

    async def set_value(self, session_obj) -> None:
        """
        Setter of the field value.
        Field value obtains from the specified field of the model object
        associated with a specific session.

        Args:
            session_obj(Session): object of specific auth session.
        """
        session_related_obj_id = await self.get_value(
            session_obj, self.session_field_name
        )

        field_in_value = await self.get_value(self.model, self.field_in)

        async with Session() as session:
            res = await session.execute(
                select(self.model).filter(
                    field_in_value == session_related_obj_id
                )
            )
            model_object = res

        if self.multiple:
            self._value = [
                await self.get_value(i, self.field_out)
                for i in model_object.all()
            ]
        else:
            model_first = model_object.scalars().first()
            if model_first:
                if self.user_property:
                    async with Session() as session:
                        relationship_model = await self.get_value(
                            self.model, self.field_out)

                        result = await session.execute(
                            select(self.model)
                            .filter(
                                self.model.id == model_first.id
                            )
                            .options(
                                selectinload(relationship_model))
                        )

                        user = result.scalars().first()
                        rel_object = await self.get_value(
                            user, self.field_out
                        )
                        self._value = await self.get_value(
                            rel_object, self.relation_field
                        )
                else:
                    self._value = await self.get_value(
                        model_first, self.field_out)

    @staticmethod
    async def get_value(obj, field) -> Any:
        """Get the value from the specified field."""
        return getattr(obj, field)


class JWTModelConstField(ConstMixin, JWTModelField):
    """Immutable JWT field created from a model."""


class JWTModelEditableField(EditableMixin, JWTModelField):
    """Mutable JWT field created from a model."""

    def get_editable_fields(self, session_model) -> EditableField:
        return EditableField(
            model=self.model,
            field_out=self.field_out,
            session_field_name=self.session_field_name,
            field_in=self.field_in
        )


class JWTFuncField(JWTAbstractField):
    """Parent class for a JWT field obtained as a result of the function.

    Attributes:
        func (function): function to get the field value.
    """

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @property
    def value(self) -> Any:
        """Returns the value of the function."""
        return self.func(*self.args, **self.kwargs)


class JWTFuncConstField(ConstMixin, JWTFuncField):
    """Immutable JWT field obtained as a result of the function."""


class JWTFuncEditableField(EditableMixin, JWTFuncField):
    """Mutable JWT field obtained as a result of the function."""
