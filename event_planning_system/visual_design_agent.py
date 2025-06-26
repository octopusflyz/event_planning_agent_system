"""
主视觉设计Agent模块
负责根据活动类型和风格指南，调用外部图片生成API，
生成符合大信科风格的活动主视觉设计（png格式）。
"""

from event_planning_system.api_clients import ImageGenerationClient

import os
import io
from PIL import Image

class VisualDesignAgent:
    def __init__(self):
        self.image_client = ImageGenerationClient()
        self.necessary_elements_path = "./数据集-图片/必要元素"

    def _load_necessary_element_images(self):
        """
        加载必要元素文件夹中的所有图片，转换为PNG格式的二进制数据
        :return: List[bytes] PNG格式图片的二进制数据列表
        """
        return self._load_images_from_folder(self.necessary_elements_path)

    def _load_images_from_folder(self, folder_path):
        """
        加载指定文件夹中的所有图片，转换为PNG格式的二进制数据
        :param folder_path: 文件夹路径
        :return: List[bytes] PNG格式图片的二进制数据列表
        """
        images_data = []
        if not os.path.exists(folder_path):
            print(f"文件夹不存在: {folder_path}")
            return images_data
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            try:
                with Image.open(filepath) as img:
                    # 转换为PNG格式
                    with io.BytesIO() as output:
                        img.convert("RGBA").save(output, format="PNG")
                        images_data.append(output.getvalue())
            except Exception as e:
                print(f"加载图片{filepath}失败: {e}")
        return images_data

    def generate_main_visual(self, style_guide, demand_info):
        """
        生成主视觉设计
        :param style_guide: dict，风格指南
        :param demand_info: dict，活动需求信息
        :return: bytes，生成的图片二进制数据（PNG格式）
        """
        # 根据风格指南和活动信息构造提示词，加入必要元素提示
        prompt = self._build_prompt(style_guide, demand_info)

        # 加载必要元素图片
        necessary_images = self._load_necessary_element_images()

        # 加载活动类型对应文件夹的图片
        activity_type = demand_info.get("活动类型", "")
        activity_images = []
        if activity_type:
            activity_folder = os.path.join("./数据集-图片", activity_type)
            activity_images = self._load_images_from_folder(activity_folder)

        # 合并必要元素图片和活动类型图片
        all_images = necessary_images + activity_images

        # 调用图片生成API，传入所有图片
        images = self.image_client.generate_image_with_elements(prompt, all_images, model="flux-dev", size="1024x1024")

        if images and len(images) > 0:
            # 生成后处理，透明叠加另一张图片到生成图片的右下角和左上角
            base_img_data = images[0]
            try:
                result_img_data = self._process_overlays(base_img_data, activity_type)
                return result_img_data
            except Exception as e:
                print(f"生成后叠加图片失败: {e}")
                return base_img_data
        else:
            return None

    def _process_overlays(self, base_img_data, activity_type=None):
        """
        处理生成图片的叠加操作，调用_overlay_image函数实现叠加
        :param base_img_data: bytes，生成图片的二进制数据
        :param activity_type: str，活动类型，用于判断叠加图片
        :return: bytes，叠加后的图片二进制数据
        """
        with Image.open(io.BytesIO(base_img_data)) as base_img:
            base_img = base_img.convert("RGBA")

            # 根据活动类型选择右下角叠加图片
            if activity_type == "晚会类":
                overlay_filename = "ball.png"
            else:
                overlay_filename = "lion.png"

            overlay_path = os.path.join("./数据集-图片/必要元素", overlay_filename)
            self._overlay_image(base_img, overlay_path, scale=0.3, position="bottom_right")

            # 左上角叠加logo
            logo_path = os.path.join("./数据集-图片/必要元素", "logo.png")
            self._overlay_image(base_img, logo_path, scale=0.3, position="top_left")

            # 保存到字节流
            with io.BytesIO() as output:
                base_img.save(output, format="PNG")
                result_img_data = output.getvalue()
        return result_img_data

    def _overlay_image(self, base_img, overlay_path, scale=0.2, position="bottom_right"):
        """
        透明叠加图片到基底图片的指定位置

        :param base_img: PIL.Image对象，基底图片，必须为RGBA模式
        :param overlay_path: str，叠加图片文件路径
        :param scale: float，叠加图片相对于基底图片宽度的缩放比例，范围0~1
        :param position: str，叠加位置，支持 "top_left", "top_right", "bottom_left", "bottom_right"
        """
        try:
            with Image.open(overlay_path) as overlay_img:
                overlay_width = int(base_img.width * scale)
                overlay_height = int(overlay_img.height * (overlay_width / overlay_img.width))
                overlay_img = overlay_img.resize((overlay_width, overlay_height), Image.Resampling.LANCZOS).convert("RGBA")

                if position == "top_left":
                    pos = (10, 10)
                elif position == "top_right":
                    pos = (base_img.width - overlay_width - 10, 10)
                elif position == "bottom_left":
                    pos = (10, base_img.height - overlay_height - 10)
                else:  # bottom_right
                    pos = (base_img.width - overlay_width - 10, base_img.height - overlay_height - 10)

                base_img.paste(overlay_img, pos, overlay_img)
        except Exception as e:
            print(f"叠加图片失败({overlay_path}): {e}")

    def _build_prompt(self, style_guide, demand_info):
        """
        构造图片生成提示词，要求必须包含必要元素图片中的元素
        """
        visual_style = style_guide.get("视觉风格", {})
        colors = ",".join(visual_style.get("配色方案", []))
        activity_type = demand_info.get("活动类型", "活动")
        theme = demand_info.get("主题方向", "主题")

        # 根据活动类型选择不同的元素描述
        if activity_type == "晚会类":
            elements = "彩灯，舞台，烟花，欢庆气氛"
        elif activity_type == "比赛类":
            elements = "奖杯，赛道，计算机，代码"
        elif activity_type == "讲座类":
            elements = "讲台，计算机，听众，学术"
        elif activity_type == "活动类":
            elements = "气球，公园，书籍, AI"
        else:
            elements = ",".join(visual_style.get("图形元素", []))

        base_prompt = (f"设计一张符合北京大学信息科学技术学院风格的{activity_type}主视觉，"
                       f"主题为{theme}，配色方案选择红黄色调或者蓝白色调{colors}，"
                       f"包含元素有{elements}，北京大学灰色的九层高中式风格博雅塔作为背景，风格简洁高级有趣，如果你要在图片中包含字符，只能是{theme}或者‘PKU’或者‘EECS’。")

        # 加入必要元素提示
        necessary_elements_prompt = "请将生成的元素居中摆放，要有北京大学特色，兼具计算机科学的现代科技感，又有中国古典文化韵味"

        prompt = base_prompt + necessary_elements_prompt
        return prompt
