from . import client_base


class VolumeActionList(client_base.Base):
    path = "/volumes/{volume_id}/actions"


class VolumeNameActionList(client_base.Base):
    path = "/volumes/actions"


class VolumeActionDetail(client_base.Base):
    path = "/volumes/{volume_id}/actions/{action_id}"
