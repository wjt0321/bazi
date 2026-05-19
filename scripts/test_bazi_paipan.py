import json
from bazi_paipan import BaziPaipan

def test_basic_paipan():
    paipan = BaziPaipan()
    result = paipan.paipan(1990, 1, 1, 12, is_lunar=False, gender="男")

    assert "bazi" in result
    assert "wuxing" in result
    assert "shishen_detail" in result

    print("八字:", result["bazi"])
    print("五行:", result["wuxing"])
    print("十神:", result["shishen_detail"])

    return True

def test_lunar_paipan():
    paipan = BaziPaipan()
    result = paipan.paipan(1990, 1, 1, 12, is_lunar=True, gender="女")

    assert "bazi" in result
    assert result["meta"]["is_lunar"] == True
    assert result["meta"]["gender"] == "女"

    print("\n农历排盘测试:")
    print("八字:", result["bazi"])
    print("元信息:", result["meta"])

    return True

def test_paipan_from_string():
    paipan = BaziPaipan()
    result = paipan.paipan_from_string("庚午 辛丑 丙申 甲午", gender="男")

    assert "bazi" in result
    assert result["bazi"]["year"]["gan"] == "庚"
    assert result["bazi"]["year"]["zhi"] == "午"
    assert result["bazi"]["day"]["gan"] == "丙"

    print("\n从八字字符串排盘测试:")
    print("八字:", result["bazi"])
    print("五行统计:", result["wuxing"])
    print("十神详情:", result["shishen_detail"])

    return True

def test_wuxing_count():
    paipan = BaziPaipan()
    result = paipan.paipan(1990, 1, 1, 12, is_lunar=False, gender="男")

    wuxing = result["wuxing"]
    assert "木" in wuxing
    assert "火" in wuxing
    assert "土" in wuxing
    assert "金" in wuxing
    assert "水" in wuxing

    total = sum(wuxing.values())
    assert total == 8, f"五行总数应为8，实际为{total}"

    print("\n五行统计测试:")
    print(f"五行分布: {wuxing}")
    print(f"总数: {total} (应为8)")

    return True

def test_shishen_calculation():
    paipan = BaziPaipan()
    result = paipan.paipan_from_string("庚午 辛丑 丙申 甲午", gender="男")

    shishen_detail = result["shishen_detail"]
    assert "day_shishen" in shishen_detail
    assert shishen_detail["day_shishen"]["gan"] == "丙"
    assert shishen_detail["day_shishen"]["zhi"] == "申"

    print("\n十神计算测试:")
    print("日干(丙火)的十神:")
    for key, value in shishen_detail.items():
        print(f"  {key}: {value['gan']}{value['zhi']} - {value['shishen']}")

    return True

def test_dayun():
    paipan = BaziPaipan()
    result = paipan.paipan(1990, 5, 15, 14, gender="男")
    bazi = result['bazi']

    dayun = paipan.compute_dayun(bazi, "男")
    assert len(dayun) == 10
    assert dayun[0]['step'] == 1
    assert 'ganzhi' in dayun[0]
    assert 'shishen' in dayun[0]

    print("\n大运测试:")
    print(f"  大运步数: {len(dayun)}")
    print(f"  第一步: {dayun[0]['ganzhi']} ({dayun[0]['shishen']})")

    return True


def test_shensha():
    paipan = BaziPaipan()
    result = paipan.paipan(1990, 5, 15, 14, gender="男")

    shensha = paipan.compute_shensha(result['bazi'])
    assert '吉神' in shensha
    assert '凶煞' in shensha

    print("\n神煞测试:")
    print(f"  吉神: {shensha['吉神']}")
    print(f"  凶煞: {shensha['凶煞']}")

    return True


def test_minggong_taiyuan_shengong():
    paipan = BaziPaipan()
    result = paipan.paipan(1990, 5, 15, 14, gender="男")

    minggong = paipan.compute_minggong(result['bazi'])
    taiyuan = paipan.compute_taiyuan(result['bazi'])
    shengong = paipan.compute_shengong(result['bazi'])

    assert 'ganzhi' in minggong
    assert 'ganzhi' in taiyuan
    assert 'ganzhi' in shengong

    print("\n命宫胎元身宫测试:")
    print(f"  命宫: {minggong['ganzhi']}")
    print(f"  胎元: {taiyuan['ganzhi']}")
    print(f"  身宫: {shengong['ganzhi']}")

    return True


def test_hepan():
    paipan = BaziPaipan()
    bazi1 = paipan.paipan(1990, 5, 15, 14, gender="男")['bazi']
    bazi2 = paipan.paipan(1992, 3, 8, 10, gender="女")['bazi']

    hepan = paipan.hepan_analysis(bazi1, bazi2)
    assert 'score' in hepan
    assert 'level' in hepan
    assert 'rizhu_relation' in hepan

    print("\n合盘测试:")
    print(f"  分数: {hepan['score']}/100 ({hepan['level']})")
    print(f"  日柱关系: {hepan['rizhu_relation']}")

    return True


def test_zeri():
    paipan = BaziPaipan()
    zeri = paipan.zeri_analysis(2025, 6, 1, event_type="结婚")

    assert 'jianxing' in zeri
    assert 'score' in zeri
    assert 'level' in zeri

    print("\n择日测试:")
    print(f"  日期: {zeri['date']}")
    print(f"  建星: {zeri['jianxing']}")
    print(f"  评级: {zeri['level']} ({zeri['score']}分)")

    return True


def test_fengshui():
    paipan = BaziPaipan()
    result = paipan.paipan(1990, 5, 15, 14, gender="男")

    fs = paipan.fengshui_reference(result['bazi'])
    assert 'xiyong' in fs
    assert 'lucky_direction' in fs
    assert 'lucky_colors' in fs

    print("\n风水测试:")
    print(f"  喜用神: {fs['xiyong']}")
    print(f"  吉利方位: {fs['lucky_direction']}")
    print(f"  适合行业: {fs['suitable_industries'][:3]}")

    return True


if __name__ == "__main__":
    print("=" * 50)
    print("八字排盘工具测试")
    print("=" * 50)

    test_basic_paipan()
    print("\n" + "-" * 50)

    test_lunar_paipan()
    print("\n" + "-" * 50)

    test_paipan_from_string()
    print("\n" + "-" * 50)

    test_wuxing_count()
    print("\n" + "-" * 50)

    test_shishen_calculation()
    print("\n" + "-" * 50)

    test_dayun()
    print("\n" + "-" * 50)

    test_shensha()
    print("\n" + "-" * 50)

    test_minggong_taiyuan_shengong()
    print("\n" + "-" * 50)

    test_hepan()
    print("\n" + "-" * 50)

    test_zeri()
    print("\n" + "-" * 50)

    test_fengshui()

    print("\n" + "=" * 50)
    print("所有测试通过!")
    print("=" * 50)
