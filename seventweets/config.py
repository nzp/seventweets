import os


class Config:
    DB_CONFIG = dict(user=os.environ.get('PG_USER'),
                     password=os.environ.get('PG_PASS'),
                     host=os.environ.get('PG_HOST'))

    NAME = 'nzp'
