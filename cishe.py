"""次舍（CISHE）· 笺稿排队缓冲池

道统出处：元极恒一·道统构件定名册 V2 ｜ 第五批
体系锚：Ω₀⊂⊙∞⊂Ω｜DID-BR-000002

工程映射：笺稿排队缓冲池。

命名映射：舍（驻）→ enqueue 次舍暂驻，笺稿入池排队；勘（出）→ dequeue 次第而勘，
按序出池待勘；察（视）→ peek 察舍观笺，池首可察而不出池。
出入台账只增不覆盖，seal/verify_ledger 前缀快照哈希防篡改。

边界：本件为算子 v0.1——三官齐备；遵循元法第四条「只增不覆盖」，
方法只增不改名不删，行为变更走新版本；凭据不入档，宣称与事实分离。
纯标准库，Python 3.10+。
"""

import copy
import hashlib
import json


class Cishe:
    """次舍（CISHE）算子 v0.1：舍官驻、勘官出、察官视。"""

    ANCHOR = "Ω₀⊂⊙∞⊂Ω｜DID-BR-000002"
    CODE = "CISHE"

    def __init__(self, config=None):
        self.config = dict(config or {})
        self.events = []  # 只增不覆盖：出入台账
        self.pool = []  # 笺稿排队缓冲池（FIFO）
        self._snapshots = []  # 已封存的台账前缀快照 (长度, 哈希)

    # ---------- 名帖 ----------

    def describe(self):
        """构件名帖：名、代号、职责、铭文、体系锚。"""
        return {
            "repo": "cishe",
            "cn": "次舍",
            "code": self.CODE,
            "duty": "笺稿排队缓冲池",
            "mingwen": "次舍暂驻，次第而勘",
            "anchor": self.ANCHOR,
        }

    # ---------- 舍官：次舍暂驻 ----------

    def enqueue(self, jiancao):
        """次舍暂驻：笺稿入池排队，返回池深。"""
        self.pool.append(jiancao)
        self.events.append({"event": "enqueue", "depth": len(self.pool)})
        return len(self.pool)

    # ---------- 勘官：次第而勘 ----------

    def dequeue(self):
        """次第而勘：按序出池待勘，池空则无笺可出。"""
        if not self.pool:
            return None
        item = self.pool.pop(0)
        self.events.append({"event": "dequeue", "depth": len(self.pool)})
        return item

    # ---------- 察官：察舍观笺 ----------

    def peek(self):
        """察舍观笺：池首可察，笺稿不出池；池空则无笺可察。"""
        return self.pool[0] if self.pool else None

    def depth(self):
        """池深：当前池内笺稿数。"""
        return len(self.pool)

    # ---------- 台账防篡改 ----------

    def ledger(self):
        """出入台账：只增不覆盖，返回深拷贝防外改。"""
        return copy.deepcopy(self.events)

    def seal(self):
        """封台账：取前缀快照哈希存证（封存动作本身不入台账），返回哈希值。"""
        digest = self._hash_prefix(len(self.events))
        self._snapshots.append((len(self.events), digest))
        return digest

    def verify_ledger(self, expect=None):
        """验台账：前缀内篡改现形返回 False；封存后新增长的合法条目不算篡改。
        expect 给定时按全量哈希比对。"""
        if expect is not None:
            return self._ledger_hash() == expect
        if not self._snapshots:
            return True  # 尚无封存，无可篡之征
        n, digest = self._snapshots[-1]
        return self._hash_prefix(n) == digest

    # ---------- 内部 ----------

    def _ledger_hash(self):
        return self._hash_prefix(len(self.events))

    def _hash_prefix(self, n):
        canonical = json.dumps(self.events[:n], ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
