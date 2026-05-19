"""
《三命通会》RAG 检索工具测试文件

测试用例覆盖:
1. 知识库加载
2. 基础语义检索
3. 关键词检索（回退模式）
4. 八字信息检索
5. 关键词提取
6. 余弦相似度计算
"""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from rag_retriever import RAGRetriever


class TestRAGRetriever(unittest.TestCase):
    """RAGRetriever 类的单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化，加载知识库"""
        kb_path = os.path.join(script_dir, '../data/sanmingtonghui_chunks.json')

        if os.path.exists(kb_path):
            cls.retriever = RAGRetriever(kb_path)
            cls.has_knowledge_base = True
        else:
            cls.retriever = RAGRetriever()
            cls.has_knowledge_base = False
            print(f"\n警告: 知识库文件不存在: {kb_path}")
            print("部分测试将被跳过")

    def test_initialization(self):
        """测试 RAGRetriever 初始化"""
        retriever = RAGRetriever()

        self.assertIsInstance(retriever.chunks, list)
        self.assertEqual(len(retriever.chunks), 0)

    def test_initialization_with_path(self):
        """测试带路径的初始化"""
        kb_path = os.path.join(script_dir, '../data/sanmingtonghui_chunks.json')

        if self.has_knowledge_base:
            retriever = RAGRetriever(kb_path)
            self.assertGreater(len(retriever.chunks), 0)

    def test_load_knowledge_base(self):
        """测试知识库加载"""
        kb_path = os.path.join(script_dir, '../data/sanmingtonghui_chunks.json')

        if not self.has_knowledge_base:
            self.skipTest("知识库文件不存在")

        retriever = RAGRetriever()
        result = retriever.load_knowledge_base(kb_path)

        self.assertTrue(result)
        self.assertGreater(len(retriever.chunks), 0)

    def test_load_knowledge_base_invalid_path(self):
        """测试加载不存在的文件"""
        retriever = RAGRetriever()
        result = retriever.load_knowledge_base('/nonexistent/path.json')

        self.assertFalse(result)
        self.assertEqual(len(retriever.chunks), 0)

    def test_search_by_keywords_basic(self):
        """测试关键词检索基础功能"""
        retriever = RAGRetriever()
        # 使用空知识库测试，应返回空列表
        results = retriever._search_by_keywords("甲木", top_k=3)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

    def test_extract_keywords(self):
        """测试关键词提取"""
        retriever = RAGRetriever()

        keywords = retriever._extract_keywords("甲木日主生在寅月")
        self.assertIn("天干甲", keywords)
        self.assertIn("地支寅", keywords)
        self.assertIn("木", keywords)

        keywords2 = retriever._extract_keywords("壬水日主生在亥月")
        self.assertTrue(any("壬" in k for k in keywords2))
        self.assertTrue(any("亥" in k for k in keywords2))
        self.assertIn("水", keywords2)

    def test_extract_keywords_shishen(self):
        """测试十神关键词提取"""
        retriever = RAGRetriever()

        keywords = retriever._extract_keywords("比肩帮身")
        self.assertIn("比", keywords)

        keywords2 = retriever._extract_keywords("伤官伤夫")
        self.assertIn("伤", keywords2)
        self.assertIn("伤官", keywords2)

    def test_search_by_keywords(self):
        """测试关键词检索"""
        if not self.has_knowledge_base:
            self.skipTest("知识库文件不存在")

        retriever = self.retriever

        results = retriever._search_by_keywords("五行生克", top_k=3)

        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 3)

        for result in results:
            self.assertIn("text", result)
            self.assertIn("source", result)
            self.assertIn("relevance", result)
            self.assertIn("chunk_id", result)
            self.assertGreater(result["relevance"], 0)

    @unittest.skipUnless(
        os.path.exists(os.path.join(script_dir, '../data/sanmingtonghui_chunks.json')),
        "需要预计算的知识库"
    )
    def test_retrieve(self):
        """测试基础检索功能"""
        retriever = self.retriever

        results = retriever.retrieve("甲木日主生在寅月", top_k=3)

        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 3)

        for result in results:
            self.assertIn("text", result)
            self.assertIn("source", result)
            self.assertIn("relevance", result)
            self.assertIn("chunk_id", result)
            self.assertIsInstance(result["text"], str)
            self.assertGreater(len(result["text"]), 0)

    @unittest.skipUnless(
        os.path.exists(os.path.join(script_dir, '../data/sanmingtonghui_chunks.json')),
        "需要预计算的知识库"
    )
    def test_retrieve_no_results(self):
        """测试无结果检索"""
        retriever = self.retriever

        results = retriever.retrieve("xyz123完全不相关的内容", top_k=5)

        self.assertIsInstance(results, list)

    def test_retrieve_empty_knowledge_base(self):
        """测试空知识库检索"""
        retriever = RAGRetriever()

        results = retriever.retrieve("测试查询", top_k=5)

        self.assertEqual(results, [])

    @unittest.skipUnless(
        os.path.exists(os.path.join(script_dir, '../data/sanmingtonghui_chunks.json')),
        "需要预计算的知识库"
    )
    def test_retrieve_by_bazi(self):
        """测试八字信息检索"""
        retriever = self.retriever

        bazi_info = {
            "bazi": {
                "year": {"gan": "庚", "zhi": "午"},
                "month": {"gan": "辛", "zhi": "丑"},
                "day": {"gan": "丙", "zhi": "申"},
                "hour": {"gan": "甲", "zhi": "午"}
            },
            "wuxing": {"木": 1, "火": 3, "土": 2, "金": 2, "水": 1}
        }

        results = retriever.retrieve_by_bazi(bazi_info, top_k=3)

        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 3)

        for result in results:
            self.assertIn("text", result)
            self.assertIn("source", result)
            self.assertIn("relevance", result)

    def test_retrieve_by_bazi_empty(self):
        """测试空八字信息检索"""
        if not self.has_knowledge_base:
            self.skipTest("知识库文件不存在")

        retriever = self.retriever

        results = retriever.retrieve_by_bazi({}, top_k=5)

        self.assertIsInstance(results, list)

    def test_get_chunks_info(self):
        """测试知识库信息获取"""
        if not self.has_knowledge_base:
            self.skipTest("知识库文件不存在")

        retriever = self.retriever

        info = retriever.get_chunks_info()

        self.assertIn("total_chunks", info)
        self.assertGreater(info["total_chunks"], 0)

    def test_get_chunks_info_empty(self):
        """测试空知识库信息获取"""
        retriever = RAGRetriever()

        info = retriever.get_chunks_info()

        self.assertEqual(info["total_chunks"], 0)

    def test_get_gan_wuxing(self):
        """测试天干五行映射"""
        retriever = RAGRetriever()

        self.assertEqual(retriever._get_gan_wuxing("甲"), "木")
        self.assertEqual(retriever._get_gan_wuxing("丙"), "火")
        self.assertEqual(retriever._get_gan_wuxing("戊"), "土")
        self.assertEqual(retriever._get_gan_wuxing("庚"), "金")
        self.assertEqual(retriever._get_gan_wuxing("壬"), "水")
        self.assertIsNone(retriever._get_gan_wuxing("X"))

    def test_constants(self):
        """测试常量定义"""
        retriever = RAGRetriever()

        self.assertEqual(len(retriever.TIAN_GAN), 10)
        self.assertEqual(len(retriever.DI_ZHI), 12)
        self.assertEqual(len(retriever.WU_XING), 5)
        self.assertEqual(len(retriever.SHI_SHEN), 10)


