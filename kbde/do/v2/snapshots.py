from . import client_base


class SnapshotList(client_base.Base):
    path = "/snapshots"


class SnapshotDetail(client_base.Base):
    path = "/snapshots/{snapshot_id}"
