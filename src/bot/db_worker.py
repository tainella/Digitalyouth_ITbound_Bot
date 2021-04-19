from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

db = declarative_base()
engine = create_engine('sqlite:///Info.db', echo=True)
metadata = MetaData()

class User(db):
    __tablename__ = 'users'
    telegram_id = Column(String, primary_key=True)
    username = Column(String)
    telegram_fullname = Column(String)
    bot_block = Column(Boolean)
    real_fullname = Column(String)
    phone = Column(String)
    moderator = relationship('moderators', backref='moders', uselist=False)
    specialist = relationship('specialists', backref='special', uselist=False)
    representative = relationship('representatives', backref='represents', uselist=False)

class Moderator(db):
	__tablename__ = 'moderators'
	telegram_id = Column(String, primary_key=True)
	is_admin = Column(Boolean)

class Specialist(db):
	__tablename__ = 'specialists'
	telegram_id = Column(String, primary_key=True)
	interests = relationship('interests', backref='areas')
	current_tasks = relationship('tasks', backref='current_tasks')

class Representative(db):
	__tablename__ = 'representatives'
	telegram_id = Column(String, primary_key=True)
	tasks = relationship('tasks', backref='published_tasks')

class Task(db):
	__tablename__ = 'tasks'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	spheres = relationship('interests', backref='spheres')
	status = Column(String)
	represen_id = Column(String)
	specialist_id = Column(String)

class Interest(db):
	__tablename__ = 'interests'
	name = Column(String, primary_key=True)

db.metadata.create_all(engine)