class TestRAGRetrieverIntegration(unittest.TestCase):
    """集成测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        kb_path = os.path.join(script_dir, '../data/sanmingtonghui_chunks.json')

        if os.path.exists(kb_path):
            cls.retriever = RAGRetriever(kb_path)
            cls.has_knowledge_base = True
        else:
            cls.retriever = None
            cls.has_knowledge_base = False

    @unittest.skipUnless(
        os.path.exists(os.path.join(script_dir, '../data/sanmingtonghui_chunks.json')),
        "需要预计算的知识库"
    )
    def test_end_to_end_retrieval(self):
        """端到端检索测试"""
        retriever = self.retriever

        query = "论五行生克"
        results = retriever.retrieve(query, top_k=3)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 3)

        result = results[0]
        self.assertIn("text", result)
        self.assertIn("source", result)
        self.assertIn("relevance", result)
        self.assertIn("chunk_id", result)

        self.assertIn("五行", result["text"] or "生克" in result["text"])

    @unittest.skipUnless(
        os.path.exists(os.path.join(script_dir, '../data/sanmingtonghui_chunks.json')),
        "需要预计算的知识库"
    )
    def test_output_format(self):
        """测试输出格式符合规范"""
        retriever = self.retriever

        results = retriever.retrieve("甲木", top_k=1)

        if len(results) > 0:
            result = results[0]

            self.assertIsInstance(result["text"], str)
            self.assertIsInstance(result["source"], str)
            self.assertIsInstance(result["relevance"], float)
            self.assertIsInstance(result["chunk_id"], int)

            self.assertGreaterEqual(result["relevance"], 0.0)
            self.assertLessEqual(result["relevance"], 1.0)


def run_basic_tests():
    """运行基础功能测试（无需知识库）"""
    print("\n" + "=" * 60)
    print("运行基础功能测试")
    print("=" * 60)

    retriever = RAGRetriever()

    print("\n1. 测试初始化...")
    assert isinstance(retriever.chunks, list)
    print("   ✓ 初始化正常")

    print("\n2. 测试关键词检索（空知识库）...")
    results = retriever._search_by_keywords("甲木", top_k=3)
    assert isinstance(results, list)
    assert len(results) == 0
    print("   ✓ 空知识库检索返回空列表")

    print("\n3. 测试关键词提取...")
    keywords = retriever._extract_keywords("甲木日主生在寅月")
    print(f"   查询: 甲木日主生在寅月")
    print(f"   提取关键词: {keywords}")
    assert "甲" in keywords or "木" in keywords
    print("   ✓ 关键词提取正常")

    print("\n4. 测试天干五行映射...")
    assert retriever._get_gan_wuxing("甲") == "木"
    assert retriever._get_gan_wuxing("丙") == "火"
    print("   ✓ 天干五行映射正常")

    print("\n" + "=" * 60)
    print("基础功能测试完成!")
    print("=" * 60)


def run_full_tests():
    """运行完整测试套件"""
    print("\n" + "=" * 60)
    print("运行完整测试套件")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestRAGRetriever))
    suite.addTests(loader.loadTestsFromTestCase(TestRAGRetrieverIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ 所有测试通过!")
    else:
        print("✗ 部分测试失败")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RAG 检索工具测试")
    parser.add_argument(
        '--basic',
        action='store_true',
        help='仅运行基础功能测试（无需知识库）'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='运行完整测试套件'
    )

    args = parser.parse_args()

    if args.basic:
        run_basic_tests()
    elif args.full:
        run_full_tests()
    else:
        run_basic_tests()

        if os.path.exists(os.path.join(script_dir, '../data/sanmingtonghui_chunks.json')):
            print("\n")
            response = input("是否运行完整测试套件（包括需要知识库的测试）? (y/n): ")
            if response.lower() == 'y':
                run_full_tests()
        else:
            print("\n提示: 知识库文件不存在，跳过完整测试")
            print("如需运行完整测试，请先运行 init_knowledge_base.py 初始化知识库")
