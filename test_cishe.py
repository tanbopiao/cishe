"""次舍（CISHE）算子骨架单测：名帖完整、桩位齐整、只增不覆盖。"""
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

    def test_enqueue_stub(self):
        with self.assertRaises(NotImplementedError):
            self.op.enqueue(None)

    def test_dequeue_stub(self):
        with self.assertRaises(NotImplementedError):
            self.op.dequeue()


if __name__ == "__main__":
    unittest.main()
