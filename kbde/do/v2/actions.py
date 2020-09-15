from . import client_base


class ActionList(client_base.Base):
    path = "/actions"


class ActionDetail(client_base.Base):
    path = "/actions/{action_id}"
