from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

ALLOWED_ORIGINS = ['http://localhost:4200']

Base = declarative_base()
engine = create_engine('mysql+pymysql://keepsafe:7k77xJuGeqZYu97gpFfS8xsheXYHGHjB@localhost/keepsafe_db')

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    public_key = Column(Binary(32))

class Captcha(Base):
    __tablename__ = 'captcha'

    uuid = Column(String(36), primary_key = True)
    answer_hash = Column(Binary(32))
    created = Column(DateTime, default = func.now())
    ip_address_hash = Column(Binary(32))
    user_agent_hash = Column(Binary(32))

class Challenge(Base):
    __tablename__ = 'challenge'
    uuid = Column(String(36), primary_key = True)
    user_id = Column(Integer, ForeignKey("user.id"))
    answer_hash = Column(Binary(32))
    created = Column(DateTime, default = func.now())

    user = relationship("User")

class UserSession(Base):
    __tablename__ = 'session'
    uuid = Column(String(36), primary_key = True)
    user_id = Column(Integer, ForeignKey("user.id"))
    created = Column(DateTime, default = func.now())
    ip_address_hash = Column(Binary(32))
    user_agent_hash = Column(Binary(32))

    user = relationship("User")

class Devices(Base):
    __tablename__ = 'devices'
    uuid = Column(String(36), primary_key = True)
    userID = Column(Integer)
    answer = Column(String(6))
    public_key = Column(String(44))
    expires = Column(DateTime)
    permissions = Column(String(4))

Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine)
session = Session()

class CorsMiddleware(object):
    def process_request(self, request, response):
        origin = request.get_header('Origin')

        if origin in ALLOWED_ORIGINS:
            response.set_header('Access-Control-Allow-Origin', origin)
            response.set_header('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept')

class DatabaseSessionMiddleware(object):
    def __init__(self, db_session):
        self._db_session = db_session

    # When a new request comes in, add the database session to the request context
    def process_request(self, req, res, resource = None):
        req.context['db_session'] = self._db_session

    # When a response is provided to a request, close the session
    def process_response(self, req, res, resource = None):
        db_session = req.context['db_session']

        db_session.close()

class ConfigurationMiddleware(object):
    def __init__(self, server_key_pair):
        self._configuration = {
            'server_key_pair': server_key_pair
        }

    def process_request(self, req, res, resource = None):
        req.context['configuration'] = self._configuration
