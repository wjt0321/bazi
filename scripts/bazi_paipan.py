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

            year_ganzhi = lunar.getYearInGanZhiByLiChun()
            year_gan = year_ganzhi[0]
            year_zhi = year_ganzhi[1]
            month_gan = self.gan_list[lunar.getMonthGanIndex()]
            month_zhi = self.zhi_list[lunar.getMonthZhiIndex()]
            day_gan = self.gan_list[lunar.getDayGanIndex()]
            day_zhi = self.zhi_list[lunar.getDayZhiIndex()]
            hour_gan = self.gan_list[lunar.getTimeGanIndex()]
            hour_zhi = self.zhi_list[lunar.getTimeZhiIndex()]

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

    # ==================== 大运流年计算 ====================

    def _is_yang_gan(self, gan: str) -> bool:
        """判断天干是否为阳干"""
        return gan in ["甲", "丙", "戊", "庚", "壬"]

    def _get_next_ganzhi(self, gan: str, zhi: str, forward: bool = True) -> tuple:
        """
        获取下一个/上一个干支组合

        Args:
            gan: 当前天干
            zhi: 当前地支
            forward: True为顺排，False为逆排

        Returns:
            (下一个天干, 下一个地支)
        """
        gan_idx = self.gan_order[gan]
        zhi_idx = self.zhi_order[zhi]

        if forward:
            next_gan_idx = (gan_idx + 1) % 10
            next_zhi_idx = (zhi_idx + 1) % 12
        else:
            next_gan_idx = (gan_idx - 1) % 10
            next_zhi_idx = (zhi_idx - 1) % 12

        return self.gan_list[next_gan_idx], self.zhi_list[next_zhi_idx]

    def compute_dayun(self, bazi: Dict, gender: str) -> list:
        """
        计算大运

        规则：
        - 阳年男命顺排，阴年男命逆排
        - 阳年女命逆排，阴年女命顺排

        Args:
            bazi: 八字字典
            gender: 性别 (男/女)

        Returns:
            大运列表，每项包含年龄和干支
        """
        year_gan = bazi["year"]["gan"]
        month_gan = bazi["month"]["gan"]
        month_zhi = bazi["month"]["zhi"]

        is_yang_year = self._is_yang_gan(year_gan)
        is_male = gender == "男"

        # 确定顺逆：阳男阴女顺排，阴男阳女逆排
        forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)

        dayun = []
        current_gan, current_zhi = month_gan, month_zhi

        for i in range(10):
            current_gan, current_zhi = self._get_next_ganzhi(current_gan, current_zhi, forward)
            shishen = self._get_shishen(bazi["day"]["gan"], current_gan)
            dayun.append({
                "step": i + 1,
                "ganzhi": f"{current_gan}{current_zhi}",
                "shishen": self.shishen_names[shishen]
            })

        return dayun

    def compute_qiyun(self, solar, lunar, gender: str) -> dict:
        """
        计算起运岁数

        规则：
        - 从出生日到下一个/上一个节气的天数
        - 三天折合一岁，一天折合四个月，一个时辰折合十天

        Args:
            solar: Solar对象
            lunar: Lunar对象
            gender: 性别

        Returns:
            起运信息字典
        """
        year_gan = self.gan_list[lunar.getYearGanIndex()]
        is_yang_year = self._is_yang_gan(year_gan)
        is_male = gender == "男"
        forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)

        # 获取节气信息
        jie_qi = lunar.getJieQiTable()
        current_jie = lunar.getPrevJieQi()
        next_jie = lunar.getNextJieQi()

        # 计算到节气的天数差
        birth_solar = solar
        if forward:
            # 顺排：计算到下一个节气的天数
            target_solar = next_jie.getSolar()
        else:
            # 逆排：计算到上一个节气的天数
            target_solar = current_jie.getSolar()

        days_diff = birth_solar.subtract(target_solar)
        days_diff = abs(days_diff)

        # 三天折合一岁
        years = days_diff // 3
        remainder_days = days_diff % 3

        # 余下天数折合月数 (1天 = 4个月)
        months = remainder_days * 4

        return {
            "days_to_jieqi": days_diff,
            "qiyun_age": years,
            "qiyun_months": months,
            "qiyun_total_months": years * 12 + months,
            "direction": "顺行" if forward else "逆行"
        }

    def compute_liunian(self, year: int) -> dict:
        """
        计算指定农历年份的流年（或公历年份对应的农历年）

        Args:
            year: 年份（如果是公历，会自动转换为对应的农历年干支）

        Returns:
            流年信息字典
        """
        # 使用六十甲子表直接计算，避免依赖农历库的1月1日
        # 公元4年是甲子年
        base_year = 4
        offset = (year - base_year) % 60
        
        gan_idx = offset % 10
        zhi_idx = offset % 12
        
        year_gan = self.gan_list[gan_idx]
        year_zhi = self.zhi_list[zhi_idx]

        return {
            "year": year,
            "ganzhi": f"{year_gan}{year_zhi}",
            "gan": year_gan,
            "zhi": year_zhi,
            "gan_wuxing": self.wuxing_gan[year_gan],
            "zhi_wuxing": self.wuxing_zhi[year_zhi]
        }

    # ==================== 神煞判断 ====================

    def compute_shensha(self, bazi: Dict) -> dict:
        """
        计算常用神煞

        Args:
            bazi: 八字字典

        Returns:
            神煞分类字典
        """
        day_gan = bazi["day"]["gan"]
        day_zhi = bazi["day"]["zhi"]
        year_zhi = bazi["year"]["zhi"]
        month_zhi = bazi["month"]["zhi"]

        jishen = []
        xiongsha = []

        # 天乙贵人 (以日干为主)
        tianyi_map = {
            "甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
            "乙": ["子", "申"], "己": ["子", "申"],
            "丙": ["亥", "酉"], "丁": ["亥", "酉"],
            "壬": ["卯", "巳"], "癸": ["卯", "巳"],
            "辛": ["午", "寅"]
        }
        for zhi in [year_zhi, month_zhi, day_zhi, bazi["hour"]["zhi"]]:
            if zhi in tianyi_map.get(day_gan, []):
                jishen.append(f"天乙贵人({zhi})")
                break

        # 文昌 (以日干为主)
        wenchang_map = {
            "甲": "巳", "乙": "午", "丙": "申", "丁": "酉",
            "戊": "申", "己": "酉", "庚": "亥", "辛": "子",
            "壬": "寅", "癸": "卯"
        }
        wc_zhi = wenchang_map.get(day_gan, "")
        for pos, zhi in [("年", year_zhi), ("月", month_zhi), ("日", day_zhi), ("时", bazi["hour"]["zhi"])]:
            if zhi == wc_zhi:
                jishen.append(f"文昌({pos})")

        # 驿马 (以年支或日支为主，此处用日支)
        yima_map = {
            "申": "寅", "子": "寅", "辰": "寅",
            "亥": "巳", "卯": "巳", "未": "巳",
            "寅": "申", "午": "申", "戌": "申",
            "巳": "亥", "酉": "亥", "丑": "亥"
        }
        ym_zhi = yima_map.get(day_zhi, "")
        for pos, zhi in [("年", year_zhi), ("月", month_zhi), ("日", day_zhi), ("时", bazi["hour"]["zhi"])]:
            if zhi == ym_zhi:
                xiongsha.append(f"驿马({pos})")

        # 桃花 (以年支或日支为主，此处用日支)
        taohua_map = {
            "申": "酉", "子": "酉", "辰": "酉",
            "亥": "子", "卯": "子", "未": "子",
            "寅": "卯", "午": "卯", "戌": "卯",
            "巳": "午", "酉": "午", "丑": "午"
        }
        th_zhi = taohua_map.get(day_zhi, "")
        for pos, zhi in [("年", year_zhi), ("月", month_zhi), ("日", day_zhi), ("时", bazi["hour"]["zhi"])]:
            if zhi == th_zhi:
                xiongsha.append(f"桃花({pos})")

        # 羊刃 (以日干为主)
        yangren_map = {
            "甲": "卯", "乙": "寅",
            "丙": "午", "丁": "巳",
            "戊": "午", "己": "巳",
            "庚": "酉", "辛": "申",
            "壬": "子", "癸": "亥"
        }
        yr_zhi = yangren_map.get(day_gan, "")
        for pos, zhi in [("年", year_zhi), ("月", month_zhi), ("日", day_zhi), ("时", bazi["hour"]["zhi"])]:
            if zhi == yr_zhi:
                xiongsha.append(f"羊刃({pos})")

        # 空亡 (以日柱为主，查六十甲子旬空)
        kongwang_map = {
            "甲子": ["戌", "亥"], "甲戌": ["申", "酉"], "甲申": ["午", "未"],
            "甲午": ["辰", "巳"], "甲辰": ["寅", "卯"], "甲寅": ["子", "丑"]
        }
        # 找到日柱所在的旬
        day_ganzhi = f"{day_gan}{day_zhi}"
        for xun, kongs in kongwang_map.items():
            xun_gan_idx = self.gan_order[xun[0]]
            day_gan_idx = self.gan_order[day_gan]
            if (day_gan_idx - xun_gan_idx) % 10 in range(6):
                if day_zhi in kongs:
                    xiongsha.append(f"空亡(日)")
                break

        return {
            "吉神": list(set(jishen)),
            "凶煞": list(set(xiongsha))
        }

    # ==================== 命宫胎元身宫 ====================

    def compute_minggong(self, bazi: Dict) -> dict:
        """
        计算命宫

        公式：命宫地支 = (26 - 月支序号 - 时支序号) % 12
        命宫天干按年干起月法推算

        Args:
            bazi: 八字字典

        Returns:
            命宫信息字典
        """
        month_zhi_idx = self.zhi_order[bazi["month"]["zhi"]]
        hour_zhi_idx = self.zhi_order[bazi["hour"]["zhi"]]

        # 命宫地支
        minggong_zhi_idx = (26 - month_zhi_idx - hour_zhi_idx) % 12
        if minggong_zhi_idx == 0:
            minggong_zhi_idx = 12
        minggong_zhi = self.zhi_list[minggong_zhi_idx - 1]

        # 命宫天干：按年干起月法（五虎遁月）
        year_gan = bazi["year"]["gan"]
        # 寅月起始的天干
        if year_gan in ["甲", "己"]:
            start_gan = "丙"
        elif year_gan in ["乙", "庚"]:
            start_gan = "戊"
        elif year_gan in ["丙", "辛"]:
            start_gan = "庚"
        elif year_gan in ["丁", "壬"]:
            start_gan = "壬"
        else:  # 戊、癸
            start_gan = "甲"

        start_idx = self.gan_order[start_gan]
        minggong_zhi_pos = minggong_zhi_idx - 1  # 0-based
        minggong_gan_idx = (start_idx + minggong_zhi_pos) % 10
        minggong_gan = self.gan_list[minggong_gan_idx]

        return {
            "ganzhi": f"{minggong_gan}{minggong_zhi}",
            "gan": minggong_gan,
            "zhi": minggong_zhi,
            "gan_wuxing": self.wuxing_gan[minggong_gan],
            "zhi_wuxing": self.wuxing_zhi[minggong_zhi]
        }

    def compute_taiyuan(self, bazi: Dict) -> dict:
        """
        计算胎元

        公式：
        - 胎元天干 = 月干前进一位
        - 胎元地支 = 月支前进三位

        Args:
            bazi: 八字字典

        Returns:
            胎元信息字典
        """
        month_gan_idx = self.gan_order[bazi["month"]["gan"]]
        month_zhi_idx = self.zhi_order[bazi["month"]["zhi"]]

        taiyuan_gan = self.gan_list[(month_gan_idx + 1) % 10]
        taiyuan_zhi = self.zhi_list[(month_zhi_idx + 3) % 12]

        return {
            "ganzhi": f"{taiyuan_gan}{taiyuan_zhi}",
            "gan": taiyuan_gan,
            "zhi": taiyuan_zhi,
            "gan_wuxing": self.wuxing_gan[taiyuan_gan],
            "zhi_wuxing": self.wuxing_zhi[taiyuan_zhi]
        }

    def compute_shengong(self, bazi: Dict) -> dict:
        """
        计算身宫

        公式：身宫地支 = (月支序号 + 时支序号) * 2 % 12
        身宫天干按年干起月法推算

        Args:
            bazi: 八字字典

        Returns:
            身宫信息字典
        """
        month_zhi_idx = self.zhi_order[bazi["month"]["zhi"]]
        hour_zhi_idx = self.zhi_order[bazi["hour"]["zhi"]]

        # 身宫地支
        shengong_zhi_idx = ((month_zhi_idx + hour_zhi_idx) * 2) % 12
        shengong_zhi = self.zhi_list[shengong_zhi_idx]

        # 身宫天干：按年干起月法
        year_gan = bazi["year"]["gan"]
        if year_gan in ["甲", "己"]:
            start_gan = "丙"
        elif year_gan in ["乙", "庚"]:
            start_gan = "戊"
        elif year_gan in ["丙", "辛"]:
            start_gan = "庚"
        elif year_gan in ["丁", "壬"]:
            start_gan = "壬"
        else:
            start_gan = "甲"

        start_idx = self.gan_order[start_gan]
        shengong_gan_idx = (start_idx + shengong_zhi_idx) % 10
        shengong_gan = self.gan_list[shengong_gan_idx]

        return {
            "ganzhi": f"{shengong_gan}{shengong_zhi}",
            "gan": shengong_gan,
            "zhi": shengong_zhi,
            "gan_wuxing": self.wuxing_gan[shengong_gan],
            "zhi_wuxing": self.wuxing_zhi[shengong_zhi]
        }

    # ==================== 合盘分析 ====================

    def hepan_analysis(self, bazi1: Dict, bazi2: Dict) -> dict:
        """
        两人八字合盘分析

        Args:
            bazi1: 第一个人的八字
            bazi2: 第二个人的八字

        Returns:
            合盘分析结果字典
        """
        tiangan_he = []
        dizhi_he = []
        dizhi_chong = []

        # 天干相合
        tg_he_rules = {
            ("甲", "己"): "甲己合土", ("己", "甲"): "甲己合土",
            ("乙", "庚"): "乙庚合金", ("庚", "乙"): "乙庚合金",
            ("丙", "辛"): "丙辛合水", ("辛", "丙"): "丙辛合水",
            ("丁", "壬"): "丁壬合木", ("壬", "丁"): "丁壬合木",
            ("戊", "癸"): "戊癸合火", ("癸", "戊"): "戊癸合火"
        }

        positions = ["year", "month", "day", "hour"]
        for p1 in positions:
            for p2 in positions:
                pair = (bazi1[p1]["gan"], bazi2[p2]["gan"])
                if pair in tg_he_rules:
                    tiangan_he.append(f"{tg_he_rules[pair]}({p1}-{p2})")

        # 地支六合
        dz_he_rules = {
            ("子", "丑"): "子丑合土", ("丑", "子"): "子丑合土",
            ("寅", "亥"): "寅亥合木", ("亥", "寅"): "寅亥合木",
            ("卯", "戌"): "卯戌合火", ("戌", "卯"): "卯戌合火",
            ("辰", "酉"): "辰酉合金", ("酉", "辰"): "辰酉合金",
            ("巳", "申"): "巳申合水", ("申", "巳"): "巳申合水",
            ("午", "未"): "午未合火", ("未", "午"): "午未合火"
        }

        for p1 in positions:
            for p2 in positions:
                pair = (bazi1[p1]["zhi"], bazi2[p2]["zhi"])
                if pair in dz_he_rules:
                    dizhi_he.append(f"{dz_he_rules[pair]}({p1}-{p2})")

        # 地支六冲
        dz_chong_rules = {
            ("子", "午"): "子午冲", ("午", "子"): "子午冲",
            ("丑", "未"): "丑未冲", ("未", "丑"): "丑未冲",
            ("寅", "申"): "寅申冲", ("申", "寅"): "寅申冲",
            ("卯", "酉"): "卯酉冲", ("酉", "卯"): "卯酉冲",
            ("辰", "戌"): "辰戌冲", ("戌", "辰"): "辰戌冲",
            ("巳", "亥"): "巳亥冲", ("亥", "巳"): "巳亥冲"
        }

        for p1 in positions:
            for p2 in positions:
                pair = (bazi1[p1]["zhi"], bazi2[p2]["zhi"])
                if pair in dz_chong_rules:
                    dizhi_chong.append(f"{dz_chong_rules[pair]}({p1}-{p2})")

        # 五行互补分析
        wuxing1 = self._count_wuxing(bazi1)
        wuxing2 = self._count_wuxing(bazi2)

        weak1 = [k for k, v in wuxing1.items() if v <= 1]
        strong2 = [k for k, v in wuxing2.items() if v >= 3]
        complement = []
        for w in weak1:
            if w in strong2:
                complement.append(w)

        # 日柱配对分析
        day_gan1, day_gan2 = bazi1["day"]["gan"], bazi2["day"]["gan"]
        day_zhi1, day_zhi2 = bazi1["day"]["zhi"], bazi2["day"]["zhi"]

        # 日干生克关系
        wuxing_order = {"木": 0, "火": 1, "土": 2, "金": 3, "水": 4}
        wx1 = self.wuxing_gan[day_gan1]
        wx2 = self.wuxing_gan[day_gan2]
        diff = (wuxing_order[wx2] - wuxing_order[wx1]) % 5

        if diff == 1:
            rizhu_relation = f"{day_gan1}生{day_gan2}（相生）"
        elif diff == 4:
            rizhu_relation = f"{day_gan2}生{day_gan1}（相生）"
        elif diff == 2:
            rizhu_relation = f"{day_gan1}克{day_gan2}（相克）"
        elif diff == 3:
            rizhu_relation = f"{day_gan2}克{day_gan1}（相克）"
        else:
            rizhu_relation = "比和（同类）"

        # 计算合盘分数 (简单算法)
        score = 60
        score += min(len(tiangan_he) * 3, 15)
        score += min(len(dizhi_he) * 3, 15)
        score -= min(len(dizhi_chong) * 5, 15)
        score += len(complement) * 5
        score = max(0, min(100, score))

        return {
            "tiangan_he": list(set(tiangan_he)),
            "dizhi_he": list(set(dizhi_he)),
            "dizhi_chong": list(set(dizhi_chong)),
            "wuxing_complement": complement,
            "rizhu_relation": rizhu_relation,
            "score": score,
            "level": "上等" if score >= 80 else "中等" if score >= 60 else "下等"
        }

    # ==================== 择日系统 ====================

    def zeri_analysis(self, year: int, month: int, day: int, hour: int = 12, event_type: str = "") -> dict:
        """
        择日分析

        Args:
            year: 公历年份
            month: 月份
            day: 日期
            hour: 小时
            event_type: 事件类型 (结婚/搬家/开业/签约/动土)

        Returns:
            择日分析结果字典
        """
        # 计算该日的八字
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()

        day_gan = self.gan_list[lunar.getDayGanIndex()]
        day_zhi = self.zhi_list[lunar.getDayZhiIndex()]
        month_gan = self.gan_list[lunar.getMonthGanIndex()]
        month_zhi = self.zhi_list[lunar.getMonthZhiIndex()]

        # 十二建星 (以月支和日支推算)
        jianxing_list = ["建", "除", "满", "平", "定", "执", "破", "危", "成", "收", "开", "闭"]
        month_zhi_idx = self.zhi_order[month_zhi]
        day_zhi_idx = self.zhi_order[day_zhi]
        jianxing_idx = (day_zhi_idx - month_zhi_idx) % 12
        jianxing = jianxing_list[jianxing_idx]

        # 根据事件类型判断宜忌
        suitable = []
        unsuitable = []
        score = 50

        # 建星吉凶判断
        jianxing_yiji = {
            "建": (["出行", "上任"], ["嫁娶", "动土"]),
            "除": (["除旧", "清洁", "治病"], ["嫁娶", "安葬"]),
            "满": (["开业", "签约"], ["安葬", "动土"]),
            "平": (["平常事"], ["大事不宜"]),
            "定": (["订婚", "签约"], ["出行", "变动"]),
            "执": (["捕捉", "守成"], ["开业", "嫁娶"]),
            "破": (["破屋", "治病"], ["大事不宜"]),
            "危": (["安床", "祭祀"], ["出行", "动土"]),
            "成": (["签约", "开业", "嫁娶"], ["诉讼"]),
            "收": (["收获", "安葬"], ["开业", "出行"]),
            "开": (["开业", "签约", "出行"], ["安葬"]),
            "闭": (["安葬", "收藏"], ["开业", "出行"])
        }

        st, ust = jianxing_yiji.get(jianxing, ([], []))
        suitable.extend(st)
        unsuitable.extend(ust)

        # 根据事件类型评分
        event_scores = {
            "结婚": {"成": 20, "开": 15, "建": -10, "破": -20, "平": -10},
            "搬家": {"成": 15, "开": 15, "除": 10, "破": -15, "执": -10},
            "开业": {"满": 20, "成": 20, "开": 15, "破": -20, "收": -15},
            "签约": {"成": 20, "开": 15, "定": 10, "破": -20, "执": -10},
            "动土": {"成": 10, "除": 10, "开": 10, "破": -20, "建": -10}
        }

        if event_type in event_scores:
            score += event_scores[event_type].get(jianxing, 0)

        # 日柱天干判断
        if day_gan in ["甲", "乙"]:
            score += 5  # 木日生气

        score = max(0, min(100, score))

        return {
            "date": f"{year}-{month:02d}-{day:02d}",
            "day_bazi": f"{month_gan}{month_zhi} {day_gan}{day_zhi}",
            "jianxing": jianxing,
            "suitable": list(set(suitable)),
            "unsuitable": list(set(unsuitable)),
            "score": score,
            "level": "大吉" if score >= 80 else "吉" if score >= 60 else "平" if score >= 40 else "凶"
        }

    # ==================== 风水参考 ====================

    def fengshui_reference(self, bazi: Dict) -> dict:
        """
        基于八字的风水参考建议

        Args:
            bazi: 八字字典

        Returns:
            风水建议字典
        """
        wuxing_count = self._count_wuxing(bazi)
        day_gan = bazi["day"]["gan"]

        # 找出最旺和最弱的五行
        max_wuxing = max(wuxing_count, key=wuxing_count.get)
        min_wuxing = min(wuxing_count, key=wuxing_count.get)

        # 喜用神：偏弱或受克的五行（简化判断）
        # 通常日主弱的补日主，日主强的泄耗
        # 这里简化：最弱的为喜用
        xiyong = min_wuxing

        # 方位
        direction_map = {
            "木": ["东方", "东南"],
            "火": ["南方"],
            "土": ["中央", "西南", "东北"],
            "金": ["西方", "西北"],
            "水": ["北方"]
        }

        # 颜色
        color_map = {
            "木": ["青色", "绿色"],
            "火": ["红色", "紫色", "粉色"],
            "土": ["黄色", "棕色", "米色"],
            "金": ["白色", "金色", "银色"],
            "水": ["黑色", "蓝色", "灰色"]
        }

        # 数字
        number_map = {
            "木": [3, 8],
            "火": [2, 7],
            "土": [5, 0],
            "金": [4, 9],
            "水": [1, 6]
        }

        # 行业
        industry_map = {
            "木": ["教育", "文化", "出版", "纺织", "农林", "园艺"],
            "火": ["能源", "电力", "餐饮", "美容", "光学", "互联网"],
            "土": ["房地产", "建筑", "农业", "矿产", "陶瓷", "仓储"],
            "金": ["金融", "银行", "机械", "汽车", "五金", "珠宝"],
            "水": ["物流", "运输", "旅游", "水产", "饮料", "贸易"]
        }

        return {
            "day_gan": day_gan,
            "wuxing_balance": wuxing_count,
            "max_wuxing": max_wuxing,
            "min_wuxing": min_wuxing,
            "xiyong": xiyong,
            "lucky_direction": direction_map.get(xiyong, []),
            "lucky_colors": color_map.get(xiyong, []),
            "lucky_numbers": number_map.get(xiyong, []),
            "suitable_industries": industry_map.get(xiyong, []),
            "avoid_direction": direction_map.get(max_wuxing, [])
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
