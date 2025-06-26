"""
活动规划与设计Agent模块
负责根据活动类型和需求，设计详细的活动方案，
包括赛题设计、规则说明、评分标准、流程安排等。
"""

from event_planning_system.api_clients import RuleGenerationClient, TextProcessingClient

class EventPlanningAgent:
    def __init__(self):
        self.rule_client = RuleGenerationClient()
        self.text_client = TextProcessingClient()

    def design_event_plan(self, style_guide,demand_info):
        """
        根据需求信息设计详细活动方案
        :param demand_info: dict，完整的活动需求信息
        :return: dict，包含详细的活动规划方案
        """
        plan = {}

        # 根据风格指南调整文案风格
        style = style_guide.get("文案风格", {}).get("语言风格", "正式")
        
        # 示例：比赛类型设计方案
        if demand_info.get("活动类型") == "比赛类":
            # 调用规则生成API生成赛事规则和评分标准
            requirements = "基于给定数据集和代码，设计调参赛的规则和评分标准。"
            rules = self.rule_client.generate_rules(demand_info.get("活动类型"), requirements)
            plan["赛事规则"] = rules if rules else "参赛者需基于给定数据集和代码进行调参，提交最终模型。"
            plan["评分标准"] = "根据模型性能指标（准确率、召回率等）综合评分。"
            plan["流程设计"] = "报名->初赛->复赛->决赛->颁奖典礼"
            plan["时间安排"] = "4月下旬预热，5月中旬总结"

        # 示例：讲座类型设计方案
        elif demand_info.get("活动类型") == "讲座类":
            # 调用规则生成API生成讲座流程
            requirements = "基于讲座主题和目标听众，设计讲座的流程和安排。"
            rules = self.rule_client.generate_rules(demand_info.get("活动类型"), requirements)
            plan["讲座流程"] = rules if rules else "讲座包含开场介绍、主题演讲、互动问答、总结致辞等环节。"
            plan["讲座安排"] = "根据讲座主题邀请专家或学者进行演讲，并安排互动问答环节以增强参与感。"
            plan["流程设计"] = "开场介绍->主题演讲->互动问答->总结致辞"
            plan["时间安排"] = "根据讲师和场地情况，时间待定，建议提前1个月确认"

        # 示例：晚会类型设计方案
        elif demand_info.get("活动类型") == "晚会类":
            # 调用规则生成API生成晚会流程
            requirements = "基于给定主题和活动需求，设计晚会的流程和节目安排。"
            rules = self.rule_client.generate_rules(demand_info.get("活动类型"), requirements)
            plan["晚会流程"] = rules if rules else "晚会节目分为多个环节，包含开场、表演、互动环节、抽奖、闭幕等。"
            plan["节目安排"] = "根据主题选择合适的表演节目，如歌舞、话剧、小品等，确保内容丰富多样。"
            plan["流程设计"] = "开场->节目表演->互动环节->抽奖->闭幕"
            plan["时间安排"] = "12月初准备，12月中旬举办"

        # 示例：活动类型设计方案
        elif demand_info.get("活动类型") == "活动类":
            # 调用规则生成API生成活动流程
            requirements = "基于活动目标和参与人群，设计活动的具体流程和安排。"
            rules = self.rule_client.generate_rules(demand_info.get("活动类型"), requirements)
            plan["活动流程"] = rules if rules else "活动流程包含开场、主要环节、互动环节、总结等。"
            plan["活动安排"] = "根据活动性质选择合适的环节和活动形式，如团体互动、个人挑战、知识分享等。"
            plan["流程设计"] = "开场->主要活动->互动环节->总结"
            plan["时间安排"] = "活动开始前1个月制定时间表，并根据场地、嘉宾安排调整"

        else:
            plan["活动方案"] = "根据具体需求定制"

        # 补充其他规划细节
        plan["资源需求"] = "场地、设备、人员支持等"

        import json
        # 构造基础内容字符串
        demand_info_text = self._build_base_content(demand_info, "活动需求信息汇总")
        plan_text = self._build_base_content(plan, "活动规划方案")
        style = "正式"

        # 给模型输入的prompt
        prompt_a = "你需要根据我提供的基本信息，写一个活动需求信息汇总。请在第一行用标题写出‘活动需求信息汇总’，正文部分按照信息收集的常见格式,按照我提供的信息分点分段列出信息，请确保语言顺畅，格式清晰易懂，注意文本里面分段之间要换行输出。"
        prompt_b = "你需要根据我提供的基本信息，写一个活动规划方案。请在第一行用标题写出‘活动规划方案’，正文部分按照活动规划的常见格式，按照我提供的信息分点分段列出信息，请确保语言顺畅，格式清晰易懂，注意文本里面分段之间要换行输出。"

        # 读取对应活动类型的参考文档内容作为风格参考
        activity_type = demand_info.get("活动类型", "其他")
        style_reference = self._load_reference_docs(activity_type)

        refined_demand_info = self.text_client.refine_text(demand_info_text, style, style_reference, prompt_a)
        refined_plan = self.text_client.refine_text(plan_text, style, style_reference, prompt_b)

        return {
            "润色后的需求信息": refined_demand_info,
            "润色后的活动规划方案": refined_plan
        }

    def _build_base_content(self, info_dict, title):
        """
        构造基础内容字符串，格式化为标题加分点信息，适用于活动需求或规划
        :param info_dict: dict，信息字典
        :param title: str，标题
        :return: str，格式化的多行字符串
        """
        lines = [title, ""]
        for key, value in info_dict.items():
            lines.append(f"- {key}：{value}")
        return "\n".join(lines)

    def _load_reference_docs(self, activity_type, reference_data_path="./数据集-推送"):
        """
        读取对应活动类型文件夹下的所有txt文档内容，base64编码后拼接成字符串作为风格参考
        """
        import os
        import base64
        from glob import glob

        folder_path = os.path.join(reference_data_path, activity_type)
        if not os.path.exists(folder_path):
            return ""

        encoded_texts = []
        doc_files = glob(os.path.join(folder_path, "*.txt"))
        for doc_file in doc_files:
            try:
                with open(doc_file, "rb") as f:
                    content = f.read(100)  # 只读取文件前100个字节
                encoded_content = base64.b64encode(content).decode('utf-8')
                encoded_texts.append(encoded_content)
            except Exception as e:
                print(f"读取文档 {doc_file} 失败: {e}")

        return "\n".join(encoded_texts)
