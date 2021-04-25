# -*- coding: utf-8 -*-

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
	specialists = association_proxy("spheres_specialists", "specialists")
	tasks = association_proxy("spheres_tasks", "task")
	status = Column(Boolean) #false недоступно, true доступно
	def __init__(self, name):
		self.name = name
		self.tasks = []
		self.specialists = []
		self.status = True


class Task(db):
	__tablename__ = 'task'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	spheres = relationship("SpheresToTasks", back_populates="task")
	status = Column(String) #['awaiting_confirmation', 'awaiting_specialist', 'in_work', 'closed_with_success', 'canceled_by_represented', 'closed_by_other_reason']
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
		self.status = 'awaiting_confirmation'
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

# Конец блока создания БД, начало инкапсуляции
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

def add_specialist(user):
	if not user.specialist:
		new_spec = Specialist(user)
		Session.add(new_spec)
		logging.info(f"Юзер стал специалистом")
		if user.status is not None:
			if user.status == "moderator":
				user.moderator = None
			elif user.status == "representative":
				user.representative = None
				#сбросить все текущие задачи
				drop_current_tasks(user)
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
		if user.status == "specialist" or user.status == "representative":
			drop_current_tasks(user) #сбросить все текущие задачи
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
		if user.status == "specialist":
			drop_current_tasks(user) #сбросить все текущие задачи
		user.status = "representative"
		Session.commit()
		return new_representative
	else:
		raise Exception("Ошибка, юзер уже является представителем")


def add_task(name, description, representative, spheres: list = None):
    spheres_db = []
    for sphere in spheres:
        t = Session.query(Sphere).filter_by(name=sphere).first()
        if t is None:
            raise Exception(f'Сфера "{sphere}" не существует')
        else:
            if t.status == False:
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
    new_task.status = 'awaiting_confirmation'
    Session.add(new_task)
    Session.commit()
    logging.info("Задание создано")
    return new_task


def add_spheres_global(spheres):
	for sphere in spheres:
		already_added = Session.query(Sphere).filter_by(name=sphere).first()
		if already_added is None:
			new_sphere = Sphere(sphere)
			Session.add(new_sphere)
		else:
			if already_added.status == True:
				logging.warning(f'Сфера "{sphere}" уже добавлена')
			else:
				already_added.status = True
	Session.commit()
# # setting

def delete_spheres_global(spheres): #выведи предупреждение представителю что все задачи будут сняты
	for sphere in spheres:
		already_added = Session.query(Sphere).filter_by(name=sphere).first()
		if already_added is None:
			raise Exception(f'Сфера "{sphere}" не существует')
		else:
			already_added.status = False
	Session.commit()
	#закрыть все задачи под этими сферами
	all_tasks = Session.query(Task).filter(Task.status not in  ['closed_with_success', 'canceled_by_represented', 'closed_by_other_reason']).all()
	for task in all_tasks:
		common = [d for d in spheres if d in task.spheres]
		if common != None:
            # TODO
			#if task.status == 'inwork':
				#ОТПРАВИТЬ ОПОВЕЩЕНИЕ ЧТО ЗАДАЧА СНЯТА
			task.status = "closed_by_other_reason"
			Session.commit()
	#удалить у всех специалистов эти сферы из интересов
	all_specialists = Session.query(User).filter(User.specialist != None).all()
	for spec in all_specialists:
		for spec_sphere in spec.spheres:
			for sphere in spheres:
				spec_sphere.remove(sphere)
				#ОТПРАВИТЬ ОПОВЕЩЕНИЕ ЧТО СФЕРА ТЕПЕРЬ НЕДОСТУПНА
				Session.commit()

def drop_current_tasks(user):
	if user.status == "representative":
		for task in user.representative.tasks:
			# TODO
            #if task.status == "in_work":
				#ОТПРАВИТЬ ОПОВЕЩЕНИЕ
			task.status = "canceled_by_represented"
	elif user.status == "specialist":
		for task in user.specialist.tasks:
			drop_specialist_task(task)
		user.specialist.tasks = []
	else:
		raise Exception(f'Юзер "{user.telegram_id}" не представитель или специалист')

