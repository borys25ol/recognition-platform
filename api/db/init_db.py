from sqlalchemy import create_engine, MetaData
from werkzeug.security import generate_password_hash

from api.db.tables import users
from utils.common import get_config

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


class RecordNotFound(Exception):
    """Requested record in database was not found"""


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[users])


def drop_tables(engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=[users])


def sample_user_data(engine):
    conn = engine.connect()
    conn.execute(users.insert(), [
        {'username': 'borys25ol',
         'email': 'borysoliinyk@test.com',
         'name': 'Borys',
         'last_name': 'Oliinyk',
         'password': generate_password_hash('q1w2e3r4'),
         }
    ])
    conn.close()


if __name__ == '__main__':
    db_url = DSN.format(**get_config()['postgres'])
    engine = create_engine(db_url)

    # setup_test_db(engine)

    sample_user_data(engine)
