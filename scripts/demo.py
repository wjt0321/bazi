#!/usr/bin/env python3
"""
《三命通会》智能命理 Agent - 演示脚本
模拟完整的命理分析对话流程
"""

import json
from bazi_paipan import BaziPaipan
from rag_retriever import RAGRetriever

def main():
    print("=" * 70)
    print("《三命通会》智能命理 Agent - 演示")
    print("=" * 70)

    # 用户信息
    user_query = "我想算命"
    user_birth_info = {
        "year": 1990,
        "month": 8,
        "day": 15,
        "hour": 14,
        "is_lunar": False,
        "gender": "男"
    }

    print(f"\n【用户】: {user_query}")
    print(f"出生信息: {user_birth_info['year']}年{user_birth_info['month']}月{user_birth_info['day']}日{user_birth_info['hour']}点, {user_birth_info['gender']}")

    # Step 1: 八字排盘
    print("\n" + "-" * 70)
    print("Step 1: 八字排盘")
    print("-" * 70)

    paipan = BaziPaipan()
    bazi_result = paipan.paipan(
        user_birth_info['year'],
        user_birth_info['month'],
        user_birth_info['day'],
        user_birth_info['hour'],
        is_lunar=user_birth_info['is_lunar'],
        gender=user_birth_info['gender']
    )

    print(f"\n八字: {bazi_result['bazi_string']}")
    print(f"日主: {bazi_result['day_gan']} ({bazi_result['day_gan']}属{bazi_result['bazi']['day']['gan_wuxing']})")
    print(f"五行统计: {json.dumps(bazi_result['wuxing'], ensure_ascii=False)}")

    print("\n四柱十神:")
    for pillar, info in bazi_result['shishen_detail'].items():
        pillar_name = {"year_shishen": "年柱", "month_shishen": "月柱",
                      "day_shishen": "日柱", "hour_shishen": "时柱"}[pillar]
        print(f"  {pillar_name} {info['gan']}{info['zhi']}: {info['shishen_full']}")

    # Step 2: RAG 检索
    print("\n" + "-" * 70)
    print("Step 2: 检索《三命通会》相关原文")
    print("-" * 70)

    retriever = RAGRetriever('../data/sanmingtonghui_chunks.json')

    day_gan = bazi_result['day_gan']
    month_zhi = bazi_result['bazi']['month']['zhi']

    search_queries = [
        f"{day_gan}水日主",
        f"{day_gan}日主生在{month_zhi}月",
        "壬水"
    ]

    all_results = []
    for query in search_queries:
        print(f"\n检索: {query}")
        results = retriever.retrieve(query, top_k=2)
        all_results.extend(results)

    # 去重
    seen_ids = set()
    unique_results = []
    for r in all_results:
        if r['chunk_id'] not in seen_ids:
            seen_ids.add(r['chunk_id'])
            unique_results.append(r)

    print(f"\n找到 {len(unique_results)} 个相关原文")

    # Step 3: 整合分析
    print("\n" + "-" * 70)
    print("Step 3: 命理分析（基于《三命通会》）")
    print("-" * 70)

    analysis = f"""
根据《三命通会》的理论，对命主进行如下分析：

【八字信息】
八字：{bazi_result['bazi_string']}
日主：{day_gan}水
月令：{month_zhi}

【五行分析】
{json.dumps(bazi_result['wuxing'], ensure_ascii=False)}

五行缺水，命局偏枯。《三命通会》云："壬水属阳，乃甘泽长流之水，能滋生草木，长养万物。独喜春夏生人，秋冬值令，则无生意。"

【十神分析】
年柱偏印，月柱食神，日柱比肩，时柱偏财。

【初步判断】
1. 日主壬水，生于申月，金水旺盛，身旺
2. 喜木火土为用，忌金水过多
3. 时柱带偏财，有财运
4. 食神透出，聪明才智

【建议】
1. 宜从事与木火相关的行业
2. 东方、南方运势较好
3. 忌金水旺地
"""

    print(analysis)

    # 输出参考原文
    print("\n【参考原文】")
    for i, result in enumerate(unique_results[:2], 1):
        print(f"\n{i}. 来源: {result['source']}")
        print(f"   相关性: {result['relevance']:.2f}")
        print(f"   内容: {result['text'][:200]}...")

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()
