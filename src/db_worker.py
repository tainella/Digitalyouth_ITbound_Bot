from datetime import datetime
import logging
import random

from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from sqlalchemy import exc

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%y-%m-%d %H:%M:%S')
db = declarative_base()
engine = create_engine('sqlite:///data/database.db', echo=False)
metadata = MetaData()
Session = sessionmaker(bind=engine)
Session = Session()

# Блок создания БД

class SpheresToTasks(db):
	__tablename__ = 'spheres_to_tasks'
	
	id = Column(Integer, primary_key=True)
	sphere_name = Column(String, ForeignKey('sphere.name'), nullable=True)
	task_id = Column(Integer, ForeignKey('task.id'), nullable=True)
	task = relationship("Task", back_populates = "spheres")
	spheres = relationship("Sphere", backref = backref("spheres_tasks"))	

	def __init__(self, task=None, sphere=None):
		self.sphere = sphere
		self.task = task

class SpheresToSpecialists(db):
	__tablename__ = 'spheres_to_specialists'
	
	id = Column(Integer, primary_key=True)
	sphere_name = Column(String, ForeignKey('sphere.name'), nullable=True)
	specialist_id = Column(Integer, ForeignKey('specialist.id'), nullable=True)
	spheres = relationship("Sphere", backref = backref("spheres_specialists"))	
	specialist = relationship("Specialist", back_populates = "spheres")	

	def __init__(self, specialist=None, spheres=None):
			self.spheres = spheres
			self.specialist = specialist

class Sphere(db):
	__tablename__ = 'sphere'
	name = Column(String, primary_key=True)
	# tasks = relationship("SpheresToTasks", back_populates="sphere")
	# specialists = relationship("SpheresToSpecialists", back_populates="sphere")
	specialists = association_proxy("spheres_specialists", "specialists")
	tasks = association_proxy("spheres_tasks", "task")
	def __init__(self, name):
		self.name = name
		self.tasks = []
		self.specialists = []

class Task(db):
	__tablename__ = 'task'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	spheres = relationship("SpheresToTasks", back_populates="task")
	status = Column(String) #check, open, in_work, closed
	representative_id = Column(Integer, ForeignKey('representative.id'))	
	representative = relationship("Representative", back_populates="tasks")
	specialist_id = Column(Integer, ForeignKey('specialist.id'))	
	specialist = relationship("Specialist", back_populates="tasks")
	time_of_creation = Column(DateTime)
	
	def __init__(self, name, description, representative):
		self.name = name
		self.description = description
		self.representative = representative
		
		self.spheres = []
		self.status = 'check'
		self.time_of_creation = datetime.now() # TODO поставить временную зону UTC+3

	def __str__(self):
		return "Название: {},\t описание: {},\t сферы: {}, статус: {}, время создания: {}, представитель: {}, специалист: {}".format(
			self.name, self.description, self.spheres, self.status, self.time_of_creation, self.representative, self.specialist
		)

class Moderator(db):
	__tablename__ = 'moderator'
	id = Column(Integer, primary_key=True)
	user_id = Column(String, ForeignKey('user.telegram_id'))	
	user = relationship("User", back_populates="moderator")
	is_admin = Column(Boolean)
	
	def __init__(self, user):
		self.is_admin = False
		self.user = user


class Specialist(db):
	__tablename__ = 'specialist'
	id = Column(Integer, primary_key=True)
	user_id = Column(String, ForeignKey('user.telegram_id'))	
	user = relationship("User", back_populates="specialist")
	subsribed = Column(Boolean)
	spheres = relationship("SpheresToSpecialists", back_populates="specialist")
	tasks = relationship('Task', back_populates="specialist")
	
	def __init__(self, user):
		self.subsribed = True
		self.user = user


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

	def __str__(self):
		return f"телеграм ID: {self.telegram_id},\tтелеграм никнейм: {self.telegram_fullname},\tтелеграм юзернейм: {self.username}"

db.metadata.create_all(engine)

# Конец блока создания БД, начало инкапсуляция
# Блок Добавления

def add_user(telegram_id: str, telegram_fullname: str, username: str = None):
	"""
	Добавление нового юзера
	"""
	if get_user(telegram_id):
		raise Exception(f"Ошибка, тегерам id {telegram_id} должен быть уникальным")
	else:
		new_user = User(telegram_id,  telegram_fullname, username)
		Session.add(new_user)
		Session.commit()
		logging.info(f"Юзер: '{new_user}' был успешно добавлен")
		return new_user

# TODO обрабатывать случай, если юзер имеет другую роль
def add_specialist(user):
	if not user.specialist:
		new_spec = Specialist(user)
		Session.add(new_spec)
        
		logging.info(f"Юзер стал специалистом")
		user.status = "specialist"
		Session.commit()
		return new_spec
	else:
		raise Exception("Ошибка, юзер уже является специалистом")


def add_moderator(user):
    if not user.moderator:
        new_moder = Moderator(user)
        Session.add(new_moder)
        logging.info(f"Юзер стал модератором")
        user.status = "moderator"
        Session.commit()
        return new_moder
    else:
        raise Exception("Ошибка, юзер уже является модератором")


def add_representative(user):
    if not user.representative:
        new_representative = Representative(user)
        Session.add(new_representative)
        logging.info(f"Юзер стал представителем")
        user.status = "representative"
        Session.commit()
        return new_representative
    else:
        raise Exception("Ошибка, юзер уже является представителем")


