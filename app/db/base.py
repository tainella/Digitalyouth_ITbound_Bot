from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from loguru import logger

from ..core.settings import Settings

# TODO добавить ТП внутри ПП
# TODO добавить рассылку сообщений внутри ПП

Base = declarative_base(name=Settings().sqlite_dsn.split("/")[-1])
engine = create_engine(Settings().sqlite_dsn, echo=False)
Session = sessionmaker(bind=engine)
scoped_Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False, autoflush=False))


@contextmanager
def session_scope():
    session = scoped_Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(e)
        raise e
    finally:
        session.close()
