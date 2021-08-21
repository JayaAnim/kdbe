from . import client_base


class DropletActionList(client_base.Base):
    path = "/droplets/{droplet_id}/actions"


class DropletActionDetail(client_base.Base):
    path = "/droplets/{droplet_id}/actions/{action_id}"
