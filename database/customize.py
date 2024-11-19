import datetime
from typing import Any, List, Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query


class BaseFilterQuery(Query):
    def __init__(
            self,
            entities,
            session: Optional[AsyncSession] = None,
            **kwargs
    ):
        super().__init__(entities, session=session)
        self._add_soft_delete_filter()

    def _add_soft_delete_filter(self) -> None:
        """
        Adds a soft delete filter to the query for entities
        containing the SoftDeleteMixin.
        """
        for entity in self.column_descriptions:
            get_criteria = getattr(entity['entity'], 'get_criteria', None)
            if callable(get_criteria):
                criteria = get_criteria(entity['entity'])
                self._where_criteria += (criteria,)

    async def delete(self, synchronize_session='evaluate') -> None:
        """
        Performs a soft delete for all entities matching the query.

        If the entity contains a method `get_criteria`,
        it is considered as implementing the SoftDeleteMixin.
        """
        result = await self.session.execute(self.statement)
        instances = result.scalars().all()
        for instance in instances:
            if callable(getattr(instance, 'get_criteria', None)):
                instance.deleted_at = datetime.datetime.utcnow()
                table = instance.__class__.__table__
                unique_constraints = [c for c in table.constraints
                                      if isinstance(c, UniqueConstraint)]
                for constraint in unique_constraints:
                    columns = constraint.columns
                    for column in columns:
                        column_name = column.name
                        if column_name not in ['id', 'deleted_at']:
                            value = getattr(
                                instance,
                                column_name
                            )
                            if value:
                                setattr(
                                    instance,
                                    column_name,
                                    f"deleted_{value}"
                                )
                self.session.add(instance)
            else:
                await self.session.delete(instance)
        await self.session.commit()

    def all(self) -> List[Any]:
        result = self.session.execute(self.statement)
        return list(result.scalars().all())

    def first(self) -> Optional[Any]:
        result = self.session.execute(self.statement)
        return result.scalars().first()

    def get(self, id: Any) -> Optional[Any]:
        """Filters result by id property"""
        result = self.session.execute(self.filter_by(id=id))
        return result.scalars().first()

    def filter(self, *args):
        return super().filter(*args)

    def filter_by(self, **kwargs):
        return super().filter_by(**kwargs)

    def order_by(self, *args):
        return super().order_by(*args)

    def limit(self, limit: int):
        return super().limit(limit)

    def offset(self, offset: int):
        return super().offset(offset)

    def select_related(self, *args):
        """Adds related models to load with the query."""
        return super().options(*args)


class CustomAsyncSession(AsyncSession):
    def query(self, *entities, **kwargs):
        """
        A custom session class that extends the `AsyncSession`
        and provides a `query` method with additional functionality
        for "soft delete" operations.

        Args:
            *entities:
                Positional arguments representing the entities
                (models) to be included in the query.
            **kwargs:
                Keyword arguments to be passed to the constructor
                of the `BaseFilterQuery` class.

        Returns:
            BaseFilterQuery: A specialized query object that can handle
                "soft delete" functionality.
        """
        return BaseFilterQuery(entities, session=self, **kwargs)