def add_task(name, description, representative, spheres: list = None):
    task = Session.query(Task).filter_by(name=name).first()
    if task == None:
        spheres_db = []
        for sphere in spheres:
            t = Session.query(Sphere).filter_by(name=sphere).first()
            if t is None:
                raise Exception(f'Сфера "{sphere}" не существует')
            else:
                spheres_db.append(t)
        new_task = Task(name, description, representative)
        for sphere in spheres_db:
            assosiation = SpheresToTasks()
            assosiation.spheres = sphere
            Session.add(assosiation)
            Session.commit()
            new_task.spheres.append(assosiation)
        new_task.status = 'open'
        Session.add(new_task)
        Session.commit()
        logging.info("Задание создано")
        task = Session.query(Task).filter_by(name=name).first()
    else:
        logging.warning(f'Задание "{name}" уже добавлено')
    return task


def add_spheres_global(spheres):
	for sphere in spheres:
		already_added = Session.query(Sphere).filter_by(name=sphere).first()
		if already_added is None:
			new_sphere = Sphere(sphere)
			Session.add(new_sphere)
		else:
			logging.warning(f'Сфера "{sphere}" уже добавлена')
	Session.commit()

# # setting
def set_status(telegram_id, st): #st = wish_m, wish_r, m, r, s, blocked
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	if user == None:
		return False #returns Boolean
	else:
		user.status = st
		Session.commit()
		return True

def set_spesialist_spheres(telegram_id, spheres):
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	if user == None:
		raise Exception("Ошибка, юзера {telegram_id} не существует")
	else:
		if user.specialist == None:
			raise Exception("Ошибка, юзер {telegram_id} не является специалистом")
		interests = []
		for r in spheres:
			t = Session.query(Sphere).filter_by(name=r).first()
			if t is None:
				raise Exception(f'Сфера "{sphere}" не существует')
			else:
				interests.append(t)
		spec = user.specialist
		spec.spheres = []
		for sphere in interests:
			assosiation = SpheresToSpecialists()
			assosiation.spheres = sphere
			Session.add(assosiation)
			Session.commit()
			spec.spheres.append(assosiation)
		Session.commit()
		return True

def set_subscribe(telegram_id, mode):
	user = Session.query(Specialist).filter_by(subscribe=mode).first()
	if user == None:
		raise Exception("Ошибка, юзера {telegram_id} не существует")
	else:
		user.mode = mode
		Session.commit()

def set_task_status(task_name, status):
	task = Session.query(Task).filter_by(name=task_name).first()
	if task == None:
		raise Exception("Ошибка, задания {task_name} не существует")
	else:
		task.status = status
		Session.commit()

# getting
def get_user(telegram_id):
	telegram_id = str(telegram_id)
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	return user if user is not None else False

def get_spesialist_spheres(telegram_id):
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	if user == None:
		raise Exception("Ошибка, юзера {telegram_id} не существует")
	else:
		if user.specialist == None:
			raise Exception("Ошибка, юзер {telegram_id} не является специалистом")
		sp_sh = user.specialist.spheres
		y = []
		for i in sp_sh:
			y.append(i.spheres.name)
		return y

def get_all_interests():
    list_ = Session.query(Sphere).all()
    list_ = [sphere.name for sphere in list_]
    return list_
	
# # TODO переделать чтобы работало
def get_opened_taskes(spheres):
	opened_taskes = Session.query(Task).filter_by(status = 'open').filter(or_(name == s for s in spheres)).all()
	return opened_taskes
	
def get_unchecked_taskes():
	unchecked_taskes = Session.query(Task).filter_by(status = 'check').all()
	return unchecked_taskes

def get_for_check_represen_users():
    list = Session.query(User).filter_by(status = 'wish_r').all()
    return list

def get_for_check_moder_users():
    list = Session.query(User).filter_by(status = 'wish_m').all()
    return list

def get_user_status(telegram_id):
    user = Session.query(User).filter_by(telegram_id=telegram_id).first()
    if user == None:
        raise Exception("Ошибка, юзера {telegram_id} не существует")
    else:
        return user.status

def get_current_tasks_for_spec(telegram_id):
    user = Session.query(User).filter_by(telegram_id = telegram_id).first()
    if user == None:
        raise Exception("Ошибка, юзера {telegram_id} не существует")
    if user.specialist == None:
        raise Exception("Ошибка, юзер {telegram_id} не является специалистом")
    tasks = user.specialist.tasks
    curr = []
    for task in tasks:
        if task.status == 'in_work':
            curr.append(task)
    return curr

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
	pass
	user = get_user(418878871)
    #print(user.status)
	# user = add_user(418878871, "@teadove", "Петер")
	add_specialist(user)
	#user = add_user(10, "представитель_kek")
	#add_representative(user)
	# repr_ = get_user(10).representative
	# add_spheres_global(["МЛ", "Разработка ботов", "Дизайн"])
	# task = add_task("Купить мыло", "Сходить в магаз и купить пиво", repr_, ["МЛ", "Дизайн"])
	# task1 = Session.query(Task).filter_by(name="Купить мыло").first()
	# if task1 == None:
	# 	print("nope")
	# else:
	# 	for i in task1.spheres:
	# 		print(i.spheres.name)
	# #user1 = add_user("44", "специалист_kek")
	# #add_specialist(user1)
	# print('-----')
	# user = add_user(44, "kek")
	# add_specialist(user)
	# set_spesialist_spheres("44", ["Дизайн", "Разработка ботов", "МЛ"])
	# list = get_spesialist_spheres("44")
	# for i in list:
	# 	print(i)
	# list = get_unchecked_taskes()
	# for i in list:
	# 	print(i)
	# pass
