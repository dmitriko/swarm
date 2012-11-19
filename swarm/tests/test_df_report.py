from .base import BaseTestCase
from .fixtures import DF_RAW
from swarm.reports import DFReport, NodeOnlineReport
from swarm.cluster import Cluster
from swarm.scenarios import on_report
from swarm.stuff import StoragePoint


class DFParseCase(BaseTestCase):
    def test_parsing(self):
        report = DFReport.create(self.node_oid, raw_data=DF_RAW)
        data = report.parsed_data
        self.assertTrue('/home' in data)
        self.assertEqual(data['/home']['avail'], '702G')
        
    def test_update_cluster(self):
        import uuid
        storage_oid = str(uuid.uuid4())
        on_report(NodeOnlineReport.create(self.node_oid,
                                          hostname='testhost',
                                         storages=[dict(
                        node_oid=self.node_oid,
                        storage_oid=storage_oid,
                        path='/home/storage1')]))
        on_report(DFReport.create(self.node_oid, raw_data=DF_RAW))
        cluster = Cluster.instance()
        storage = cluster.get(storage_oid)
        self.assertTrue(storage)
        self.assertEqual(storage.avail, '702G')
        
