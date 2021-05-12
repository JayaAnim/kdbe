from . import command_base

from kbde.do.v2 import billing_history


class Command(command_base.GetCommand):
    
    api_client_class = billing_history.BillingHistoryList
