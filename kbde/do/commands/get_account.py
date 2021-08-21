from . import command_base

from kbde.do.v2 import account


class Command(command_base.GetCommand):
    
    api_client_class = account.Account
