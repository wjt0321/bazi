#!/usr/bin/env python3
"""
《三命通会》智能命理 Agent - 完整演示脚本
展示六大扩展功能：大运流年、神煞、命宫胎元身宫、合盘、择日、风水
"""

import json
import argparse
from bazi_paipan import BaziPaipan
from rag_retriever import RAGRetriever


def print_section(title):
    print("\n" + "=" * 70)
    print(f"【{title}】")
    print("=" * 70)


def display_bazi(bazi_result):
    print_section("八字排盘")
    print(f"\n八字: {bazi_result['bazi_string']}")
    print(f"日主: {bazi_result['day_gan']} ({bazi_result['bazi']['day']['gan_wuxing']})")

    print("\n【四柱详情】")
    labels = {"year": "年柱", "month": "月柱", "day": "日柱", "hour": "时柱"}
    for key, label in labels.items():
        p = bazi_result['bazi'][key]
        print(f"  {label}: {p['gan']}{p['zhi']}  ({p['gan_wuxing']}/{p['zhi_wuxing']})")

    print("\n【五行统计】")
    for e, c in bazi_result['wuxing'].items():
        bar = "█" * c + "░" * (4 - c)
        print(f"  {e}: {bar} {c}")

    print("\n【十神关系】")
    labels2 = {"year_shishen": "年柱", "month_shishen": "月柱",
               "day_shishen": "日柱", "hour_shishen": "时柱"}
    for key, label in labels2.items():
        info = bazi_result['shishen_detail'][key]
        print(f"  {label}: {info['gan']}{info['zhi']} → {info['shishen_full']}")


def display_dayun(paipan, bazi_result, birth_info):
    print_section("大运流年")

    from lunar_python import Solar
    solar = Solar.fromYmdHms(birth_info['year'], birth_info['month'], birth_info['day'], birth_info['hour'], 0, 0)
    lunar = solar.getLunar()
    qiyun = paipan.compute_qiyun(solar, lunar, birth_info['gender'])

    print(f"\n起运方向: {qiyun['direction']}")
    print(f"出生到节气天数: {qiyun['days_to_jieqi']}天")
    print(f"起运年龄: {qiyun['qiyun_age']}岁{qiyun['qiyun_months']}个月")

    dayun = paipan.compute_dayun(bazi_result['bazi'], birth_info['gender'])
    print(f"\n【大运排列】(共{len(dayun)}步)")
    print(f"{'步数':<4} {'年龄':<6} {'干支':<6} {'十神':<6}")
    print("-" * 30)
    for d in dayun:
        age = qiyun['qiyun_age'] + (d['step'] - 1) * 10
        print(f"{d['step']:<4} {age}岁{'':<2} {d['ganzhi']:<6} {d['shishen']:<6}")

    # 流年示例
    import datetime
    current_year = datetime.datetime.now().year
    liunian = paipan.compute_liunian(current_year)
    print(f"\n【今年流年】{current_year}年: {liunian['ganzhi']} ({liunian['gan_wuxing']}/{liunian['zhi_wuxing']})")


def display_shensha(paipan, bazi_result):
    print_section("神煞判断")

    shensha = paipan.compute_shensha(bazi_result['bazi'])

    print("\n【吉神】")
    if shensha['吉神']:
        for s in shensha['吉神']:
            print(f"  ★ {s}")
    else:
        print("  无")

    print("\n【凶煞】")
    if shensha['凶煞']:
        for s in shensha['凶煞']:
            print(f"  ⚠ {s}")
    else:
        print("  无")


def display_minggong(paipan, bazi_result):
    print_section("命宫胎元身宫")

    minggong = paipan.compute_minggong(bazi_result['bazi'])
    taiyuan = paipan.compute_taiyuan(bazi_result['bazi'])
    shengong = paipan.compute_shengong(bazi_result['bazi'])

    print(f"\n  命宫: {minggong['ganzhi']} ({minggong['gan_wuxing']}/{minggong['zhi_wuxing']})")
    print(f"  胎元: {taiyuan['ganzhi']} ({taiyuan['gan_wuxing']}/{taiyuan['zhi_wuxing']})")
    print(f"  身宫: {shengong['ganzhi']} ({shengong['gan_wuxing']}/{shengong['zhi_wuxing']})")


def display_fengshui(paipan, bazi_result):
    print_section("风水参考")

    fs = paipan.fengshui_reference(bazi_result['bazi'])

    print(f"\n  日主: {fs['day_gan']}")
    print(f"  最旺五行: {fs['max_wuxing']}")
    print(f"  最弱五行: {fs['min_wuxing']}")
    print(f"  喜用神: {fs['xiyong']}")

    print(f"\n  吉利方位: {'、'.join(fs['lucky_direction'])}")
    print(f"  吉利颜色: {'、'.join(fs['lucky_colors'])}")
    print(f"  吉利数字: {'、'.join(map(str, fs['lucky_numbers']))}")
    print(f"  适合行业: {'、'.join(fs['suitable_industries'])}")
    print(f"  避开方位: {'、'.join(fs['avoid_direction'])}")


