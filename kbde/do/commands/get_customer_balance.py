from . import command_base

from kbde.do.v2 import balance


class Command(command_base.GetCommand):
    
    api_client_class = balance.CustomerBalanceDetail
