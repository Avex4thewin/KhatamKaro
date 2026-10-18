import os
from sqlalchemy import create_engine, text

url = os.environ['DATABASE_URL']
engine = create_engine(url)
with engine.connect() as conn:
    print(conn.execute(text('select version()')).scalar())