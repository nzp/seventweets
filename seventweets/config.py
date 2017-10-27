"""Module that stores runtime configuration for the node.

Classes:
    Config: Encapsulates runtime settings.

"""

import os


class Config:
    """This class encapsulates runtime settings as class attributes.

    Class attributes hold node configuration settings read from environment
    variables. 

    Attributes:
        DB_CONFIG (dict): Database credentials.
        NAME (str): Name of this node, used to uniquely identify it in the
            network.
        ADDRESS (str): Node address, IP or FQDN.
        API_TOKEN (str): Auth token that the front end for this node uses to
            issue state changing commands.

    """

    DB_CONFIG = dict(user=os.environ.get('ST_PG_USER'),
                     password=os.environ.get('ST_PG_PASS'),
                     host=os.environ.get('ST_PG_HOST'))

    NAME = os.environ.get('ST_NODE_NAME')
    ADDRESS = os.environ.get('ST_NODE_ADDRESS')
    API_TOKEN = os.environ.get('ST_API_TOKEN')
