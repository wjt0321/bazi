# 《三命通会》八字命理分析工具

基于明代万民英所著命理经典《三命通会》的八字命理分析系统，提供完整的排盘、分析、择日、合盘等功能。零重型依赖，仅使用 Python 标准库和 `lunar_python`。

## 功能特性

- **八字排盘**：公历/农历输入，自动计算四柱、五行、十神
- **大运流年**：起运计算、大运排列、流年分析
- **神煞判断**：天乙贵人、文昌、驿马、桃花、羊刃、空亡等
- **命宫胎元身宫**：完整辅助命宫盘
- **风水参考**：喜用神、吉利方位/颜色/数字/行业
- **择日分析**：十二建星 + 事件宜忌评分
- **合盘分析**：天干五合、地支六合/六冲、五行互补
- **原文检索**：基于《三命通会》知识库的关键词检索

## 快速开始

### 安装

```bash
git clone https://github.com/wjt0321/bazi.git
cd bazi/scripts
pip install -r requirements.txt
```

### 命令行使用

```bash
# 基础排盘
python bazi.py --year 1990 --month 5 --day 15 --hour 14 --gender 男

# JSON 输出
python bazi.py --year 1990 --month 5 --day 15 --hour 14 --gender 男 --json

# 择日分析
python bazi.py --year 1990 --month 5 --day 15 --hour 14 --gender 男 --zeri 2025 6 1 结婚

# 合盘分析
python bazi.py --year 1990 --month 5 --day 15 --hour 14 --gender 男 --hepan 1992 3 8 10 女

# 跳过原文检索（更快）
python bazi.py --year 1990 --month 5 --day 15 --hour 14 --gender 男 --no-rag
```

### Python 调用

```python
from bazi_paipan import BaziPaipan

paipan = BaziPaipan()
result = paipan.paipan(1990, 5, 15, 14, gender="男")

print(result["bazi_string"])  # 庚午 辛巳 庚辰 癸未
print(result["wuxing"])       # 五行统计
print(result["shishen_detail"])  # 十神关系

# 大运
from lunar_python import Solar
solar = Solar.fromYmdHms(1990, 5, 15, 14, 0, 0)
lunar = solar.getLunar()
qiyun = paipan.compute_qiyun(solar, lunar, "男")
dayun = paipan.compute_dayun(result["bazi"], "男")

# 神煞
shensha = paipan.compute_shensha(result["bazi"])

# 风水
fengshui = paipan.fengshui_reference(result["bazi"])

# 择日
zeri = paipan.zeri_analysis(2025, 6, 1, event_type="结婚")

# 合盘
bazi2 = paipan.paipan(1992, 3, 8, 10, gender="女")
hepan = paipan.hepan_analysis(result["bazi"], bazi2["bazi"])
```

## 项目结构

```
bazi/
├── scripts/
│   ├── bazi.py              # 主命令行工具
│   ├── bazi_paipan.py       # 八字排盘核心库
│   ├── rag_retriever.py     # 知识库检索（零依赖）
│   ├── init_knowledge_base.py  # 知识库初始化
│   ├── interactive.py       # 交互式界面
│   ├── demo.py              # 演示脚本（保留兼容）
│   ├── demo_light.py        # 精简演示
│   ├── demo_preset.py       # 预设演示
│   └── requirements.txt     # 依赖：仅 lunar_python
├── data/
│   └── sanmingtonghui_chunks.json  # 《三命通会》知识库
├── references/
│   └── bazi_guide.md        # 八字基础知识参考
├── SKILL.md                 # Claude Code Skill 文档
├── AGENT.md                 # Agent 行为规范
├── CLAUDE.md                # Claude 专属配置
└── README.md                # 本文档
```

## 依赖

| 包名 | 版本 | 说明 |
|------|------|------|
| lunar_python | >=1.8.0 | 农历和八字计算 |

**零重型依赖**：已移除 sentence-transformers、numpy 等。RAG 检索改为纯关键词匹配。

## 文档

| 文档 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | Claude Code Skill 核心定义 |
| [AGENT.md](AGENT.md) | Agent 行为规范和工具调用指南 |
| [CLAUDE.md](CLAUDE.md) | Claude 专属配置和 Prompt 模板 |
| [references/bazi_guide.md](references/bazi_guide.md) | 八字基础知识 |

## 许可证

仅供学习和研究使用，命理分析仅供参考，不作为重大决策依据。
