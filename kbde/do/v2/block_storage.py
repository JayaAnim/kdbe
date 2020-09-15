from . import client_base


class Volume(client_base.Base):
    path = "/volumes"


class VolumeDetail(client_base.Base):
    path = "/volumes/{volume_id}"
