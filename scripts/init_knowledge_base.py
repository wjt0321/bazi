"""
《三命通会》知识库初始化脚本（零依赖版本）

功能：
- 加载《三命通会》原始文本
- 按卷和章节进行智能分块
- 保存为 JSON 格式知识库（不含 Embedding，纯文本分块）

使用方法：
    python init_knowledge_base.py
    python init_knowledge_base.py --input ../../workspace/sanmingtonghui.txt --output ../data/sanmingtonghui_chunks.json
"""

import json
import os
import re
from typing import List, Dict, Any


class KnowledgeBaseInitializer:
    """
    《三命通会》知识库初始化器

    负责：
    1. 加载原始文本文件
    2. 按卷和章节智能分块
    3. 保存知识库为 JSON 格式（纯文本，无 Embedding）
    """

    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []

    def load_text(self, file_path: str) -> str:
        """
        加载《三命通会》原始文本文件

        Args:
            file_path: 文本文件路径

        Returns:
            str: 文件内容

        Raises:
            FileNotFoundError: 文件不存在时抛出异常
            IOError: 读取文件失败时抛出异常
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文本文件不存在: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content

    def parse_text(self, text: str) -> List[Dict[str, Any]]:
        """
        解析文本，按卷和章节进行智能分块

        《三命通会》文本结构：
        - 卷标题：卷一、卷二、...、卷十二
        - 章节标题：○论五行生成、○总论纳音 等

        分块策略：
        - 每个章节作为一个独立的 chunk
        - 保留卷名和章节名作为元数据
        - 合并同一章节内的所有内容行

        Args:
            text: 原始文本内容

        Returns:
            List[Dict]: 分块后的文本块列表，每个块包含：
                - volume: 卷名
                - chapter: 章节名
                - content: 合并后的内容
        """
        chunks: List[Dict[str, Any]] = []

        lines = text.split('\n')
        current_volume = ""
        current_chapter = ""
        current_content: List[str] = []

        # 正则表达式匹配卷标题：卷一、卷二、卷十二 等
        volume_pattern = re.compile(r'^卷[一二三四五六七八九十百零]+')

        # 正则表达式匹配章节标题：○论五行生成、○总论纳音 等
        chapter_pattern = re.compile(r'^○(.+)')

        for line in lines:
            line = line.strip()

            # 跳过空行
            if not line:
                continue

            # 检测卷标题
            if volume_pattern.match(line):
                # 保存前一个章节块（如果有内容）
                if current_content:
                    chunks.append({
                        "volume": current_volume,
                        "chapter": current_chapter,
                        "content": '\n'.join(current_content)
                    })
                    current_content = []

                # 更新当前卷
                current_volume = line
                current_chapter = ""
                continue

            # 检测章节标题
            match = chapter_pattern.match(line)
            if match:
                # 保存前一个章节块（如果有内容）
                if current_content:
                    chunks.append({
                        "volume": current_volume,
                        "chapter": current_chapter,
                        "content": '\n'.join(current_content)
                    })
                    current_content = []

                # 更新当前章节
                current_chapter = match.group(1)
                current_content.append(line)
                continue

            # 普通内容行，归入当前卷/章节
            if current_volume:
                current_content.append(line)

        # 保存最后一个章节块（如果有内容）
        if current_content:
            chunks.append({
                "volume": current_volume,
                "chapter": current_chapter,
                "content": '\n'.join(current_content)
            })

        return chunks

    def save_knowledge_base(
        self,
        chunks: List[Dict[str, Any]],
        output_path: str
    ) -> None:
        """
        保存知识库为 JSON 格式文件

        JSON 结构：
        {
            "chunks": [...],
            "total_chunks": 数量
        }

        Args:
            chunks: 文本块列表
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"保存知识库到: {output_path}")

        # 为每个 chunk 添加 chunk_id
        for i, chunk in enumerate(chunks):
            chunk["chunk_id"] = i

        # 构建输出数据
        output_data = {
            "chunks": chunks,
            "total_chunks": len(chunks)
        }

        # 保存为 JSON 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"保存完成! 共 {len(chunks)} 个文本块")

    def init(self, text_file: str, output_file: str) -> List[Dict[str, Any]]:
        """
        初始化知识库的主函数

        执行完整流程：
        1. 加载文本文件
        2. 解析文本并分块
        3. 保存知识库

        Args:
            text_file: 输入文本文件路径
            output_file: 输出 JSON 文件路径

        Returns:
            List[Dict]: 处理后的文本块列表
        """
        print("=" * 60)
        print("《三命通会》知识库初始化工具（零依赖版本）")
        print("=" * 60)

        # 步骤 1: 加载文本
        print(f"\n[1/3] 加载文本文件: {text_file}")
        text = self.load_text(text_file)
        print(f"    文本长度: {len(text):,} 字符")

        # 步骤 2: 解析文本
        print(f"\n[2/3] 解析文本并分块...")
        chunks = self.parse_text(text)
        print(f"    解析完成! 共 {len(chunks)} 个文本块")

        # 打印分块统计
        volumes = set(chunk["volume"] for chunk in chunks if chunk["volume"])
        print(f"    涉及卷数: {len(volumes)}")
        print(f"    涉及章节数: {sum(1 for chunk in chunks if chunk['chapter'])}")

        # 步骤 3: 保存知识库
        print(f"\n[3/3] 保存知识库...")
        self.save_knowledge_base(chunks, output_file)

        print("\n" + "=" * 60)
        print("知识库初始化完成!")
        print("=" * 60)

        return chunks


