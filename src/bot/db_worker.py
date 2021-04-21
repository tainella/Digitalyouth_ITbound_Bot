from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db = declarative_base()
engine = create_engine('sqlite:///Info.db', echo=True)
metadata = MetaData()
Session = sessionmaker(bind=engine)

class User(db):
    __tablename__ = 'users'
    telegram_id = Column(String, primary_key=True)
    username = Column(String)
    telegram_fullname = Column(String)
    bot_block = Column(Boolean) #true = blocked and false = unblocked
    real_fullname = Column(String)
    phone = Column(String)
    status = Column(String) #wish_m, wish_r, m, r, s, blocked
    moderator = relationship('moderators', backref='moders', uselist=False)
    specialist = relationship('specialists', backref='special', uselist=False)
    representative = relationship('representatives', backref='represents', uselist=False)
    
    def __init__(self, telegram_id, username, telegram_fullname, real_fullname, phone, status, spec = None):
        self.telegram_id = telegram_id
        self.username = username
        self.telegram_fullname = telegram_fullname
        self.bot_block = False
        self.real_fullname = real_fullname
        self.phone = phone
        self.status = status
        self.moderator = None
        self.specialist = spec
        self.representative = None

class Moderator(db):
	__tablename__ = 'moderators'
	telegram_id = Column(String, primary_key=True)
	is_admin = Column(Boolean)
	
	def __init__(self, telegram_id):
		self.telegram_id = telegram_id
		self.is_admin = False

class Specialist(db):
	__tablename__ = 'specialists'
	telegram_id = Column(String, primary_key=True)
	interests = relationship('interests', backref='areas')
	current_tasks = relationship('tasks', backref='current_tasks')
	
	def __init__(self, telegram_id):
		self.telegram_id = telegram_id
		self.interests = []
		self.current_tasks = None

class Representative(db):
	__tablename__ = 'representatives'
	telegram_id = Column(String, primary_key=True)
	tasks = relationship('tasks', backref='published_tasks')
	
	def __init__(self, telegram_id):
		self.telegram_id = telegram_id
		self.tasks = []

class Task(db):
	__tablename__ = 'tasks'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	spheres = relationship('interests', backref='spheres')
	status = Column(String) #check, open, worked, closed
	represen_id = Column(String)
	specialist_id = Column(String)
	
	def __init__(self, name, description, spheres, represen_id):
		self.id = session.query(Task).count() + 1
		self.name = name
		self.description = description
		self.spheres = spheres
		self.status = check
		self.represen_id = represen_id
		self.specialist_id = None

class Interest(db):
	__tablename__ = 'interests'
	name = Column(String, primary_key=True)
	def __init__(self, name):
		self.name = name

db.metadata.create_all(engine)

# adding
def add_user(telegram_id, username, telegram_fullname, real_fullname, phone, status):
	if status == 's':
		add_spec(telegram_id)
		spec = Session.query(Specialist).filter_by(telegram_id=telegram_id).first()
		new_user = User(telegram_id, username, telegram_fullname, real_fullname, phone, status, spec)
	elif status == 'wish_m':
		new_user = User(telegram_id, username, telegram_fullname, real_fullname, phone, status)
	elif status == 'wish_r':
		new_user = User(telegram_id, username, telegram_fullname, real_fullname, phone, status)
	Session.add(new_user)
	Session.commit()

def add_spec(telegram_id):
	new_spec = Specialist(telegram_id)
	Session.add(new_spec)
	Session.commit()

def add_task(name, description, spheres, represen_id):
	new_task = Task(name, description, spheres, represen_id)
	Session.add(new_task)
	Session.commit()

def add_interests(spheres):
	for r in spheres:
		t = Session.query(Interest).filter_by(name=r).first()
		if t == None:
			new = Interest(r)
			Session.add(new)
			Session.commit()

# setting
def set_status(telegram_id, st): #st = wish_m, wish_r, m, r, s, blocked
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	if user == None:
		return False #returns Boolean
	else: 
		user.status = st
		Session.commit()
		return True

def change_interests(telegram_id, interests):
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	if user == None:
		return False #returns Boolean
	else: 
		user.interests = []
		for r in interests:
			sphere = Interest(name = r)
			user.interests.append(sphere)
		Session.commit()
		return True

# getting

def get_interests(telegram_id):
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	return user.interests

def get_all_interests():
	list = Session.query(Interest).all()
	return list

def get_opened_taskes():
	opened_taskes = Session.query(Task).filter_by(status = 'open').all()
	return opened_taskes
	
def get_unchecked_taskes():
	unchecked_taskes = Session.query(Task).filter_by(status = 'check').all()
	return unchecked_taskes

def get_check_represen_users():
	list = Session.query(User).filter_by(status = 'wish_r').all()
	return list

def get_check_moder_users():
	list = Session.query(User).filter_by(status = 'wish_m').all()
	return list

def get_status(telegram_id):
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	if user == None:
		return None
	else:
		return user.status
