#!/usr/bin/env python3
"""精简版演示 - 仅八字排盘，不依赖 sentence-transformers"""

from bazi_paipan import BaziPaipan


def print_banner():
    print("\n" + "=" * 60)
    print("  《三命通会》八字排盘 - 精简演示")
    print("=" * 60)


def display_bazi(result):
    print("\n" + "-" * 60)
    print("【八字排盘结果】")
    print("-" * 60)

    print(f"\n  八字: {result['bazi_string']}")
    print(f"  日主: {result['day_gan']} ({result['bazi']['day']['gan_wuxing']})")

    print("\n【四柱详情】")
    labels = {"year": "年柱", "month": "月柱", "day": "日柱", "hour": "时柱"}
    for key, label in labels.items():
        p = result['bazi'][key]
        print(f"  {label}: {p['gan']}{p['zhi']}  天干{p['gan_wuxing']} / 地支{p['zhi_wuxing']}")

    print("\n【五行统计】")
    for e, c in result['wuxing'].items():
        bar = "█" * c
        print(f"  {e}: {bar} {c}")

    print("\n【十神关系】")
    labels2 = {"year_shishen": "年柱", "month_shishen": "月柱",
               "day_shishen": "日柱", "hour_shishen": "时柱"}
    for key, label in labels2.items():
        info = result['shishen_detail'][key]
        print(f"  {label}: {info['gan']}{info['zhi']}  → {info['shishen_full']}")

    print(f"\n【出生信息】")
    print(f"  公历: {result['meta']['solar_date']}")
    print(f"  农历: {result['meta']['lunar_date']}")
    print(f"  性别: {result['meta']['gender']}")


def main():
    print_banner()

    # 可自行修改出生信息
    info = {
        "year": 1988,
        "month": 5,
        "day": 20,
        "hour": 10,
        "is_lunar": False,
        "gender": "男"
    }

    print(f"\n出生: {info['year']}-{info['month']:02d}-{info['day']:02d} {info['hour']}:00  性别: {info['gender']}")

    paipan = BaziPaipan()
    result = paipan.paipan(
        info['year'], info['month'], info['day'], info['hour'],
        is_lunar=info['is_lunar'],
        gender=info['gender']
    )

    if 'error' in result:
        print(f"错误: {result['error']}")
        return

    display_bazi(result)

    print("\n" + "=" * 60)
    print("  排盘完成！修改 demo_light.py 中的 info 可更换出生信息")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
