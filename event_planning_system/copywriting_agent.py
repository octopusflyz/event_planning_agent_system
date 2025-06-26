"""
文案创作Agent模块
负责根据活动需求和风格指南，生成符合大信科语调和特色的宣传文案，
包括微信公众号推送稿、邮件通知、短文本宣传语和社交媒体分享版本。
"""

import os
from glob import glob
from event_planning_system.api_clients import TextProcessingClient

class CopywritingAgent:
    def __init__(self, reference_data_path="./数据集-推送"):
        self.text_client = TextProcessingClient()
        self.reference_data_path = reference_data_path

    def generate_copywriting(self, style_guide, demand_info, event_plan):
        """
        生成全套宣传文案
        :param style_guide: dict，风格指南
        :param demand_info: dict，活动需求信息
        :param event_plan: dict，活动规划方案
        :return: dict，包含不同版本的宣传文案
        """
        # 构造基础文案内容
        base_content = self._build_base_content(demand_info, event_plan)

        # 根据活动类型加载对应参考文档内容作为风格参考
        activity_type = demand_info.get("活动类型", "其他")
        style_reference = self._load_reference_docs(activity_type)

        # 根据风格指南调整文案风格
        style = style_guide.get("文案风格", {}).get("语言风格", "正式")

        #prompt设计
        prompt_1="请根据我提供的base_content，写一篇微信公众号推送稿，风格请模仿北京大学信息科学技术学院大信科微信公众号的写作风格，亲切有趣可添加表情emoji"
        prompt_2="请根据我提供的base_content，写一篇邮件通知文本，风格参考常见高校邮件通知模板，正式严谨。"
        prompt_3="请根据我提供的base_content，写一篇短文本宣传语，能准确提炼活动内容和特色，宣传语概括性好，且语言具有感染力。"
        prompt_4="请根据我提供的base_content，写一篇社交媒体分享文本，风格请模仿北京大学信息科学技术学院官网的推文，语言亲切的同时，体现北京大学的文化底蕴。"

        # 调用文本处理API进行润色和风格调整，传入风格参考
        wechat_article = self.text_client.refine_text(base_content["微信公众号推送稿"], style, style_reference,prompt_1)
        email_notice = self.text_client.refine_text(base_content["邮件通知版本"], style, style_reference,prompt_2)
        short_text = self.text_client.refine_text(base_content["短文本宣传语"], style, style_reference,prompt_3)
        social_media = self.text_client.refine_text(base_content["社交媒体分享版本"], style, style_reference,prompt_4)

        result = {
            "微信公众号推送稿": wechat_article,
            "邮件通知版本": email_notice,
            "短文本宣传语": short_text,
            "社交媒体分享版本": social_media
        }

        # 如果需求中标记需要讲稿，单独生成讲稿文本
        if demand_info.get("需要讲稿", True):
            prompt_speech = "请根据我提供的base_content，写一篇活动讲稿或主持词，语言正式且富有感染力。"
            speech_text = self.text_client.refine_text(base_content["微信公众号推送稿"], style, style_reference, prompt_speech)
            result = {
            "微信公众号推送稿": wechat_article,
            "邮件通知版本": email_notice,
            "短文本宣传语": short_text,
            "社交媒体分享版本": social_media,
            "讲稿/主持词":speech_text
            }

        return result

    def _build_base_content(self, demand_info, event_plan):
        """
        构造基础文案内容模板
        """
        title = f"{demand_info.get('主题方向', '活动')}精彩来袭！"
        intro = f"欢迎参加由北京大学信息科学技术学院举办的{demand_info.get('活动类型', '活动')}。"
        body = f"本次活动的详细规划如下：{event_plan}"
        conclusion = "期待您的积极参与，共同推动大信科的发展！"

        wechat_article = f"{title}\n\n{intro}\n\n{body}\n\n{conclusion}"
        email_notice = f"尊敬的师生，您好！\n\n{intro}\n\n{body}\n\n{conclusion}"
        short_text = f"{title}\n\n{intro}\n\n{body}\n\n，欢迎报名参加！"
        social_media = f"【{title}】{intro}{body},详情请关注学院公众号。"

        return {
            "微信公众号推送稿": wechat_article,
            "邮件通知版本": email_notice,
            "短文本宣传语": short_text,
            "社交媒体分享版本": social_media
        }

    def _load_reference_docs(self, activity_type):
        """
        读取对应活动类型文件夹下的所有txt和Word文档内容，转换为JSON结构化文本作为风格参考
        Word文档使用python-docx库解析
        """
        import os
        import json
        from glob import glob
        from docx import Document

        folder_path = os.path.join(self.reference_data_path, activity_type)
        if not os.path.exists(folder_path):
            return ""

        texts = []

        # 读取txt文件
        txt_files = glob(os.path.join(folder_path, "*.txt"))
        for txt_file in txt_files:
            try:
                with open(txt_file, "r", encoding="utf-8") as f:
                    content = f.read()
                texts.append({"type": "txt", "filename": os.path.basename(txt_file), "content": content})
            except Exception as e:
                print(f"读取文档 {txt_file} 失败: {e}")

        # 读取Word文档
        docx_files = glob(os.path.join(folder_path, "*.docx"))
        for docx_file in docx_files:
            try:
                doc = Document(docx_file)
                full_text = []
                for para in doc.paragraphs:
                    full_text.append(para.text)
                content = "\n".join(full_text)
                texts.append({"type": "docx", "filename": os.path.basename(docx_file), "content": content})
            except Exception as e:
                print(f"读取Word文档 {docx_file} 失败: {e}")

        # 转换为JSON字符串
        try:
            json_text = json.dumps(texts, ensure_ascii=False)
        except Exception as e:
            print(f"转换为JSON失败: {e}")
            json_text = ""

        return json_text