def display_rag(bazi_result):
    print_section("《三命通会》原文检索")

    try:
        retriever = RAGRetriever('../data/sanmingtonghui_chunks.json')
        day_gan = bazi_result['day_gan']
        month_zhi = bazi_result['bazi']['month']['zhi']

        queries = [f"{day_gan}日主", f"{day_gan}生{month_zhi}月"]
        all_results = []
        for query in queries:
            results = retriever.retrieve(query, top_k=2)
            all_results.extend(results)

        seen = set()
        unique = []
        for r in all_results:
            if r['chunk_id'] not in seen:
                seen.add(r['chunk_id'])
                unique.append(r)

        unique.sort(key=lambda x: x['relevance'], reverse=True)

        for i, r in enumerate(unique[:3], 1):
            print(f"\n  [{i}] {r['source']}")
            print(f"      {r['text'][:200]}...")
    except Exception as e:
        print(f"  检索失败: {e}")


def display_zeri(paipan, year, month, day, event_type):
    print_section("择日分析")

    zeri = paipan.zeri_analysis(year, month, day, event_type=event_type)

    print(f"\n  日期: {zeri['date']}")
    print(f"  日柱: {zeri['day_bazi']}")
    print(f"  十二建星: {zeri['jianxing']}")
    print(f"  吉凶评级: {zeri['level']} (分数: {zeri['score']})")

    print(f"\n  宜: {', '.join(zeri['suitable']) if zeri['suitable'] else '无'}")
    print(f"  忌: {', '.join(zeri['unsuitable']) if zeri['unsuitable'] else '无'}")


def display_hepan(paipan, bazi1, bazi2, name1="甲方", name2="乙方"):
    print_section("合盘分析")

    hepan = paipan.hepan_analysis(bazi1, bazi2)

    print(f"\n  {name1} vs {name2}")
    print(f"  合盘分数: {hepan['score']}/100 ({hepan['level']})")
    print(f"  日柱关系: {hepan['rizhu_relation']}")

    if hepan['tiangan_he']:
        print(f"\n  天干相合: {', '.join(hepan['tiangan_he'])}")
    if hepan['dizhi_he']:
        print(f"  地支相合: {', '.join(hepan['dizhi_he'])}")
    if hepan['dizhi_chong']:
        print(f"  地支相冲: {', '.join(hepan['dizhi_chong'])}")
    if hepan['wuxing_complement']:
        print(f"  五行互补: {', '.join(hepan['wuxing_complement'])}")


def main():
    parser = argparse.ArgumentParser(
        description='《三命通会》智能命理 Agent - 完整演示',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python demo.py --year 1990 --month 5 --day 15 --hour 14 --gender 男
  python demo.py --year 1990 --month 5 --day 15 --hour 14 --gender 男 --zeri 2025 6 1 结婚
  python demo.py --year 1990 --month 5 --day 15 --hour 14 --gender 男 --hepan 1992 3 8 10 女
        """
    )
    parser.add_argument('--year', type=int, required=True, help='出生年份')
    parser.add_argument('--month', type=int, required=True, help='出生月份')
    parser.add_argument('--day', type=int, required=True, help='出生日期')
    parser.add_argument('--hour', type=int, required=True, help='出生小时')
    parser.add_argument('--gender', type=str, default='男', help='性别')
    parser.add_argument('--lunar', action='store_true', help='农历日期')
    parser.add_argument('--zeri', nargs=4, metavar=('Y', 'M', 'D', 'EVENT'), help='择日分析')
    parser.add_argument('--hepan', nargs=5, metavar=('Y', 'M', 'D', 'H', 'GENDER'), help='合盘分析')
    parser.add_argument('--output', type=str, choices=['text', 'json'], default='text', help='输出格式')

    args = parser.parse_args()

    paipan = BaziPaipan()
    birth_info = {
        'year': args.year, 'month': args.month, 'day': args.day, 'hour': args.hour,
        'is_lunar': args.lunar, 'gender': args.gender
    }

    # 八字排盘
    bazi_result = paipan.paipan(**birth_info)
    if 'error' in bazi_result:
        print(f"排盘错误: {bazi_result['error']}")
        return

    if args.output == 'json':
        # JSON输出完整数据
        full_result = {
            'bazi': bazi_result,
            'dayun': paipan.compute_dayun(bazi_result['bazi'], birth_info['gender']),
            'shensha': paipan.compute_shensha(bazi_result['bazi']),
            'minggong': paipan.compute_minggong(bazi_result['bazi']),
            'taiyuan': paipan.compute_taiyuan(bazi_result['bazi']),
            'shengong': paipan.compute_shengong(bazi_result['bazi']),
            'fengshui': paipan.fengshui_reference(bazi_result['bazi'])
        }
        print(json.dumps(full_result, ensure_ascii=False, indent=2))
        return

    # 文本输出
    print("\n" + "=" * 70)
    print("《三命通会》智能命理分析系统")
    print("=" * 70)
    print(f"\n出生: {birth_info['year']}年{birth_info['month']}月{birth_info['day']}日{birth_info['hour']}时")
    print(f"性别: {birth_info['gender']}")

    display_bazi(bazi_result)
    display_shensha(paipan, bazi_result)
    display_minggong(paipan, bazi_result)
    display_dayun(paipan, bazi_result, birth_info)
    display_fengshui(paipan, bazi_result)
    display_rag(bazi_result)

    # 择日分析
    if args.zeri:
        zeri_year, zeri_month, zeri_day, event = args.zeri
        display_zeri(paipan, int(zeri_year), int(zeri_month), int(zeri_day), event)

    # 合盘分析
    if args.hepan:
        hy, hm, hd, hh, hgender = args.hepan
        bazi2 = paipan.paipan(int(hy), int(hm), int(hd), int(hh), gender=hgender)
        if 'error' not in bazi2:
            display_hepan(paipan, bazi_result['bazi'], bazi2['bazi'])

    print("\n" + "=" * 70)
    print("分析完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
