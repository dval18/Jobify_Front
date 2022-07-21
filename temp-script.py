import sqlalchemy as db
import pandas as pd
import pprint
import secrets
from job_search import db
from job_search import User
# print(User.query.all())
engine = db.create_engine('sqlite:///jobify.db', {})
query = engine.execute(f"SELECT * FROM saved_job;").fetchall()
print(query)


# print(engine.table_names())
# query = engine.execute('.tables;').fetchall()
#id_list = engine.execute(f"SELECT job_id FROM jobs WHERE user_id='joshua_feliciano';").fetchall()
#id_list = [id[0] for id in id_list]
#pprint.pprint(id_list)
#print(query)

# print(secrets.token_hex(16))