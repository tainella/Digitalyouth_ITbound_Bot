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
		self.interests = None
		self.current_tasks = None

class Representative(db):
	__tablename__ = 'representatives'
	telegram_id = Column(String, primary_key=True)
	tasks = relationship('tasks', backref='published_tasks')
	
	def __init__(self, telegram_id):
		self.telegram_id = telegram_id
		self.tasks = None

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

# setting
def set_status(telegram_id, st): #st = wish_m, wish_r, m, r, s, blocked
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	if user == None:
		return False #returns Boolean
	else: 
		user.status = st
		return True

# other
def for_check_represen_users():
	list = []
	for instance in Session.query(User).order_by(telegram_id): 
		if instance.status == wish_r:
			list.append(instance)
	return list

def for_check_moder_users():
	list = []
	for instance in Session.query(User).order_by(telegram_id): 
		if instance.status == wish_m:
			list.append(instance)
	return list

def check_status(telegram_id):
	user = Session.query(User).filter_by(telegram_id=telegram_id).first()
	if user == None:
		return None
	else:
		return user.status


	



