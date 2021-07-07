from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from .base_model import BaseModelMixin


class User(BaseModelMixin):
    __tablename__ = 'user'

    telegram_id = Column(String, nullable=False, index=True, unique=True)
    # TODO сделать индексирумым как тот чел из плюма говорил
    username = Column(String)
    telegram_fullname = Column(String)
    real_fullname = Column(String)
    # TODO получать номер телефона из контакта
    #  Может ещё регулярки сделать?
    phone_n = Column(String)
    # TODO добавить enum
    status = Column(String)  # wish_moder, wish_rerpre, moderator, representative, specialist, blocked

    moderator = relationship('Moderator', back_populates="user", uselist=False, cascade='all, delete')
    specialist = relationship('Specialist', back_populates="user", uselist=False, cascade='all, delete')
    # TODO перепроверить, что all, delete удаляет только детей
    representative = relationship('Representative', back_populates="user", uselist=False, cascade='all, delete')

    def __init__(self, telegram_id: int, username: str = None, telegram_fullname: str = None, real_fullname: str = None,
                 phone_n: str = None, status: str = None):
        self.telegram_id = telegram_id
        self.username = username
        self.telegram_fullname = telegram_fullname
        self.real_fullname = real_fullname
        self.phone_n = phone_n
        self.status = status
        self._log()

    @classmethod
    def get(cls, session, id_: int = None, telegram_id: int = None):
        if id_ is None and telegram_id is None:
            raise Exception("No id specified")
        if id_ is not None:
            return session.query(cls).get(id_)
        if telegram_id is not None:
            return session.query(cls).filter_by(telegram_id=telegram_id).first()


class Sphere(BaseModelMixin):
    __tablename__ = 'sphere'
    name = Column(String, index=True, unique=True)
    is_available = Column(Boolean)  # false недоступно, true доступно

    specialists = relationship("SphereToSpecialist", back_populates='sphere')
    tasks = relationship("SphereToTask", back_populates="sphere")

    def __init__(self, name: str, is_available: bool = True):
        self.name = name
        self.is_available = is_available
        self._log()


class Specialist(BaseModelMixin):
    __tablename__ = 'specialist'

    user_id = Column(String, ForeignKey('user.id_'), nullable=False)
    subscribed = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="specialist", uselist=False)
    tasks = relationship('Task', back_populates="specialist")
    spheres = relationship("SphereToSpecialist", back_populates="specialist")

    def __init__(self, user: User, subscribed: bool = True):
        self.user = user
        self.subscribed = True
        self._log()


class Representative(BaseModelMixin):
    __tablename__ = 'representative'

    official_name = Column(String)
    user_id = Column(String, ForeignKey('user.id_'), nullable=False)

    user = relationship("User", back_populates="representative", uselist=False)
    tasks = relationship('Task', back_populates="representative")

    def __init__(self, user: User, official_name: str = None):
        self.user = user
        self.official_name = official_name
        self._log()


class Moderator(BaseModelMixin):
    __tablename__ = 'moderator'

    user_id = Column(String, ForeignKey('user.id_'))
    is_admin = Column(Boolean)

    user = relationship("User", back_populates="moderator", uselist=False)

    def __init__(self, user: User, is_admin: bool = False):
        self.user = user
        self.is_admin = is_admin
        self._log()


class Task(BaseModelMixin):
    __tablename__ = 'task'

    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(String)
    # 'awaiting_confirmation', 'awaiting_specialist', 'in_work',
    # 'closed_with_success', 'canceled_by_represented', 'closed_by_other_reason'
    time_of_creation = Column(DateTime(timezone=True), nullable=False)
    representative_id = Column(Integer, ForeignKey('representative.id_'), nullable=False)
    specialist_id = Column(Integer, ForeignKey('specialist.id_'))

    spheres = relationship("SphereToTask", back_populates="task")
    representative = relationship("Representative", back_populates="tasks", uselist=False)
    specialist = relationship("Specialist", back_populates="tasks", uselist=False)

    def __init__(self, name: str, representative: Representative
                 , description: str = None, status: str = None, specialist=None):
        self.name = name
        self.representative = representative
        self.description = description

        self.status = status or 'awaiting_confirmation'
        self.specialist = specialist
        self.time_of_creation = datetime.now()  # TODO поставить временную зону UTC+3
        self._log()


class SphereToTask(BaseModelMixin):
    __tablename__ = 'sphere_to_task'

    sphere_id = Column(Integer, ForeignKey('sphere.id_'), nullable=False)
    sphere = relationship("Sphere", back_populates="tasks")

    task_id = Column(Integer, ForeignKey('task.id_'), nullable=True)
    task = relationship("Task", back_populates="spheres")

    UniqueConstraint(sphere_id, task_id)

    def __init__(self, sphere: Sphere, task: Task):
        self.task = task
        self.sphere = sphere

        self._log()


class SphereToSpecialist(BaseModelMixin):
    __tablename__ = 'spheres_to_specialists'

    sphere_id = Column(Integer, ForeignKey('sphere.id_'), nullable=False)
    sphere = relationship("Sphere", back_populates="specialists")

    specialist_id = Column(Integer, ForeignKey('specialist.id_'), nullable=True)
    specialist = relationship("Specialist", back_populates="spheres")

    UniqueConstraint(sphere_id, specialist_id)

    def __init__(self, sphere: Sphere, specialist: Specialist):
        self.sphere = sphere
        self.specialist = specialist

        self._log()
