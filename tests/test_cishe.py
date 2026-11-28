"""次舍（CISHE）算子测试套件：名帖完整、三官行为达标、台账防篡改、v1 行为回归重放。

覆盖：舍官（enqueue）、勘官（dequeue）、察官（peek/depth）、
台账（ledger/seal/verify_ledger 前缀快照哈希防篡改）、只增不覆盖边界。
"""

import unittest

from cishe import Cishe


class TestMingtie(unittest.TestCase):
    """名帖与道统映射一致性。"""

    def setUp(self):
        self.op = Cishe()

    def test_describe_repo(self):
        d = self.op.describe()
        self.assertEqual(d["repo"], "cishe")

    def test_describe_cn(self):
        self.assertEqual(self.op.describe()["cn"], "次舍")

    def test_describe_code(self):
        self.assertEqual(self.op.describe()["code"], "CISHE")

    def test_describe_duty(self):
        self.assertEqual(self.op.describe()["duty"], "笺稿排队缓冲池")

    def test_describe_mingwen(self):
        self.assertTrue(self.op.describe()["mingwen"])

    def test_describe_anchor(self):
        self.assertTrue(self.op.describe()["anchor"].startswith("Ω₀⊂⊙∞⊂Ω"))


class TestSheGuan(unittest.TestCase):
    """舍官：次舍暂驻，笺稿入池。"""

    def setUp(self):
        self.op = Cishe()

    def test_enqueue_returns_depth(self):
        self.assertEqual(self.op.enqueue("笺一"), 1)
        self.assertEqual(self.op.enqueue("笺二"), 2)

    def test_enqueue_accepts_any_payload(self):
        self.assertEqual(self.op.enqueue({"id": 1}), 1)
        self.assertEqual(self.op.enqueue(None), 2)

    def test_enqueue_records_event(self):
        self.op.enqueue("笺一")
        self.assertEqual(self.op.ledger()[-1]["event"], "enqueue")


class TestKanGuan(unittest.TestCase):
    """勘官：次第而勘，按序出池。"""

    def setUp(self):
        self.op = Cishe()

    def test_dequeue_fifo(self):
        self.op.enqueue("笺一")
        self.op.enqueue("笺二")
        self.assertEqual(self.op.dequeue(), "笺一")
        self.assertEqual(self.op.dequeue(), "笺二")

    def test_dequeue_empty_returns_none(self):
        self.assertIsNone(self.op.dequeue())

    def test_dequeue_records_event(self):
        self.op.enqueue("笺一")
        self.op.dequeue()
        self.assertEqual(self.op.ledger()[-1]["event"], "dequeue")

    def test_interleave_order(self):
        self.op.enqueue("甲")
        self.op.enqueue("乙")
        self.assertEqual(self.op.dequeue(), "甲")
        self.op.enqueue("丙")
        self.assertEqual(self.op.dequeue(), "乙")
        self.assertEqual(self.op.dequeue(), "丙")
        self.assertIsNone(self.op.dequeue())


class TestChaGuan(unittest.TestCase):
    """察官：察舍观笺，池首可察而不出池。"""

    def setUp(self):
        self.op = Cishe()

    def test_peek_first_without_pop(self):
        self.op.enqueue("笺一")
        self.op.enqueue("笺二")
        self.assertEqual(self.op.peek(), "笺一")
        self.assertEqual(self.op.depth(), 2)

    def test_peek_empty_returns_none(self):
        self.assertIsNone(self.op.peek())

    def test_peek_does_not_touch_ledger(self):
        self.op.enqueue("笺一")
        before = len(self.op.ledger())
        self.op.peek()
        self.assertEqual(len(self.op.ledger()), before)

    def test_depth(self):
        self.assertEqual(self.op.depth(), 0)
        self.op.enqueue("笺一")
        self.assertEqual(self.op.depth(), 1)
        self.op.dequeue()
        self.assertEqual(self.op.depth(), 0)


class TestLedgerTamperEvident(unittest.TestCase):
    """台账防篡改：前缀快照哈希，篡改现形，合法增长不算篡改。"""

    def setUp(self):
        self.op = Cishe()

    def test_ledger_returns_copy(self):
        self.op.enqueue("笺一")
        ledger = self.op.ledger()
        ledger.clear()
        self.assertEqual(len(self.op.ledger()), 1)

    def test_seal_returns_digest(self):
        self.op.enqueue("笺一")
        digest = self.op.seal()
        self.assertIsInstance(digest, str)
        self.assertEqual(len(digest), 64)

    def test_verify_without_seal_is_true(self):
        self.op.enqueue("笺一")
        self.assertTrue(self.op.verify_ledger())

    def test_verify_after_legal_growth(self):
        """封存后合法新增（入池出池）不算篡改。"""
        self.op.enqueue("笺一")
        self.op.seal()
        self.op.enqueue("笺二")
        self.op.dequeue()
        self.assertTrue(self.op.verify_ledger())

    def test_tamper_past_event_detected(self):
        """封存后篡改历史台账，验封现形。"""
        self.op.enqueue("笺一")
        self.op.seal()
        self.op.events[0]["event"] = "dequeue"  # 模拟篡改历史
        self.assertFalse(self.op.verify_ledger())

    def test_tamper_delete_event_detected(self):
        self.op.enqueue("笺一")
        self.op.enqueue("笺二")
        self.op.seal()
        del self.op.events[0]  # 模拟删档
        self.assertFalse(self.op.verify_ledger())

    def test_reseal_after_growth(self):
        """再次封存以新前缀为准。"""
        self.op.enqueue("笺一")
        self.op.seal()
        self.op.enqueue("笺二")
        self.op.seal()
        self.op.events[0]["event"] = "dequeue"
        self.assertFalse(self.op.verify_ledger())

    def test_verify_with_expect_full_hash(self):
        self.op.enqueue("笺一")
        digest = self.op.seal()
        self.assertTrue(self.op.verify_ledger(expect=digest))
        self.op.enqueue("笺二")
        self.assertFalse(self.op.verify_ledger(expect=digest))


class TestRegressionV1(unittest.TestCase):
    """v1 行为回归重放：原 test_cishe.py 两条核心行为原样保留。"""

    def test_v1_describe_regression(self):
        op = Cishe()
        d = op.describe()
        self.assertEqual(d["repo"], "cishe")
        self.assertEqual(d["code"], "CISHE")
        self.assertTrue(d["anchor"].startswith("Ω₀⊂⊙∞⊂Ω"))
        self.assertTrue(d["mingwen"])

    def test_v1_fifo_regression(self):
        op = Cishe()
        op.enqueue("笺一")
        op.enqueue("笺二")
        self.assertEqual(op.dequeue(), "笺一")
        self.assertEqual(op.dequeue(), "笺二")
        self.assertIsNone(op.dequeue())

    def test_only_grows_no_removal(self):
        """只增不覆盖：v0.1 保留 v1 全部公开方法。"""
        for method in ("describe", "enqueue", "dequeue", "peek", "depth",
                       "ledger", "seal", "verify_ledger"):
            self.assertTrue(callable(getattr(Cishe, method, None)), method)


if __name__ == "__main__":
    unittest.main()
