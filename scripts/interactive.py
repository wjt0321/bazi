#!/usr/bin/env python3
"""
《三命通会》智能命理 Agent - 交互式界面（零依赖版本）

功能：
- 收集用户出生信息
- 调用八字排盘工具
- 从知识库检索相关原文
- 输出结构化结果，供 Claude 进行白话解释
"""

import json
import sys
from bazi_paipan import BaziPaipan
from rag_retriever import RAGRetriever


def print_banner():
    print("\n" + "=" * 70)
    print("《三命通会》智能命理 Agent")
    print("=" * 70)


def get_birth_info():
    print("\n请输入出生信息：")
    try:
        year = int(input("年份 (如 1990): "))
        month = int(input("月份 (1-12): "))
        day = int(input("日期 (1-31): "))
        hour = int(input("时间 (0-23，如 14): "))
        gender = input("性别 (男/女，默认男): ").strip() or "男"
        is_lunar = input("是否农历 (y/n，默认n): ").strip().lower() == "y"

        return {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "is_lunar": is_lunar,
            "gender": gender
        }
    except ValueError:
        print("输入格式错误，请重新运行！")
        return None


def display_bazi(bazi_result):
    print("\n" + "-" * 70)
    print("【八字排盘结果】")
    print("-" * 70)

    print(f"\n八字: {bazi_result['bazi_string']}")
    print(f"日主: {bazi_result['day_gan']} ({bazi_result['bazi']['day']['gan_wuxing']})")
    print(f"日支: {bazi_result['day_zhi']}")

    print("\n【五行统计】")
    wuxing = bazi_result['wuxing']
    for element, count in wuxing.items():
        print(f"  {element}: {count}")

    print("\n【十神关系】")
    for pillar, info in bazi_result['shishen_detail'].items():
        pillar_name = {"year_shishen": "年柱", "month_shishen": "月柱",
                      "day_shishen": "日柱", "hour_shishen": "时柱"}[pillar]
        print(f"  {pillar_name}: {info['gan']}{info['zhi']} - {info['shishen_full']}")

    print(f"\n【出生信息】")
    print(f"  公历: {bazi_result['meta']['solar_date']}")
    print(f"  农历: {bazi_result['meta']['lunar_date']}")
    print(f"  性别: {bazi_result['meta']['gender']}")


def display_retrieval(results):
    print("\n" + "-" * 70)
    print("【《三命通会》相关原文】")
    print("-" * 70)

    if not results:
        print("未找到相关原文")
        return

    for i, result in enumerate(results[:3], 1):
        print(f"\n[{i}] {result['source']}")
        print(f"    相关性: {result['relevance']:.2f}")
        print(f"    内容: {result['text'][:400]}...")


def display_analysis(bazi_result, retrieved_results):
    """
    输出分析所需的结构化数据，供 Claude 进行白话解释。
    本函数不输出固定结论，而是呈现原始信息。
    """
    print("\n" + "-" * 70)
    print("【命理分析数据（供 AI 白话解释）】")
    print("-" * 70)

    day_gan = bazi_result['day_gan']
    month_zhi = bazi_result['bazi']['month']['zhi']
    wuxing = bazi_result['wuxing']
    shishen = bazi_result['shishen_detail']

    print(f"\n【日主】{day_gan}（{bazi_result['bazi']['day']['gan_wuxing']}）")
    print(f"【月令】{month_zhi}（{bazi_result['bazi']['month']['zhi_wuxing']}）")
    print(f"【五行分布】{json.dumps(wuxing, ensure_ascii=False)}")

    print("\n【十神配置】")
    for pillar, info in shishen.items():
        pillar_name = {"year_shishen": "年柱", "month_shishen": "月柱",
                      "day_shishen": "日柱", "hour_shishen": "时柱"}[pillar]
        print(f"  {pillar_name}: {info['shishen_full']}（{info['gan']}{info['zhi']}）")

    if retrieved_results:
        print("\n【检索到的《三命通会》原文片段】")
        for i, r in enumerate(retrieved_results[:3], 1):
            print(f"\n  [{i}] 来源: {r['source']}")
            print(f"      {r['text'][:300]}...")

    print("\n" + "-" * 70)
    print("【请 Claude 基于以上数据进行白话命理解释】")
    print("-" * 70)


def main():
    print_banner()

    # 初始化工具
    try:
        paipan = BaziPaipan()
        retriever = RAGRetriever('../data/sanmingtonghui_chunks.json')
    except Exception as e:
        print(f"初始化错误: {e}")
        return

    # 获取出生信息
    birth_info = get_birth_info()
    if not birth_info:
        return

    # 八字排盘
    try:
        bazi_result = paipan.paipan(
            birth_info['year'],
            birth_info['month'],
            birth_info['day'],
            birth_info['hour'],
            is_lunar=birth_info['is_lunar'],
            gender=birth_info['gender']
        )

        if 'error' in bazi_result:
            print(f"排盘错误: {bazi_result['error']}")
            return

        display_bazi(bazi_result)

    except Exception as e:
        print(f"排盘出错: {e}")
        return

    # RAG 检索
    try:
        day_gan = bazi_result['day_gan']
        month_zhi = bazi_result['bazi']['month']['zhi']

        # 多个检索词
        queries = [
            f"{day_gan}日主",
            f"{day_gan}生{month_zhi}月",
            f"{day_gan}"
        ]

        all_results = []
        for query in queries:
            results = retriever.retrieve(query, top_k=2)
            all_results.extend(results)

        # 去重
        seen = set()
        unique_results = []
        for r in all_results:
            if r['chunk_id'] not in seen:
                seen.add(r['chunk_id'])
                unique_results.append(r)

        unique_results.sort(key=lambda x: x['relevance'], reverse=True)

        display_retrieval(unique_results)

    except Exception as e:
        print(f"检索出错: {e}")
        unique_results = []

    # 显示分析数据
    display_analysis(bazi_result, unique_results if 'unique_results' in locals() else [])

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
