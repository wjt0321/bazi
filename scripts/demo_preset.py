#!/usr/bin/env python3
"""
《三命通会》智能命理 Agent - 预设演示
使用预设数据演示完整功能
"""

import json
from bazi_paipan import BaziPaipan
from rag_retriever import RAGRetriever

def print_banner():
    print("\n" + "=" * 70)
    print("《三命通会》智能命理 Agent - 预设演示")
    print("=" * 70)

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
    print("\n" + "-" * 70)
    print("【命理分析（基于《三命通会》）】")
    print("-" * 70)

    day_gan = bazi_result['day_gan']
    day_gan_wuxing = bazi_result['bazi']['day']['gan_wuxing']
    month_zhi = bazi_result['bazi']['month']['zhi']
    wuxing = bazi_result['wuxing']

    # 根据日主五行生成分析
    wuxing_description = {
        "木": "甲乙木，其性直，其情和，其味酸，其色青。",
        "火": "丙丁火，其性急，其情恭，其味苦，其色赤。",
        "土": "戊己土，其性重，其情厚，其味甘，其色黄。",
        "金": "庚辛金，其性刚，其情烈，其味辛，其色白。",
        "水": "壬癸水，其性聪，其情善，其味咸，其色黑。"
    }

    analysis = f"""
【基本格局】
日干{day_gan}属{day_gan_wuxing}，生于{month_zhi}月。

【五行分布】
{json.dumps(wuxing, ensure_ascii=False, indent=2)}

【《三命通会》要点】
{wuxing_description.get(day_gan_wuxing, '')}

【初步判断】
1. 日干{day_gan}{day_gan_wuxing}，看月令得令与否
2. 五行{max(wuxing.items(), key=lambda x: x[1])[0]}偏旺，{min(wuxing.items(), key=lambda x: x[1])[0]}偏弱
3. 需结合大运流年来看运势走向

【注意】
以上分析仅供参考，不可作为重大决策的唯一依据。
命理之说，古已有之，但需理性对待，结合实际情况灵活判断。
"""

    print(analysis)

def main():
    print_banner()

    # 预设数据
    preset_info = {
        "year": 1988,
        "month": 5,
        "day": 20,
        "hour": 10,
        "is_lunar": False,
        "gender": "男"
    }

    print("\n【预设出生信息】")
    print(f"年份: {preset_info['year']}")
    print(f"月份: {preset_info['month']}")
    print(f"日期: {preset_info['day']}")
    print(f"时间: {preset_info['hour']}")
    print(f"性别: {preset_info['gender']}")
    print(f"农历: {'是' if preset_info['is_lunar'] else '否'}")

    # 初始化工具
    print("\n正在初始化...")
    paipan = BaziPaipan()
    retriever = RAGRetriever('../data/sanmingtonghui_chunks.json')

    # Step 1: 八字排盘
    print("\n正在排盘...")
    bazi_result = paipan.paipan(
        preset_info['year'],
        preset_info['month'],
        preset_info['day'],
        preset_info['hour'],
        is_lunar=preset_info['is_lunar'],
        gender=preset_info['gender']
    )

    if 'error' in bazi_result:
        print(f"排盘错误: {bazi_result['error']}")
        return

    display_bazi(bazi_result)

    # Step 2: RAG 检索
    print("\n正在检索《三命通会》...")
    day_gan = bazi_result['day_gan']
    month_zhi = bazi_result['bazi']['month']['zhi']

    queries = [f"{day_gan}日主", f"{day_gan}生{month_zhi}月", f"{day_gan}"]
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

    # Step 3: 分析
    display_analysis(bazi_result, unique_results)

    print("\n" + "=" * 70)
    print("演示完毕！")
    print("你可以运行 'python interactive.py' 来输入自己的出生信息。")
    print("=" * 70)

if __name__ == "__main__":
    main()
