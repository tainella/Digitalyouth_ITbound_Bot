from datetime import datetime
from typing import Union, Tuple

from loguru import logger
import sqlalchemy.orm.exc
from sqlalchemy import Column, Integer, DateTime

from .base import Base


# FIXME Добавить общение юзеров с ЛА
class BaseModelMixin(Base):
    __abstract__ = True

    id_ = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # TODO написать мета init

    @classmethod
    def get(cls, session, id_: Union[int, Tuple[int, ...]]):
        if isinstance(id_, int):
            return session.query(cls).get(id_)
        else:
            return [session.query(cls).get(i) for i in id_]

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id_ == other.id_

    def __hash__(self):
        return hash((self.__class__, self.id_))

    def __str__(self):
        """
        Выдаёт поля обьекта и их значения, публичные и не вызываемые.
        """
        fields_dict = {field: getattr(self, field) for field in dir(self) if not field.startswith('_')
                       and not callable(getattr(self, field)) and field not in ["query", "registry", 'metadata']}
        return self.__class__.__name__ + ": " + str(fields_dict)

    def _log(self):
        logger.info('instance "{}" of "{}" created'.format(self, self.__class__.__name__))

