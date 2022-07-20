import sqlalchemy as db
import pandas as pd
import pprint
import secrets

engine = db.create_engine('sqlite:///jobify.db')
engine.execute(f"CREATE TABLE user")
# query = engine.execute('.tables;').fetchall()
#id_list = engine.execute(f"SELECT job_id FROM jobs WHERE user_id='joshua_feliciano';").fetchall()
#id_list = [id[0] for id in id_list]
#pprint.pprint(id_list)
#print(query)

# print(secrets.token_hex(16))