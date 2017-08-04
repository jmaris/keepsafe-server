from sqlalchemy import *

engine = create_engine('mysql+pymysql://keepsafe:7k77xJuGeqZYu97gpFfS8xsheXYHGHjB@localhost/keepsafe_db')

metadata = MetaData()

user = Table('user', metadata,
    Column('id', Integer, primary_key = True),
    Column('username_hash', String(88)),
    Column('public_key', String(44))
)

metadata.create_all(engine)