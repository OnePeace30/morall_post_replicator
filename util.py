import logging
import os
import sqlalchemy as sa

from io import StringIO
from sqlalchemy.orm import sessionmaker
from html.parser import HTMLParser
from contextlib import contextmanager
from configparser import ConfigParser, NoOptionError

from models import  BaseMaster, BaseSlave


config = ConfigParser()
current_path = os.path.dirname(__file__)
config_file = os.path.join(current_path, 'config.ini')
config.read(config_file)
mode = 'MASTER'
try:
    DB_USER = config.get(mode, 'db_user')
    DB_PWD = config.get(mode, 'db_pwd')
    DB_HOST = config.get(mode, 'db_host')
    DB_PORT = config.get(mode, 'db_port')
    DB_NAME = config.get(mode, 'db_name')
except NoOptionError:
    raise
master_engine = sa.create_engine(
    f'postgresql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    echo=True,
)
mode = 'SLAVE'
try:
    DB_USER = config.get(mode, 'db_user')
    DB_PWD = config.get(mode, 'db_pwd')
    DB_HOST = config.get(mode, 'db_host')
    DB_PORT = config.get(mode, 'db_port')
    DB_NAME = config.get(mode, 'db_name')
except NoOptionError:
    raise
slave_engine = sa.create_engine(
    f'postgresql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    echo=True,
)
logger = logging.getLogger('replicator')




class Database():

    def __init__(self):
        logger.info('Init database connection')
        DBSession_master = sessionmaker(
            binds={
                BaseMaster: master_engine,
            },
            expire_on_commit=False,
        )
        DBSession_slave = sessionmaker(
            binds={
                BaseSlave: slave_engine,
            },
            expire_on_commit=False,
        )
        self.master_session = DBSession_master()
        self.slave_session = DBSession_slave()

    def __del__(self):
        logger.info('Close database connection')
        self.master_session.close()
        self.slave_session.close()

    @contextmanager
    def session_scope(self, session):
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    # django like method
    def get_or_create(self, session, model, defaults=None, **kwargs):
        with self.session_scope(session) as _session:
            instance = _session.query(model).filter_by(**kwargs).one_or_none()
            if instance:
                return instance, False
            else:
                kwargs |= defaults or {}
                instance = model(**kwargs)
                try:
                    _session.add(instance)
                    _session.commit()
                except Exception:
                    _session.rollback()
                    instance = _session.query(model).filter_by(**kwargs).one()
                    return instance, False
                else:
                    return instance, True


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

