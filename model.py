from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import falcon
import json, uuid, random, string, base64, datetime

import nacl.encoding, nacl.hash

from captcha.image import ImageCaptcha

ALLOWED_ORIGINS = ['http://localhost:4200']

Base = declarative_base()
engine = create_engine('mysql+pymysql://keepsafe:7k77xJuGeqZYu97gpFfS8xsheXYHGHjB@localhost/keepsafe_db')

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    username_hash = Column(String(88))
    public_key = Column(String(44))

class Captcha(Base):
    __tablename__ = 'captcha'

    uuid = Column(String(36), primary_key = True)
    answer = Column(String(6))
    date_created = Column(DateTime, default = func.now())
    ip_address_hash = Column(String(44))

Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine)
session = Session()

#new_user = User(
#    username_hash = 'f08MWDBZh8BFMDFxxap1TT/geuP8jeBqN7bQsToN1usxrYyhipONKAuh3mmJZ4+eyThKh3oea8d8bk0lrQj7Uw==',
#    public_key = 'QOK6kY3xFFT/4wQhjkCZrprclu5VrKc/gdK5PYdI6kQ='
#)

#session.add(new_user)
#session.commit()

class UserResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = 'User::Get'

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = 'User::Post'

class CaptchaResource(object):
    def on_get(self, req, resp):
        # Generate a new captcha

        image = ImageCaptcha()

        captcha_uuid = str(uuid.uuid4())
        captcha_answer = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(6))
        captcha_image = 'data:image/png;base64,' + str(base64.b64encode(image.generate(captcha_answer).getvalue())).split("'")[1]

        # The answer should be case insensitive, the caps are just there for the bots
        captcha_answer = captcha_answer.lower()

        # Hash the user's IP address with the captcha UUID as salt
        captcha_ip_address_hash = nacl.hash.sha256(str.encode(captcha_uuid + req.remote_addr), encoder = nacl.encoding.Base64Encoder).decode('utf-8')

        captcha = Captcha(
            uuid = captcha_uuid,
            answer = captcha_answer,
            # date_created = datetime.datetime.utcnow,
            ip_address_hash = captcha_ip_address_hash
        )

        session = req.context['session']

        session.add(captcha)
        session.commit()

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'uuid': captcha_uuid,
            'image': captcha_image
        })

class CorsMiddleware(object):
    def process_request(self, request, response):
        origin = request.get_header('Origin')

        if origin in ALLOWED_ORIGINS:
            response.set_header('Access-Control-Allow-Origin', origin)

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

class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        userResource = UserResource()
        captchaResource = CaptchaResource()

        self.add_route('/users', userResource)
        self.add_route('/captcha', captchaResource)

app = App(middleware = [CorsMiddleware(), DatabaseSessionMiddleware(session)])