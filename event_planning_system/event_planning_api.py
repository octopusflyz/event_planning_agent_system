"""
事件策划系统主接口
提供单次输入调用多Agent协作系统的接口，
完成活动需求解析、规划设计、主视觉生成和文案创作，
并将结果保存到本地文件。
"""

import os
import base64

from event_planning_system.coordinator_agent import CoordinatorAgent

REFERENCE_DATA_PATH = "./数据集-推送"  # 参考资料路径，可根据实际调整

def save_image(image_bytes, save_path):
    """
    保存图片二进制数据到文件
    """
    with open(save_path, "wb") as f:
        f.write(image_bytes)

def save_text(text, save_path):
    """
    保存文本内容到文件，自动将字符串中的转义换行符\n替换为真实换行
    """
    import os
    dir_path = os.path.dirname(save_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text.replace("\\n", "\n"))

def main():
    print("欢迎使用大信科活动规划与宣传智能系统：\n")
    input_text = input("请输入活动需求描述（自然语言，输入exit退出）：\n")
    if input_text.strip().lower() == "exit":
        print("退出程序。")
        return

    coordinator = CoordinatorAgent(REFERENCE_DATA_PATH)
    print("系统正在处理，请稍候...（预计等待3-4分钟，调用外部API时间较长）")

    # 这里增加style_guide参数示例，实际可根据需求动态生成或传入
    style_guide = {
        "文案风格": {
            "语言风格": "正式"
        }
    }

    result = coordinator.run(input_text)

    # 保存活动需求信息
    demand_info_path = "output_活动需求信息.txt"
    save_text(str(result["活动需求信息"]), demand_info_path)
    print(f"活动需求信息已保存到 {demand_info_path}")

    # 保存活动规划方案
    event_plan_path = "output_活动规划方案.txt"
    save_text(str(result["活动规划方案"]), event_plan_path)
    print(f"活动规划方案已保存到 {event_plan_path}")

    # 保存主视觉设计图片
    if result["主视觉设计图片"]:
        image_path = "output_主视觉设计.png"
        save_image(result["主视觉设计图片"], image_path)
        print(f"主视觉设计图片已保存到 {image_path}")
    else:
        print("主视觉设计图片生成失败。")

    # 保存宣传文案
    copywriting = result["宣传文案"]
    for key, content in copywriting.items():
        filename = f"output_宣传文案_{key}.txt"
        save_text(content, filename)
        print(f"{key}已保存到 {filename}")

    # 如果有讲稿/主持词，单独保存
    speech_key = "讲稿/主持词"
    if speech_key in copywriting:
        speech_filename = f"output_宣传文案_{speech_key}.txt"
        # 确保目录存在
        import os
        dir_path = os.path.dirname(speech_filename)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        save_text(copywriting[speech_key], speech_filename)
        print(f"{speech_key}已保存到 {speech_filename}")

    print("所有输出已完成。")

if __name__ == "__main__":
    main()
