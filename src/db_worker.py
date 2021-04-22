from datetime import datetime
import logging

from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_

logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%y-%m-%d %H:%M:%S')

db = declarative_base()
engine = create_engine('sqlite:///data/database.db', echo=True)
metadata = MetaData()
Session = sessionmaker(bind=engine)
Session = Session()

spheres_to_tasks_table = Table('spheres_to_tasks', db.metadata,
    Column('sphere_name', String, ForeignKey('sphere.name')),
    Column('task_id', Integer, ForeignKey('task.id'))
)

spheres_to_specialists_table = Table('spheres_to_specialists', db.metadata,
    Column('sphere_name', String, ForeignKey('sphere.name')),
    Column('specialist_id', Integer, ForeignKey('specialist.id'))
)

class Sphere(db):
	__tablename__ = 'sphere'
	name = Column(String, primary_key=True)
	tasks = relationship("Task", secondary=spheres_to_tasks_table, back_populates="spheres")
	specialists = relationship("Specialist", secondary=spheres_to_specialists_table, back_populates="spheres")
	def __init__(self, name):
		self.name = name

class Task(db):
	__tablename__ = 'task'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	spheres = relationship("Sphere", secondary=spheres_to_tasks_table, back_populates="tasks")
	status = Column(String) #check, open, worked, closed
	representative_id = Column(String, ForeignKey('representative.id'))	
	representative = relationship("Representative", back_populates="tasks")
	specialist_id = Column(String, ForeignKey('specialist.id'))	
	specialist = relationship("Specialist", back_populates="tasks")
	time_of_creation = Column(DateTime)
	
	def __init__(self, name, description, representative, spheres = None):
		self.name = name
		self.description = description
		self.spheres = spheres
		self.representative = representative
		
		self.status = 'check'
		self.time_of_creation = datetime.now() # TODO поставить временную зону UTC+3

class Moderator(db):
	__tablename__ = 'moderator'
	id = Column(Integer, primary_key=True)
	user_id = Column(String, ForeignKey('user.telegram_id'))	
	user = relationship("User", back_populates="moderator")
	is_admin = Column(Boolean)
	
	def __init__(self):
		self.is_admin = False

class Specialist(db):
	__tablename__ = 'specialist'
	id = Column(Integer, primary_key=True)
	user_id = Column(String, ForeignKey('user.telegram_id'))	
	user = relationship("User", back_populates="specialist")
	subsribed = Column(Boolean)
	spheres = relationship("Sphere", secondary=spheres_to_specialists_table, back_populates="specialists")
	tasks = relationship('Task', back_populates="specialist")
	
	def __init__(self):
		self.subsribed = True

class Representative(db):
	__tablename__ = 'representative'
	id = Column(Integer, primary_key=True)
	user_id = Column(String, ForeignKey('user.telegram_id'))	
	user = relationship("User", back_populates="representative")
	tasks = relationship('Task', back_populates="representative")
	
	def __init__(self, user):
		self.user = user

class User(db):
    __tablename__ = 'user'
    telegram_id = Column(String, primary_key=True)
    username = Column(String, nullable=True)
    telegram_fullname = Column(String)
    real_fullname = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, nullable=True) #wish_moder, wish_rerpre, moderator, representative, specialist, blocked
    moderator = relationship('Moderator', back_populates="user", uselist=False)
    specialist = relationship('Specialist', back_populates="user", uselist=False)
    representative = relationship('Representative', back_populates="user", uselist=False)
    
    def __init__(self, telegram_id, telegram_fullname, username=None):
        self.telegram_id = telegram_id
        self.username = username
        self.telegram_fullname = telegram_fullname

db.metadata.create_all(engine)

# # adding
# def add_user(telegram_id, username, telegram_fullname, real_fullname, phone, status):
# 	if status == 's':
# 		print('BEFORE User')
# 		add_spec(telegram_id)
# 		spec = Session.query(Specialist).filter_by(telegram_id=telegram_id).first()
# 		new_user = User(telegram_id, username, telegram_fullname, real_fullname, phone, status, spec)
# 		print('AFTER User')
# 	elif status == 'wish_m':
# 		new_user = User(telegram_id, username, telegram_fullname, real_fullname, phone, status)
# 	elif status == 'wish_r':
# 		new_user = User(telegram_id, username, telegram_fullname, real_fullname, phone, status)
# 	Session.add(new_user)
# 	Session.commit()

