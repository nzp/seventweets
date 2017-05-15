import os


class Config:
    DB_CONFIG = dict(user=os.environ.get('ST_PG_USER'),
                     password=os.environ.get('ST_PG_PASS'),
                     host=os.environ.get('ST_PG_HOST'))

    NAME = 'nzp'
