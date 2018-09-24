from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import USERNAME, PASSWORD, PORT, SERVER, DB_NAME

engine = create_engine('mysql+pymysql://{username}:{password}@{server}:{port}/{db_name}?charset=utf8'.format(
    username=USERNAME, password=PASSWORD, server=SERVER, port=int(PORT), db_name=DB_NAME), encoding='utf-8', echo=False,
    max_overflow=10, pool_timeout=3, pool_size=5, pool_recycle=120, pool_pre_ping=True)

Session = sessionmaker(bind=engine)

session = Session()
