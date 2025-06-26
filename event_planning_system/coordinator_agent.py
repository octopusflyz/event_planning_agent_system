"""
协调与质量控制Agent模块
负责管理各Agent的工作流程与依赖关系，
评估输出质量，进行必要的修正和协调，
确保系统整体输出的完整性和一致性。
"""

from event_planning_system.demand_parser_agent import DemandParserAgent
from event_planning_system.style_analysis_agent import StyleAnalysisAgent
from event_planning_system.event_planning_agent import EventPlanningAgent
from event_planning_system.visual_design_agent import VisualDesignAgent
from event_planning_system.copywriting_agent import CopywritingAgent

class CoordinatorAgent:
    def __init__(self, reference_data_path):
        self.demand_parser = DemandParserAgent()
        self.style_analyzer = StyleAnalysisAgent(reference_data_path)
        self.event_planner = EventPlanningAgent()
        self.visual_designer = VisualDesignAgent()
        self.copywriter = CopywritingAgent()

    def run(self, input_text):
        """
        运行整个多Agent协作流程
        :param input_text: 用户输入的非结构化活动需求文本
        :return: dict，包含完整的活动规划、主视觉设计（图片二进制）和宣传文案
        """
        # 1. 需求解析与推断
        demand_info = self.demand_parser.parse_and_infer(input_text)

        # 2. 风格分析
        style_guide = self.style_analyzer.get_style_guide()

        # 3. 活动规划设计
        event_plan = self.event_planner.design_event_plan(style_guide,demand_info)

        # 4. 主视觉设计
        main_visual = self.visual_designer.generate_main_visual(style_guide, demand_info)

        # 5. 文案创作
        copywriting = self.copywriter.generate_copywriting(style_guide, demand_info, event_plan)

        # 6. 质量控制与协调（简化示例，实际可扩展）
        # 这里可以添加对输出内容的检查和修正逻辑

        return {
            "活动需求信息": demand_info,
            "活动规划方案": event_plan,
            "主视觉设计图片": main_visual,
            "宣传文案": copywriting
        }
