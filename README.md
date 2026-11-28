# cishe
次舍·笺稿排队缓冲池 | CISHE · ZONGYUAN-ROOT Daotong Component

## Install

零第三方依赖，仅 Python 3.10+ 标准库。

```bash
git clone https://github.com/tanbopiao/cishe.git
cd cishe
python3 -m unittest discover -s tests -v   # 运行测试套件
```

## Usage

```python
from cishe import Cishe

pool = Cishe()
pool.enqueue("笺一")   # 舍官：次舍暂驻，笺稿入池
pool.peek()            # 察官：池首可察，不出池
pool.dequeue()         # 勘官：次第而勘，按序出池
pool.seal()            # 封台账：前缀快照哈希存证
pool.verify_ledger()   # 验台账：篡改现形，合法增长不算篡改
```

## 命名映射表

道统出处：元极恒一·道统构件定名册 V2（第五批）；体系锚：Ω₀⊂⊙∞⊂Ω｜DID-BR-000002。

| 命名 | 逻辑本体 | 算子 | 职责 |
|------|----------|------|------|
| 次舍 | 笺稿排队缓冲池 | `Cishe` | 缓冲池本体，出入有账 |
| 舍（驻） | 入池排队 | `enqueue` | 次舍暂驻，笺稿入池 |
| 勘（出） | 按序出池 | `dequeue` | 次第而勘，FIFO 出池待勘 |
| 察（视） | 池首可察 | `peek` / `depth` | 察舍观笺，不出池、不动账 |
| 台账 | 出入留痕 | `ledger` | 只增不覆盖，深拷贝防外改 |
| 封存 | 防篡改存证 | `seal` | 前缀快照哈希，封存不入账 |
| 验封 | 篡改现形 | `verify_ledger` | 前缀核验，合法增长不算篡改 |

边界：算子 v0.1，三官齐备；遵循元法第四条「只增不覆盖」，方法只增不改名不删，行为变更走新版本。
