from . import command_base

from kbde.do.v2 import actions


class Command(command_base.GetCommand):
    
    api_client_class = actions.ActionList
