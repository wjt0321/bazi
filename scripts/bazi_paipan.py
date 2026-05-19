"""
八字排盘工具

基于 lunar_python 库实现完整的八字排盘功能，包括：
- 四柱天干地支计算
- 五行属性统计
- 十神关系计算
- 支持公历和农历输入

使用方法：
    python bazi_paipan.py --year 1990 --month 1 --day 1 --hour 12 --gender 男

或者作为模块导入：
    from bazi_paipan import BaziPaipan
    paipan = BaziPaipan()
    result = paipan.paipan(1990, 1, 1, 12, is_lunar=False, gender="男")
"""

from lunar_python import Lunar, Solar
from typing import Dict, Any, Optional


class BaziPaipan:
    """
    八字排盘类

    提供完整的八字排盘功能，包括：
    - 天干地支计算
    - 五行统计
    - 十神关系
    - 支持公历/农历输入
    """

    def __init__(self):
        """
        初始化八字排盘器

        设置天干、地支列表，以及天干地支对应的五行属性
        """
        self.gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

        self.zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

        self.wuxing_gan = {
            "甲": "木", "乙": "木",
            "丙": "火", "丁": "火",
            "戊": "土", "己": "土",
            "庚": "金", "辛": "金",
            "壬": "水", "癸": "水"
        }

        self.wuxing_zhi = {
            "子": "水", "丑": "土",
            "寅": "木", "卯": "木",
            "辰": "土", "巳": "火",
            "午": "火", "未": "土",
            "申": "金", "酉": "金",
            "戌": "土", "亥": "水"
        }

        self.gan_order = {g: i for i, g in enumerate(self.gan_list)}
        self.zhi_order = {z: i for i, z in enumerate(self.zhi_list)}

        self.shishen_names = {
            "比": "比肩",
            "劫": "劫财",
            "食": "食神",
            "伤": "伤官",
            "财": "正财",
            "才": "偏财",
            "官": "正官",
            "杀": "七杀",
            "枭": "偏印",
            "印": "正印"
        }

    def _get_shishen(self, day_gan: str, other_gan: str) -> str:
        """
        计算十神

        根据日干和其他干的关系计算十神

        Args:
            day_gan: 日干
            other_gan: 其他天干

        Returns:
            十神简称（比、劫、食、伤、财、才、官、杀、枭、印）
        """
        day_idx = self.gan_order[day_gan]
        other_idx = self.gan_order[other_gan]

        diff = (other_idx - day_idx) % 10

        shishen_map = {
            0: "比",
            1: "劫",
            2: "食",
            3: "伤",
            4: "财",
            5: "才",
            6: "官",
            7: "杀",
            8: "枭",
            9: "印"
        }

        return shishen_map[diff]

    def _count_wuxing(self, bazi: Dict) -> Dict[str, int]:
        """
        统计五行数量

        统计八字中木、火、土、金、水的个数

        Args:
            bazi: 八字字典

        Returns:
            五行计数字典
        """
        wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

        for position in ["year", "month", "day", "hour"]:
            gan = bazi[position]["gan"]
            zhi = bazi[position]["zhi"]

            wuxing_count[self.wuxing_gan[gan]] += 1
            wuxing_count[self.wuxing_zhi[zhi]] += 1

        return wuxing_count

    def _get_shishen_detail(self, bazi: Dict) -> Dict[str, dict]:
        """
        获取详细十神信息

        计算四柱各位置的十神及其五行属性

        Args:
            bazi: 八字字典

        Returns:
            包含各位置十神详情的字典
        """
        day_gan = bazi["day"]["gan"]
        shishen_detail = {}

        for position in ["year", "month", "day", "hour"]:
            gan = bazi[position]["gan"]
            shishen = self._get_shishen(day_gan, gan)
            zhi = bazi[position]["zhi"]

            key = f"{position}_shishen"
            shishen_detail[key] = {
                "gan": gan,
                "zhi": zhi,
                "shishen": shishen,
                "shishen_full": self.shishen_names[shishen],
                "gan_wuxing": self.wuxing_gan[gan],
                "zhi_wuxing": self.wuxing_zhi[zhi]
            }

        return shishen_detail

    def _get_zhi_xing(self, zhi: str) -> str:
        """
        获取地支藏干主气

        Args:
            zhi: 地支

        Returns:
            地支藏干的主气天干
        """
        zang_gan = {
            "子": "癸", "丑": "己", "寅": "甲", "卯": "乙",
            "辰": "戊", "巳": "丙", "午": "丁", "未": "己",
            "申": "庚", "酉": "辛", "戌": "戊", "亥": "壬"
        }
        return zang_gan.get(zhi, "")

    def paipan(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        is_lunar: bool = False,
        gender: str = "男"
    ) -> Dict[str, Any]:
        """
        八字排盘主函数

        根据出生日期时间计算完整八字

        Args:
            year: 年份
            month: 月份 (1-12)
            day: 日期 (1-31)
            hour: 小时 (0-23)
            is_lunar: 是否农历 (默认公历)
            gender: 性别 (男/女)

        Returns:
            包含八字、五行、十神等完整信息的字典
        """
        try:
            if is_lunar:
                lunar = Lunar.fromYmdHms(year, month, day, hour, 0, 0)
                solar = lunar.getSolar()
            else:
                solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)

            lunar = solar.getLunar()

            year_gan_idx = lunar.getYearGanIndex()
            year_zhi_idx = lunar.getYearZhiIndex()
            month_gan_idx = lunar.getMonthGanIndex()
            month_zhi_idx = lunar.getMonthZhiIndex()
            day_gan_idx = lunar.getDayGanIndex()
            day_zhi_idx = lunar.getDayZhiIndex()
            hour_gan_idx = lunar.getTimeGanIndex()
            hour_zhi_idx = lunar.getTimeZhiIndex()

            year_gan = self.gan_list[year_gan_idx]
            year_zhi = self.zhi_list[year_zhi_idx]
            month_gan = self.gan_list[month_gan_idx]
            month_zhi = self.zhi_list[month_zhi_idx]
            day_gan = self.gan_list[day_gan_idx]
            day_zhi = self.zhi_list[day_zhi_idx]
            hour_gan = self.gan_list[hour_gan_idx]
            hour_zhi = self.zhi_list[hour_zhi_idx]

            bazi = {
                "year": {
                    "gan": year_gan,
                    "zhi": year_zhi,
                    "gan_wuxing": self.wuxing_gan[year_gan],
                    "zhi_wuxing": self.wuxing_zhi[year_zhi],
                    "zhi_xing": self._get_zhi_xing(year_zhi)
                },
                "month": {
                    "gan": month_gan,
                    "zhi": month_zhi,
                    "gan_wuxing": self.wuxing_gan[month_gan],
                    "zhi_wuxing": self.wuxing_zhi[month_zhi],
                    "zhi_xing": self._get_zhi_xing(month_zhi)
                },
                "day": {
                    "gan": day_gan,
                    "zhi": day_zhi,
                    "gan_wuxing": self.wuxing_gan[day_gan],
                    "zhi_wuxing": self.wuxing_zhi[day_zhi],
                    "zhi_xing": self._get_zhi_xing(day_zhi)
                },
                "hour": {
                    "gan": hour_gan,
                    "zhi": hour_zhi,
                    "gan_wuxing": self.wuxing_gan[hour_gan],
                    "zhi_wuxing": self.wuxing_zhi[hour_zhi],
                    "zhi_xing": self._get_zhi_xing(hour_zhi)
                }
            }

            wuxing_count = self._count_wuxing(bazi)
            shishen_detail = self._get_shishen_detail(bazi)

            result = {
                "bazi": bazi,
                "bazi_string": f"{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}",
                "day_gan": day_gan,
                "day_zhi": day_zhi,
                "wuxing": wuxing_count,
                "shishen_detail": shishen_detail,
                "meta": {
                    "solar_date": solar.toString(),
                    "lunar_date": lunar.toString(),
                    "lunar_year": lunar.getYearInChinese(),
                    "lunar_month": lunar.getMonthInChinese(),
                    "lunar_day": lunar.getDayInChinese(),
                    "gender": gender,
                    "is_lunar": is_lunar,
                    "week_day": solar.getWeek()
                }
            }

            return result

        except Exception as e:
            return {"error": str(e)}

    def paipan_from_string(self, bazi_str: str, gender: str = "男") -> Dict[str, Any]:
        """
        从八字字符串进行排盘

        当已有八字时，可以直接输入字符串进行分析

        Args:
            bazi_str: 八字字符串，格式如 "庚午 辛丑 丙申 甲午"
            gender: 性别 (男/女)

        Returns:
            包含八字、五行、十神等完整信息的字典
        """
        parts = bazi_str.strip().split()

        if len(parts) != 4:
            return {"error": "八字格式错误，应为4个字，例如：庚午 辛丑 丙申 甲午"}

        bazi = {}
        positions = ["year", "month", "day", "hour"]

        for i, part in enumerate(parts):
            if len(part) != 2:
                return {"error": f"'{part}' 格式错误，应为2个字符"}

            gan, zhi = part[0], part[1]

            if gan not in self.gan_list:
                return {"error": f"'{gan}' 不是有效的天干"}

            if zhi not in self.zhi_list:
                return {"error": f"'{zhi}' 不是有效的地支"}

            bazi[positions[i]] = {
                "gan": gan,
                "zhi": zhi,
                "gan_wuxing": self.wuxing_gan[gan],
                "zhi_wuxing": self.wuxing_zhi[zhi],
                "zhi_xing": self._get_zhi_xing(zhi)
            }

        wuxing_count = self._count_wuxing(bazi)
        shishen_detail = self._get_shishen_detail(bazi)

        return {
            "bazi": bazi,
            "bazi_string": bazi_str,
            "day_gan": bazi["day"]["gan"],
            "day_zhi": bazi["day"]["zhi"],
            "wuxing": wuxing_count,
            "shishen_detail": shishen_detail,
            "meta": {
                "gender": gender,
                "from_string": True
            }
        }

    def get_bazi_summary(self, result: Dict[str, Any]) -> str:
        """
        生成八字摘要信息

        Args:
            result: paipan() 或 paipan_from_string() 返回的结果

        Returns:
            格式化的八字摘要字符串
        """
        if "error" in result:
            return f"错误: {result['error']}"

        bazi = result["bazi"]
        wuxing = result["wuxing"]
        day_gan = result["day_gan"]

        summary = []
        summary.append(f"八字: {result['bazi_string']}")
        summary.append(f"日主: {day_gan}{self.wuxing_gan[day_gan] if day_gan in self.wuxing_gan else ''}")
        summary.append(f"年柱: {bazi['year']['gan']}{bazi['year']['zhi']} ({bazi['year']['gan_wuxing']})")
        summary.append(f"月柱: {bazi['month']['gan']}{bazi['month']['zhi']} ({bazi['month']['gan_wuxing']})")
        summary.append(f"日柱: {bazi['day']['gan']}{bazi['day']['zhi']} ({bazi['day']['gan_wuxing']})")
        summary.append(f"时柱: {bazi['hour']['gan']}{bazi['hour']['zhi']} ({bazi['hour']['gan_wuxing']})")
        summary.append(f"五行: 木{wuxing['木']} 火{wuxing['火']} 土{wuxing['土']} 金{wuxing['金']} 水{wuxing['水']}")

        return "\n".join(summary)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description='八字排盘工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python bazi_paipan.py --year 1990 --month 1 --day 1 --hour 12
  python bazi_paipan.py --year 1990 --month 1 --day 1 --hour 12 --gender 女
  python bazi_paipan.py --year 1990 --month 1 --day 1 --hour 12 --lunar
        """
    )
    parser.add_argument('--year', type=int, required=True, help='年份')
    parser.add_argument('--month', type=int, required=True, help='月份 (1-12)')
    parser.add_argument('--day', type=int, required=True, help='日期 (1-31)')
    parser.add_argument('--hour', type=int, required=True, help='小时 (0-23)')
    parser.add_argument('--gender', type=str, default='男', help='性别 (男/女)')
    parser.add_argument('--lunar', action='store_true', help='使用农历日期')
    parser.add_argument('--format', type=str, default='json', choices=['json', 'text'], help='输出格式')

    args = parser.parse_args()

    paipan = BaziPaipan()
    result = paipan.paipan(
        args.year, args.month, args.day, args.hour,
        is_lunar=args.lunar, gender=args.gender
    )

    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(paipan.get_bazi_summary(result))