# def add_spec(telegram_id):
# 	print('BEFORE Spec')
# 	new_spec = Specialist(telegram_id)
# 	print('BEFORE Spec')
# 	Session.add(new_spec)
# 	Session.commit()

# def add_task(name, description, spheres, represen_id):
# 	new_task = Task(name, description, spheres, represen_id)
# 	Session.add(new_task)
# 	Session.commit()

# def add_spheres(spheres):
# 	for r in spheres:
# 		t = Session.query(Sphere).filter_by(name=r).first()
# 		if t == None:
# 			print('BEFORE Interest')
# 			new = Sphere(r)
# 			print('AFTER Interest')
# 			Session.add(new)
# 			Session.commit()

# # setting
# def set_status(telegram_id, st): #st = wish_m, wish_r, m, r, s, blocked
# 	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
# 	if user == None:
# 		return False #returns Boolean
# 	else: 
# 		user.status = st
# 		Session.commit()
# 		return True

# def change_spheres(telegram_id, spheres):
# 	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
# 	if user == None:
# 		return False #returns Boolean
# 	else: 
# 		user.interests = []
# 		for r in spheres:
# 			sphere = Sphere(name = r)
# 			user.interests.append(sphere)
# 		Session.commit()
# 		return True

# def change_subscribe(telegram_id, mode):
# 	user = Session.query(Specialist).filter_by(subscribe=mode).first()

# # getting
# def get_user(telegram_id):
# 	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
# 	return user

# def get_sphere(telegram_id):
# 	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
# 	return user.spheres

# def get_all_interests():
# 	list = Session.query(Sphere).all()
# 	return list
	
# # TODO переделать чтобы работало
# # def get_opened_taskes(spheres):
# # 	opened_taskes = Session.query(Task).filter_by(status = 'open').filter(or_(name == s for s in spheres)).all()
# # 	return opened_taskes
	
# def get_unchecked_taskes():
# 	unchecked_taskes = Session.query(Task).filter_by(status = 'check').all()
# 	return unchecked_taskes

# def get_for_check_represen_users():
# 	list = Session.query(User).filter_by(status = 'wish_r').all()
# 	return list

# def get_for_check_moder_users():
# 	list = Session.query(User).filter_by(status = 'wish_m').all()
# 	return list

# def get_status(telegram_id):
# 	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
# 	if user == None:
# 		return None
# 	else:
# 		return user.status

# def get_current_tasks_for_spec(telegram_id):
# 	list = Session.query(Task).filter_by(specialist_id = telegram_id).filter_by(status = 'worked').all()
# 	return list

# def get_current_tasks_for_represen(telegram_id):
# 	list = Session.query(Task).filter_by(represen_id = telegram_id).filter_by(status = 'worked').all()
# 	return list

# def get_history_tasks_for_spec(telegram_id):
# 	list = Session.query(Task).filter_by(specialist_id = telegram_id).filter_by(status = 'closed').all()
# 	return list

# def get_history_tasks_for_represen(telegram_id):
# 	list = Session.query(Task).filter_by(represen_id = telegram_id).filter_by(status = 'closed').all()

# 	return list
	
	

if __name__ == '__main__':
	print("\n\n\n")	
	
	# new_user = User("0", "TeaDove")
	# Session.add(new_user)
	# new_repr = Representative(new_user)
	# Session.add(new_repr)
	# Session.commit()

	spheres = Session.query(Sphere).all()
	print(spheres)
	repr_ = Session.query(User).filter_by(telegram_id="0").all()[0].representative
	new_task = Task("Купить пиво", "Послать Амелию за пивом", repr_, spheres)
	Session.add(new_task)
	print(new_task.spheres)
	# Session.add(spheres[0])
	# Session.add(spheres[1])
	# Session.add(spheres[2])
	# Session.commit()



	# print(Session.query(User).filter_by(telegram_id="0").all()[0])
	
	# new_task = Task("Купить пиво", "Послать Амелию за пивом", repr_)
	# Session.add(new_task)
	# Session.commit()
	# print(repr_.tasks[0].__dict__)
	# print()
	# add_spheres(['ML','Web'])
	# add_user('6567987', 'tea', 'Hoop Hoop', 'Ho Ho Ho', '45698460469', 's')
	# change_spheres('6567987', ['ML'])
	# print(get_sphere('6567987'))

	
	pass