from . import command_base

from kbde.do.v2 import actions


class Command(command_base.GetCommand):
    
    api_client_class = actions.ActionDetail

    def add_arguments(self, parser):
        parser.add_argument("action_id")
