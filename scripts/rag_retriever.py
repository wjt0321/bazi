"""
《三命通会》RAG 检索工具（零依赖版本）
基于纯关键词匹配进行检索，无需 Embedding 模型

功能特性:
- 基于关键词的智能检索
- 自动关键词提取（天干、地支、五行、十神）
- 八字信息检索
- 零外部依赖，仅使用 Python 标准库
"""

import json
import os
import sys
import re
from typing import List, Dict, Any, Optional


class RAGRetriever:
    """
    RAG 检索器类，用于从《三命通会》知识库中检索相关内容

    Attributes:
        chunks: 知识库文本块列表
    """

    # 天干列表
    TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

    # 地支列表
    DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 五行列表
    WU_XING = ["木", "火", "土", "金", "水"]

    # 十神列表
    SHI_SHEN = ["比", "劫", "食", "伤", "财", "才", "官", "杀", "枭", "印"]

    # 十神全称映射
    SHI_SHEN_FULL = {
        "比": "比肩", "劫": "劫财",
        "食": "食神", "伤": "伤官",
        "财": "正财", "才": "偏财",
        "官": "正官", "杀": "七杀",
        "枭": "偏印", "印": "正印"
    }

    def __init__(self, knowledge_base_path: Optional[str] = None):
        """
        初始化 RAG 检索器

        Args:
            knowledge_base_path: 知识库文件路径（JSON格式），如果提供则自动加载
        """
        self.chunks: List[Dict[str, Any]] = []

        if knowledge_base_path and os.path.exists(knowledge_base_path):
            self.load_knowledge_base(knowledge_base_path)

    def load_knowledge_base(self, path: str) -> bool:
        """
        加载知识库 JSON 文件

        Args:
            path: 知识库文件路径

        Returns:
            bool: 加载是否成功
        """
        try:
            print(f"加载知识库: {path}", file=sys.stderr)

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.chunks = data.get("chunks", [])

            total = len(self.chunks)
            print(f"加载完成! 共 {total} 个文本块", file=sys.stderr)

            return True

        except FileNotFoundError:
            print(f"错误: 找不到知识库文件: {path}", file=sys.stderr)
            return False
        except json.JSONDecodeError as e:
            print(f"错误: JSON 解析失败: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"错误: 加载知识库失败: {e}", file=sys.stderr)
            return False

    def _extract_keywords(self, query: str) -> List[str]:
        """
        从查询文本中自动提取关键词
        识别天干、地支、五行、十神等命理专有词汇

        Args:
            query: 查询文本

        Returns:
            List[str]: 提取的关键词列表
        """
        keywords = []

        for char in query:
            if char in self.TIAN_GAN:
                keywords.append(f"天干{char}")
            elif char in self.DI_ZHI:
                keywords.append(f"地支{char}")

        for word in self.WU_XING:
            if word in query:
                keywords.append(word)

        for word, full in self.SHI_SHEN_FULL.items():
            if word in query or full in query:
                keywords.append(word)
                keywords.append(full)

        if "日主" in query or "日元" in query:
            keywords.extend(["日主", "日元"])

        if "月令" in query or "月支" in query:
            keywords.extend(["月令", "月支"])

        if "旺" in query or "衰" in query or "强弱" in query:
            keywords.extend(["旺相休囚死", "五行旺相"])

        pattern = re.compile(r'[甲乙丙丁戊己庚辛壬癸]{2,}')
        matches = pattern.findall(query)
        keywords.extend(matches)

        return keywords if keywords else [query]

    def _search_by_keywords(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        基于关键词进行检索

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            List[Dict]: 检索结果列表
        """
        keywords = self._extract_keywords(query)

        scored_chunks = []
        for chunk in self.chunks:
            content = chunk.get("content", "")
            content_lower = content.lower()
            score = 0
            matched_keywords = []

            for keyword in keywords:
                keyword_lower = keyword.lower()
                count = content_lower.count(keyword_lower)
                if count > 0:
                    score += count
                    matched_keywords.append(keyword)

                    if keyword_lower in content_lower[:200]:
                        score += 3

            if score > 0:
                scored_chunks.append((chunk, score, matched_keywords))

        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        results = []
        for chunk, score, matched in scored_chunks[:top_k]:
            source = chunk.get('chapter') or chunk.get('volume', '未知')
            if chunk.get('volume') and chunk.get('chapter'):
                source = f"{chunk['volume']}·{chunk['chapter']}"

            relevance = min(score / 10, 1.0)
            results.append({
                "text": chunk.get("content", ""),
                "source": source,
                "relevance": round(relevance, 4),
                "chunk_id": chunk.get("chunk_id", 0),
                "matched_keywords": matched
            })

        return results

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        检索与查询相关的知识库内容

        Args:
            query: 查询文本
            top_k: 返回结果数量，默认 5

        Returns:
            List[Dict]: 检索结果列表，每项包含:
                - text: 相关内容文本
                - source: 来源（卷·章节）
                - relevance: 相关性分数
                - chunk_id: 文本块 ID
        """
        if not self.chunks:
            print("警告: 知识库未加载", file=sys.stderr)
            return []

        print(f"检索: {query}", file=sys.stderr)

        return self._search_by_keywords(query, top_k)

    def retrieve_by_bazi(self, bazi_info: Dict[str, Any], query: str = "", top_k: int = 5) -> List[Dict[str, Any]]:
        """
        根据八字信息检索相关命理知识

        Args:
            bazi_info: 八字信息字典，应包含:
                - bazi: 八字字典，包含 year, month, day, hour 的 gan/zhi
                - wuxing: 五行计数字典
                - shishen_detail: 十神详情
            query: 额外查询文本（可选）
            top_k: 返回结果数量

        Returns:
            List[Dict[str, Any]]: 检索结果列表
        """
        search_queries = []

        if "bazi" in bazi_info:
            bazi = bazi_info["bazi"]
            day_gan = bazi.get("day", {}).get("gan", "")
            month_zhi = bazi.get("month", {}).get("zhi", "")
            day_zhi = bazi.get("day", {}).get("zhi", "")
            year_zhi = bazi.get("year", {}).get("zhi", "")
            year_gan = bazi.get("year", {}).get("gan", "")
            hour_gan = bazi.get("hour", {}).get("gan", "")

            if day_gan and month_zhi:
                search_queries.append(f"{day_gan}日主生在{month_zhi}月")

            if day_zhi:
                search_queries.append(f"{day_zhi}日坐命")

            if year_gan and year_zhi:
                search_queries.append(f"论{year_gan}{year_zhi}年")

            gan_wuxing = self._get_gan_wuxing(day_gan)
            if gan_wuxing:
                search_queries.append(f"{gan_wuxing}木论")

            search_queries.append(f"{month_zhi}月令")
            search_queries.append(f"论{day_gan}{day_zhi}")

            if hour_gan:
                hour_zhi = bazi.get("hour", {}).get("zhi", "")
                search_queries.append(f"论{day_gan}日{hour_gan}{hour_zhi}时")

        if "wuxing" in bazi_info:
            wuxing = bazi_info["wuxing"]
            total = sum(wuxing.values())

            if total > 0:
                weak_elements = [k for k, v in wuxing.items() if v <= 1]
                strong_elements = [k for k, v in wuxing.items() if v >= 3]

                if weak_elements:
                    search_queries.append(f"{weak_elements[0]}弱")
                    search_queries.append(f"{weak_elements[0]}不足")

                if strong_elements:
                    search_queries.append(f"{strong_elements[0]}旺")
                    search_queries.append(f"{strong_elements[0]}过盛")

        if "shishen_detail" in bazi_info:
            shishen = bazi_info["shishen_detail"]
            for key, value in shishen.items():
                if isinstance(value, dict):
                    shishen_name = value.get("shishen", "")
                    if shishen_name:
                        full_name = self.SHI_SHEN_FULL.get(shishen_name, shishen_name)
                        search_queries.append(f"{full_name}论")

        if query:
            search_queries.append(query)

        print(f"生成检索查询: {search_queries}", file=sys.stderr)

        all_results = []
        seen_chunks = set()

        for sq in search_queries:
            results = self.retrieve(sq, top_k=3)
            for r in results:
                if r["chunk_id"] not in seen_chunks:
                    seen_chunks.add(r["chunk_id"])
                    all_results.append(r)

        all_results.sort(key=lambda x: x["relevance"], reverse=True)

        return all_results[:top_k]

    def _get_gan_wuxing(self, gan: str) -> Optional[str]:
        """
        获取天干的五行属性

        Args:
            gan: 天干字符

        Returns:
            str 或 None: 五行属性
        """
        wuxing_map = {
            "甲": "木", "乙": "木",
            "丙": "火", "丁": "火",
            "戊": "土", "己": "土",
            "庚": "金", "辛": "金",
            "壬": "水", "癸": "水"
        }
        return wuxing_map.get(gan)

    def get_chunks_info(self) -> Dict[str, Any]:
        """
        获取知识库的基本统计信息

        Returns:
            Dict: 包含 chunks 数量、平均长度等信息
        """
        if not self.chunks:
            return {"total_chunks": 0}

        total_length = sum(len(c.get("content", "")) for c in self.chunks)
        volumes = set(c.get("volume", "未知") for c in self.chunks)
        chapters = set(c.get("chapter", "") for c in self.chunks if c.get("chapter"))

        return {
            "total_chunks": len(self.chunks),
            "total_characters": total_length,
            "average_length": total_length // len(self.chunks) if self.chunks else 0,
            "volumes_count": len(volumes),
            "chapters_count": len(chapters)
        }


def main():
    """
    命令行入口函数
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="《三命通会》RAG 检索工具（零依赖版本）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python rag_retriever.py --query "甲木日主生在寅月" --top_k 5
  python rag_retriever.py --query "五行生克" --kb_path ../data/sanmingtonghui_chunks.json
  python rag_retriever.py --info
        """
    )

    parser.add_argument(
        '--query', '-q',
        type=str,
        default=None,
        help='查询文本'
    )
    parser.add_argument(
        '--top_k', '-k',
        type=int,
        default=5,
        help='返回结果数量（默认: 5）'
    )
    parser.add_argument(
        '--kb_path', '-p',
        type=str,
        default='../data/sanmingtonghui_chunks.json',
        help='知识库路径（默认: ../data/sanmingtonghui_chunks.json）'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='显示知识库信息而非执行检索'
    )

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    kb_path = os.path.join(script_dir, args.kb_path)

    retriever = RAGRetriever()

    if not os.path.exists(kb_path):
        print(f"错误: 找不到知识库文件: {kb_path}", file=sys.stderr)
        print(f"提示: 请先运行 init_knowledge_base.py 初始化知识库", file=sys.stderr)
        sys.exit(1)

    retriever.load_knowledge_base(kb_path)

    if args.info:
        info = retriever.get_chunks_info()
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return

    if not args.query:
        parser.print_help()
        print("\n错误: --query 是必需参数（除非使用 --info）", file=sys.stderr)
        sys.exit(1)

    results = retriever.retrieve(args.query, top_k=args.top_k)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