def drop_specialist_task(task):
	task.status = "awaiting_specialist"
	task.specialist = None
	Session.commit()

def set_status(user, st): #st = wish_m, wish_r, m, r, s, blocked
	user.status = st
	Session.commit()
	return True

def set_spesialist_spheres(user, spheres):
	interests = []
	for r in spheres:
		t = Session.query(Sphere).filter_by(name=r).first()
		if t is None:
			raise Exception(f'Сфера "{sphere}" не существует')
		else:
			interests.append(t)
	spec = user.specialist
	if spec == None:
		raise Exception("Ошибка, юзер не является специалистом")
	spec.spheres = []
	for sphere in interests:
		assosiation = SpheresToSpecialists()
		assosiation.spheres = sphere
		Session.add(assosiation)
		Session.commit()
		spec.spheres.append(assosiation)
	Session.commit()
	return True

def set_subscribe(user, mode):
	user.mode = mode
	Session.commit()

def set_task_status(task, status):
    if task == None:
        raise Exception("Ошибка, задания {task} не существует")
    else:
        if status not in ['awaiting_confirmation', 'awaiting_specialist', 'in_work', 'closed_with_success', 'canceled_by_represented', 'closed_by_other_reason']:
            raise Exception(f"Ошибка, неправильный статус: {status}")
        else:
            task.status = status
            Session.commit()

# getting
def get_user(telegram_id):
	telegram_id = str(telegram_id)
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	return user if user is not None else False

def get_task(id):
	task = Session.query(Task).filter_by(id = id).first()
	return task


def get_spesialist_spheres(user):
	# user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	if user.specialist is None:
		raise Exception("Ошибка, юзер {telegram_id} не является специалистом")
	sp_sh = user.specialist.spheres
	y = []
	for i in sp_sh:
		y.append(i.spheres.name)
	return y


def get_all_interests():
	list_ = Session.query(Sphere).filter_by(status=True).all()
	list_ = [sphere.name for sphere in list_]
	return list_


def get_opened_tasks(spheres):
    opened_taskes = Session.query(Task).filter_by(status = 'open').all()
    req_tasks = [] 
    for task in opened_taskes:
        common = [d for d in spheres if d in task.spheres]
        if common is not None:
            req_tasks.append(task)
    return req_tasks
	

def get_unchecked_tasks():
	unchecked_taskes = Session.query(Task).filter_by(status = 'check').all()
	return unchecked_taskes


# TODO поменять на другой статус и утвердить статусы
def get_for_check_represen_users():
	list_ = Session.query(User).filter_by(status = 'wish_r').all()
	return list_

# TODO поменять на другой статус и утвердить статусы
def get_for_check_moder_users():
	list_ = Session.query(User).filter_by(status = 'wish_m').all()
	return list_


def get_tasks_for_user(user, task_status):
    if user.status == 'specialist':
        tasks = user.specialist.tasks
    elif user.status == 'representative':
        tasks = user.representative.tasks
    else:
        raise Exception("Ошибка, юзер {telegram_id} не является представителем или специалистом")
    curr = []
    if isinstance(task_status, str):
        for task in tasks:
            if task.status == task_status:
                curr.append(task)
    else:
        for task in tasks:
            if task.status in task_status:
                curr.append(task)
    return curr

def get_users_for_notification(task): #после прохождения задачей модерации
	users_for_notification = []
	all_specialists = Session.query(User).filter(User.specialist != None).all()
	for spec in all_specialists:
		common = [d for d in spec.specialist.spheres if d in task.spheres]
		if common != None:
			users_for_notification.append(spec)
	return users_for_notification


if __name__ == '__main__':
    # user = add_user(346235776, '@tainella', "Загадка")
    # add_representative(user)
    # add_specialist(get_user(418878871))
	#set_task_status("Купить мыло", "open")
	#task = get_task("Купить мыло")
	#users = get_users_for_notification(task)
	#for i in users:
	#print(i.telegram_id)
    # add_spheres_global(["МЛ", "Написание текстов", "Бекенд"])   
    # print(get_all_interests())
    # add_representative(get_user(1409549287))
    # user = get_user(418878871)
    # set_spesialist_spheres(user, ["МЛ", 'Разработка ботов', 'Бекенд'])
    pass
