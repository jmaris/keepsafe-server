from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

ALLOWED_ORIGINS = ['http://localhost:4200']

Base = declarative_base()
engine = create_engine('mysql+pymysql://keepsafe:7k77xJuGeqZYu97gpFfS8xsheXYHGHjB@localhost/keepsafe_db')

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    publicKey = Column(String(44))

class Captcha(Base):
    __tablename__ = 'captcha'

    uuid = Column(String(36), primary_key = True)
    answer = Column(String(6))
    created = Column(DateTime, default = func.now())
    ip_address_hash = Column(String(44))

class Challenge(Base):
        __tablename__ = 'challenges'
        uuid = Column(String(36), primary_key = True)
        userID = Column(Integer)
        answer = Column(String(44))
        created = Column(DateTime, default = func.now())
        

Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine)
session = Session()

#new_user = User(
#    username_hash = 'f08MWDBZh8BFMDFxxap1TT/geuP8jeBqN7bQsToN1usxrYyhipONKAuh3mmJZ4+eyThKh3oea8d8bk0lrQj7Uw==',
#    public_key = 'QOK6kY3xFFT/4wQhjkCZrprclu5VrKc/gdK5PYdI6kQ='
#)

#session.add(new_user)
#session.commit()

class CorsMiddleware(object):
    def process_request(self, request, response):
        origin = request.get_header('Origin')

        if origin in ALLOWED_ORIGINS:
            response.set_header('Access-Control-Allow-Origin', origin)
            response.set_header('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept')

class DatabaseSessionMiddleware(object):
    def __init__(self, session):
        self._session = session

    # When a new request comes in, add the database session to the request context
    def process_request(self, req, res, resource = None):
        req.context['session'] = self._session

    # When a response is provided to a request, close the session
    def process_response(self, req, res, resource = None):
        session = req.context['session']

        session.close()

class ConfigurationMiddleware(object):
    def __init__(self, server_key_pair):
        self._configuration = {
            'server_key_pair': server_key_pair
        }

    def process_request(self, req, res, resource = None):
        req.context['configuration'] = self._configuration