def main():
    """
    命令行入口函数

    支持参数：
    - --input: 输入文本文件路径（默认 ../../workspace/sanmingtonghui.txt）
    - --output: 输出 JSON 文件路径（默认 ../data/sanmingtonghui_chunks.json）
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='《三命通会》知识库初始化工具（零依赖版本）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python init_knowledge_base.py
  python init_knowledge_base.py --input ../../workspace/sanmingtonghui.txt
  python init_knowledge_base.py --output ./data/kb.json
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        default='../../workspace/sanmingtonghui.txt',
        help='输入文本文件路径（默认: ../../workspace/sanmingtonghui.txt）'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='../data/sanmingtonghui_chunks.json',
        help='输出 JSON 文件路径（默认: ../data/sanmingtonghui_chunks.json）'
    )

    args = parser.parse_args()

    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 处理相对路径
    input_path = args.input
    if not os.path.isabs(input_path):
        input_path = os.path.join(script_dir, input_path)

    output_path = args.output
    if not os.path.isabs(output_path):
        output_path = os.path.join(script_dir, output_path)

    # 验证输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误: 找不到文本文件 {input_path}")
        print("请确保《三命通会》文本文件存在，或使用 --input 参数指定正确路径")
        exit(1)

    # 创建初始化器并执行
    initializer = KnowledgeBaseInitializer()
    chunks = initializer.init(input_path, output_path)

    # 打印知识库统计信息
    print(f"\n知识库统计:")
    print(f"  - 总文本块数: {len(chunks)}")

    # 统计各卷的章节数
    volume_stats: Dict[str, int] = {}
    for chunk in chunks:
        vol = chunk.get("volume", "未知")
        volume_stats[vol] = volume_stats.get(vol, 0) + 1

    print(f"  - 卷数: {len(volume_stats)}")

    # 打印前 5 个文本块的信息
    print(f"\n前 5 个文本块预览:")
    for i, chunk in enumerate(chunks[:5]):
        vol = chunk.get("volume", "无卷名")
        ch = chunk.get("chapter", "无章节名")
        content_preview = chunk["content"][:50].replace('\n', ' ')
        print(f"  [{i}] {vol}·{ch}")
        print(f"      内容: {content_preview}...")


if __name__ == "__main__":
    main()
