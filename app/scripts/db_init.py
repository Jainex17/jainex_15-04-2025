from app.models import Base
from app.db import engine

def create_all_table():
    Base.metadata.create_all(bind=engine)
    print("All Tables Created successfully")

create_all_table()