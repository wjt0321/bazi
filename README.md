# 《三命通会》智能命理 Agent Skill

基于明代万民英所著命理经典《三命通会》的 Claude Code Agent Skill，提供完整的八字命理分析能力，包括八字排盘、命理分析、事件预测和知识问答功能。

## 目录

- [功能介绍](#功能介绍)
- [安装说明](#安装说明)
- [初始化知识库](#初始化知识库)
- [使用方法](#使用方法)
- [工具说明](#工具说明)
- [项目结构](#项目结构)
- [依赖说明](#依赖说明)
- [注意事项](#注意事项)
- [参考资料](#参考资料)

---

## 功能介绍

本 Skill 提供以下核心功能：

### 1. 八字排盘
- 根据出生年月日时排出完整八字（年柱、月柱、日柱、时柱）
- 计算五行分布和十神关系
- 支持公历和农历输入
- 自动处理闰年和闰月

### 2. 命理分析
- 基于《三命通会》进行深度命理分析
- 分析日主强弱、五行生克、十神配置
- 判断用神和忌神
- 性格、事业、财运、感情、健康等全方位分析

### 3. 事件预测
- 分析特定事件的吉凶（签约、搬家、开业、结婚等）
- 择日分析，选择有利时间
- 给出趋吉避凶的建议

### 4. 知识问答
- 解答命理概念问题（什么是七杀、十神有哪些等）
- 解释《三命通会》的原文论断
- 提供命理知识的应用指导

---

## 安装说明

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆或下载本项目**

```bash
cd sanmingtonghui-skill/scripts
```

2. **安装 Python 依赖**

```bash
pip install -r requirements.txt
```

这将安装以下依赖：
- `lunar_python>=1.8.0` - 农历和八字计算
- `sentence-transformers>=2.2.0` - Embedding 模型
- `numpy>=1.24.0` - 数值计算

3. **验证安装**

```bash
python -c "from bazi_paipan import BaziPaipan; print('安装成功!')"
```

---

## 初始化知识库

首次使用前需要初始化知识库，这将生成《三命通会》文本的 Embedding 向量。

### 步骤

1. **确保原始文本存在**

项目已包含预处理好的知识库文件：
```
sanmingtonghui-skill/data/sanmingtonghui_chunks.json
```

如需重新生成，执行：

```bash
cd sanmingtonghui-skill/scripts
python init_knowledge_base.py --input ../../sanmingtonghui.txt --output ../data/sanmingtonghui_chunks.json
```

2. **初始化过程说明**

初始化脚本会：
- 加载《三命通会》原始文本
- 按卷和章节进行智能分块
- 使用 multilingual MiniLM 模型计算 Embedding 向量
- 保存为 JSON 格式知识库

**注意**：首次运行会下载 Embedding 模型（约 500MB），请确保网络连接正常。

---

## 使用方法

### 方法一：作为 Claude Code Agent Skill 使用

1. 将本目录配置为 Claude Code 的 Skill
2. 在 Claude Code 中通过对话进行命理分析

**示例对话**：

```
用户: 我想算命

助手: 您好！要进行命理分析，需要您提供以下信息：
      1. 出生年份（公历）: 例如 1990
      2. 出生月份: 例如 5
      3. 出生日期: 例如 15
      4. 出生时辰: 请尽量精确到小时(0-23)，例如 14
      5. 性别: 男/女
      请提供您的出生信息。

用户: 1990年5月15日下午3点，男

助手: 正在为您排盘和分析...
      [系统自动执行八字排盘和 RAG 检索]
      [进行命理分析]

      【命理分析结果】
      ... [详细分析内容] ...
```

### 方法二：直接使用 Python 工具

#### 八字排盘

```python
from bazi_paipan import BaziPaipan

paipan = BaziPaipan()
result = paipan.paipan(1990, 5, 15, 15, is_lunar=False, gender="男")

print("八字:", result["bazi_string"])
print("五行:", result["wuxing"])
print("十神:", result["shishen_detail"])
```

命令行调用：

```bash
cd sanmingtonghui-skill/scripts
python bazi_paipan.py --year 1990 --month 5 --day 15 --hour 15 --gender 男
```

#### RAG 检索

```python
from rag_retriever import RAGRetriever

retriever = RAGRetriever("sanmingtonghui-skill/data/sanmingtonghui_chunks.json")
results = retriever.retrieve("甲木日主", top_k=5)

for r in results:
    print(f"来源: {r['source']}")
    print(f"相关性: {r['relevance']:.3f}")
    print(f"内容: {r['text'][:100]}...")
```

命令行调用：

```bash
cd sanmingtonghui-skill/scripts
python rag_retriever.py --query "甲木日主" --top_k 5
```

---

## 工具说明

### 1. bazi_paipan.py - 八字排盘工具

**功能**：
- 将出生时间转换为八字
- 计算五行属性统计
- 计算十神关系
- 支持公历和农历输入

**参数说明**：

| 参数 | 类型 | 必须 | 说明 | 示例 |
|------|------|------|------|------|
| `--year` | int | 是 | 公历年份 | 1990 |
| `--month` | int | 是 | 月份 (1-12) | 1 |
| `--day` | int | 是 | 日期 (1-31) | 1 |
| `--hour` | int | 是 | 小时 (0-23) | 12 |
| `--gender` | str | 是 | 性别 | 男/女 |
| `--lunar` | flag | 否 | 表示输入为农历时间 | --lunar |

**输出示例**：

```json
{
  "bazi": {
    "year": {"gan": "庚", "zhi": "午", "gan_wuxing": "金", "zhi_wuxing": "火"},
    "month": {"gan": "辛", "zhi": "丑", "gan_wuxing": "金", "zhi_wuxing": "土"},
    "day": {"gan": "丙", "zhi": "申", "gan_wuxing": "火", "zhi_wuxing": "金"},
    "hour": {"gan": "甲", "zhi": "午", "gan_wuxing": "木", "zhi_wuxing": "火"}
  },
  "bazi_string": "庚午 辛丑 丙申 甲午",
  "wuxing": {"木": 1, "火": 3, "土": 2, "金": 2, "水": 0},
  "shishen_detail": {...}
}
```

### 2. rag_retriever.py - RAG 检索工具

**功能**：
- 基于 Embedding 的语义检索
- 基于关键词的回退检索
- 自动提取八字关键词（天干、地支、五行、十神）
- 八字信息检索

**参数说明**：

| 参数 | 类型 | 必须 | 说明 | 示例 |
|------|------|------|------|------|
| `--query` | str | 是 | 查询文本 | 甲木日主 |
| `--top_k` | int | 否 | 返回结果数量，默认5 | 5 |
| `--kb_path` | str | 否 | 知识库路径 | ../data/sanmingtonghui_chunks.json |

**输出示例**：

```json
[
  {
    "text": "甲木喜用丁火，丙火次之。...甲木参天，脱胎要火...",
    "source": "卷四·论甲木",
    "relevance": 0.892,
    "chunk_id": 156
  }
]
```

### 3. init_knowledge_base.py - 知识库初始化脚本

**功能**：
- 加载《三命通会》原始文本
- 按卷和章节智能分块
- 使用 sentence-transformers 计算 Embedding
- 保存为 JSON 格式知识库

**参数说明**：

| 参数 | 类型 | 必须 | 说明 | 示例 |
|------|------|------|------|------|
| `--input` | str | 否 | 输入文本文件路径 | ../../sanmingtonghui.txt |
| `--output` | str | 否 | 输出 JSON 文件路径 | ../data/sanmingtonghui_chunks.json |
| `--model` | str | 否 | Embedding 模型名称 | paraphrase-multilingual-MiniLM-L12-v2 |

---

## 项目结构

```
sanmingtonghui-skill/
├── SKILL.md                              # Skill 完整说明文档
├── README.md                             # 项目说明文档（本文档）
├── sanmingtonghui.txt                    # 《三命通会》原始文本
│
├── scripts/                              # Python 工具脚本
│   ├── __init__.py
│   ├── bazi_paipan.py                   # 八字排盘工具
│   ├── rag_retriever.py                  # RAG 检索工具
│   ├── init_knowledge_base.py            # 知识库初始化脚本
│   ├── requirements.txt                  # Python 依赖
│   ├── test_bazi_paipan.py              # 八字排盘测试
│   ├── test_rag_retriever.py             # RAG 检索测试
│   └── __pycache__/                      # Python 缓存目录
│
├── data/                                 # 知识库数据
│   ├── .gitkeep
│   └── sanmingtonghui_chunks.json       # 《三命通会》分块知识库
│
└── references/                           # 参考资料
    └── bazi_guide.md                    # 八字基础知识参考文档
```

---

## 依赖说明

### Python 包依赖

| 包名 | 版本要求 | 功能说明 |
|------|---------|---------|
| lunar_python | >=1.8.0 | 农历和八字计算，支撑八字排盘功能 |
| sentence-transformers | >=2.2.0 | Embedding 模型，用于语义检索 |
| numpy | >=1.24.0 | 数值计算，向量运算 |

### 模型说明

默认使用 Embedding 模型：`paraphrase-multilingual-MiniLM-L12-v2`

- 模型大小：约 500MB
- 支持语言：50+ 语言（包括中文）
- 特点：体积小、速度快、效果好

---

## 注意事项

### 1. 信息准确性

- **时间准确性**：八字排盘依赖准确的出生时间，误差可能导致八字完全错误
- **公历/农历区分**：必须确认用户提供的是公历还是农历时间
- **真太阳时**：中国幅员辽阔，高质量分析需考虑真太阳时（东部和西部存在时差）
- **性别区分**：大运起运规则男女不同，必须确认性别

### 2. 分析判断

- **综合判断**：命理分析需综合考量多个因素，不可单凭一点下结论
- **原文为据**：所有分析结论必须引用《三命通会》原文作为依据
- **用神取法**：用神的取法有多种，应根据具体命局灵活判断
- **大运流年**：应结合大运和流年进行动态分析

### 3. 结果表达

- **语言得体**：分析语言应专业但温和，不可危言耸听
- **积极引导**：即使命局有不足，也应给出改善建议
- **明确说明**：分析仅供参考，不可作为重大决策的唯一依据
- **保护隐私**：不泄露用户提供的任何个人信息

### 4. 伦理规范

- **适度分析**：命理分析应适度，不可过度依赖
- **正向引导**：引导用户积极面对命运，而非消极等待
- **专业边界**：命理分析仅供参考，不可替代专业咨询（如医疗、法律等）
- **文化传承**：尊重命理文化传统，传承中华智慧

### 5. 技术限制

- 知识库中的 Embedding 向量需要首次运行时计算
- 网络不稳定时模型下载可能失败
- 复杂的命理判断（如大运流年）需要更深入的专业分析

---

## 参考资料

### 典籍

- **《三命通会》** - 明·万民英 撰
  - 中国古代命理学的集大成之作
  - 详细论述了八字命理的理论和应用
  - 被广泛认为是命理学的重要参考文献

### 技术参考

- **lunar_python**: https://github.com/goyiya/lunar-python
  - Python 农历库，支持八字排盘
- **sentence-transformers**: https://github.com/UKPLab/sentence-transformers
  - Sentence Embedding 模型库

### 相关文档

- `SKILL.md` - 完整的 Skill 技术文档
- `references/bazi_guide.md` - 八字基础知识参考
- `scripts/bazi_paipan.py` - 八字排盘工具源码
- `scripts/rag_retriever.py` - RAG 检索工具源码

---

## 后续扩展

本 Skill 可扩展的方向：

1. **增加大运流年计算**：完善大运起运和流年分析
2. **增加神煞判断**：自动判断命中的吉神凶煞
3. **增加命宫胎元**：补充命宫、胎元、身宫分析
4. **增加合盘分析**：姻缘合盘、合伙合盘等
5. **增加择日系统**：更精确的吉日选择
6. **增加风水参考**：结合命理的风水建议

---

*本 Skill 基于《三命通会》制作，传承中华命理智慧，供有缘人参悟人生。*
