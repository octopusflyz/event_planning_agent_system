"""
需求解析与推断Agent模块
负责解析用户输入的非结构化活动需求文本，
提取显性信息，推断并补全隐性信息，
形成完整的活动需求方案。
"""

import re

class DemandParserAgent:
    def __init__(self):
        pass

    def parse_and_infer(self, input_text):
        """
        解析输入文本，提取显性信息，推断隐性信息
        :param input_text: 用户输入的非结构化文本
        :return: dict，包含完整的活动需求信息
        """
        # 简单示例：用正则和关键词提取显性信息
        info = {}

        # 提取活动类型（示例关键词，按照优先级搜索）
        if re.search(r"比赛|竞赛|挑战赛|马拉松|杯", input_text):
            info["活动类型"] = "比赛类"
        elif re.search(r"讲座|论坛|辅导|茶话会|学术", input_text):
            info["活动类型"] = "讲座类"
        elif re.search(r"新年|毕业|迎新", input_text):
            info["活动类型"] = "晚会类"
        elif re.search(r"活动|联谊|节", input_text):
            info["活动类型"] = "活动类"
        else:
            info["活动类型"] = "其他"

        # 提取主题方向（示例）
        theme_match = re.search(r"大模型|AI|人工智能|机器学习", input_text)
        info["主题方向"] = theme_match.group(0) if theme_match else "未知"

        # 识别“安排”或“时间”字样，取其后面一句话加入时间安排
        arrange_match = re.search(r"(安排|时间)[^\n。]*[。]([^\n。]+)[。]?", input_text)
        if arrange_match:
            info["时间安排"] = arrange_match.group(2)
        else:
            info["时间安排"] = "待定"

        # 识别“目标”或“目的”或“旨在”字样，取其后面一句话加入活动主旨
        purpose_match = re.search(r"(目标|目的|旨在)[^\n。]*[。]([^\n。]+)[。]?", input_text)
        if purpose_match:
            info["活动主旨"] = purpose_match.group(2)
        else:
            info["活动主旨"] = "未明确说明"


        # 识别“想法”字样，取其后面一句话加入初步构想
        idea_match = re.search(r"想法[^\n。]*[。]([^\n。]+)[。]?", input_text)
        if idea_match:
            info["初步构想"] = idea_match.group(1)
        else:
            info["初步构想"] = input_text[:100] + "..."

        # 新增规则：识别讲稿或主持词关键词，标记需要生成讲稿文本
        if re.search(r"讲稿|主持词", input_text):
            info["需要讲稿"] = True
        else:
            info["需要讲稿"] = False

        # 去除所有字段中的换行符，避免传递转义换行符
        for key in info:
            if isinstance(info[key], str):
                info[key] = info[key].replace("\\n", "").replace("\n", "")

        # 推断隐性信息（示例）
        info["目标受众"] = "北京大学信息科学技术学院学生及相关人员"
        info["活动规模"] = "人数（50-200人）"
        info["可能合作方"] = "XX公司、XX企业"

        return info
