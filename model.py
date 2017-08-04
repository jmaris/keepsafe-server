from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import falcon

Base = declarative_base()
engine = create_engine('mysql+pymysql://keepsafe:7k77xJuGeqZYu97gpFfS8xsheXYHGHjB@localhost/keepsafe_db')

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    username_hash = Column(String(88))
    public_key = Column(String(44))

# Base.metadata.create_all(engine)

#Session = sessionmaker(bind = engine)
#session = Session()

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

app = falcon.API()

userResource = UserResource()

app.add_route('/users', userResource)