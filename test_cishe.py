"""次舍（CISHE）算子单测：名帖完整、行为达标、只增不覆盖。"""
import unittest

from cishe import Cishe


class TestCishe(unittest.TestCase):
    def setUp(self):
        self.op = Cishe()

    def test_describe(self):
        d = self.op.describe()
        self.assertEqual(d["repo"], "cishe")
        self.assertEqual(d["code"], "CISHE")
        self.assertTrue(d["anchor"].startswith("Ω₀⊂⊙∞⊂Ω"))
        self.assertTrue(d["mingwen"])

    def test_fifo(self):
        self.op.enqueue("笺一")
        self.op.enqueue("笺二")
        self.assertEqual(self.op.dequeue(), "笺一")
        self.assertEqual(self.op.dequeue(), "笺二")
        self.assertIsNone(self.op.dequeue())


if __name__ == "__main__":
    unittest.main()
