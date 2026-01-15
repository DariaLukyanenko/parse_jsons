import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

load_dotenv()


class PreBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, autoincrement=True)


DB_USER = os.getenv('DB_USER_LOGIN')
DB_PASS = os.getenv('DB_USER_PASSWORD')
DB_IP = os.getenv('DB_IP')
DB_NAME = os.getenv('DB_NAME')


Base = declarative_base(cls=PreBase)
engine = create_engine(
     f'mssql+pyodbc://{DB_USER}:{DB_PASS}@{DB_IP}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server'
)
Session = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
