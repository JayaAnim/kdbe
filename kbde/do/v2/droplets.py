from . import client_base


class DropletList(client_base.Base):
    path = "/droplets"


class DropletDetail(client_base.Base):
    path = "/droplets/{droplet_id}"
