from . import client_base


class VolumeList(client_base.Base):
    path = "/volumes"


class VolumeDetail(client_base.Base):
    path = "/volumes/{volume_id}"


class VolumeSnapshotList(client_base.Base):
    path = "/volumes/{volume_id}/snapshots"


class SnapshotDetail(client_base.Base):
    path = "/snapshots/{snapshot_id}"
