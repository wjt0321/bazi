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

    print("\n" + "=" * 50)
    print("所有测试通过!")
    print("=" * 50)
