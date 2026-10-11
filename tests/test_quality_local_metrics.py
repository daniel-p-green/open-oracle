import json
import unittest
from strands_quality.receipts import EvidenceReceipt
from strands_quality.local_metrics import AggregateMetrics, DebugReceiptBuffer


class LocalMetricsTests(unittest.TestCase):
    def receipt(self):
        receipt=EvidenceReceipt(config_hash='a'*64, execution='exact_source', source_catalog={})
        receipt.finish()
        return receipt
    def test_aggregate_has_no_request_identity_or_source_history(self):
        receipt=self.receipt()
        aggregate=AggregateMetrics()
        aggregate.record(receipt)
        value=aggregate.snapshot()
        self.assertNotIn(receipt.request_id,json.dumps(value))
        self.assertNotIn('released_sources',value)
        self.assertIsNone(value['unique_visitor_count'])
        self.assertEqual(sum(value['completed_operation_counts'].values()),1)
    def test_disabled_default_and_absolute_ttl(self):
        receipt=self.receipt()
        disabled=DebugReceiptBuffer()
        disabled.put(receipt)
        self.assertEqual(disabled.snapshots(),[])
        now=[0.]
        enabled=DebugReceiptBuffer(enabled=True,ttl_seconds=10,clock=lambda:now[0])
        enabled.put(receipt)
        now[0]=9
        self.assertEqual(len(enabled.snapshots()),1)
        now[0]=10
        self.assertEqual(enabled.snapshots(),[])
    def test_count_bound_stop_and_clear(self):
        buffer=DebugReceiptBuffer(enabled=True,max_entries=1)
        buffer.put(self.receipt());buffer.put(self.receipt())
        self.assertEqual(len(buffer.snapshots()),1)
        buffer.clear()
        self.assertEqual(buffer.snapshots(),[])
        buffer.put(self.receipt());buffer.stop();buffer.put(self.receipt())
        self.assertEqual(buffer.snapshots(),[])
