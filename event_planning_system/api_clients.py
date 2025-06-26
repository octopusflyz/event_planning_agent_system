"""
外部API调用客户端模块
封装图片生成、文本处理、规则逻辑生成等外部API调用
"""

import requests

import base64
import requests

class ImageGenerationClient:
    def __init__(self):
        self.api_url = "https://llmapi.lcpu.dev/v1/images/generations"
        self.api_key = "YOUR_API_KEY"

    def generate_image(self, prompt, model="flux-dev", size="1024x1024"):
        """
        调用外部图片生成API
        :param prompt: 生成提示词
        :param model: 模型名称
        :param size: 图片尺寸
        :return: 图片二进制数据列表
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": model,
            "prompt": prompt,
            "size": size
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=300)
            if response.status_code == 200:
                res_json = response.json()
                images_data = []
                for item in res_json.get("data", []):
                    img_url = item.get("url")
                    if img_url:
                        img_response = requests.get(img_url, timeout=30)
                        if img_response.status_code == 200:
                            images_data.append(img_response.content)
                return images_data
            else:
                print(f"图片生成API请求失败，状态码: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"图片生成API请求异常: {e}")
            return None

    def generate_image_with_elements(self, prompt, images, model="doubao-1.5-vision-pro-250328", size="1024x1024"):
        """
        调用外部图片生成API，传入提示词和必要元素图片（PNG格式二进制）
        :param prompt: 生成提示词
        :param images: List[bytes] PNG格式图片二进制数据列表
        :param model: 模型名称
        :param size: 图片尺寸
        :return: 图片二进制数据列表
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        # 将图片二进制转为base64字符串
        base64_images = [base64.b64encode(img).decode('utf-8') for img in images]

        data = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "elements_images": base64_images  # 假设API支持此字段传递图片
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=300)
            if response.status_code == 200:
                res_json = response.json()
                images_data = []
                for item in res_json.get("data", []):
                    img_url = item.get("url")
                    if img_url:
                        img_response = requests.get(img_url, timeout=30)
                        if img_response.status_code == 200:
                            images_data.append(img_response.content)
                return images_data
            else:
                print(f"图片生成API请求失败，状态码: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"图片生成API请求异常: {e}")
            return None

class TextProcessingClient:
    def __init__(self, model="deepseek-chat"):
        """
        初始化文本处理客户端，支持选择不同的LLM模型
        :param model: 使用的模型名称，默认使用deepseek-chat
        """
        self.api_url = "https://llmapi.lcpu.dev/v1/chat/completions"
        self.api_key = "YOUR_API_KEY"
        self.model = model

    def refine_text(self, text, style, style_reference="", prompt1=""):
        """
        调用文本处理API进行润色和风格调整，参考提供的文本风格
        :param text: 原始文本
        :param style: 目标风格描述
        :param style_reference: 参考文本风格内容
        :param prompt1: 调用时传入的自定义提示词
        :return: 润色后的文本
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        common_prompt = f"请模仿以下文本风格进行润色，请保证格式清晰明了，风格描述：{style}\n参考文本风格内容：{style_reference}\n需要润色的文本：{text}"
        full_prompt = prompt1 + "\n" + common_prompt if prompt1 else common_prompt
        messages = [
            {"role": "system", "content": "你是一个专业的文案润色助手。"},
            {"role": "user", "content": full_prompt}
        ]
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=300)
            if response.status_code == 200:
                res_json = response.json()
                choices = res_json.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", text)
                else:
                    return text
            else:
                print(f"文本处理API请求失败，状态码: {response.status_code}")
                return text
        except requests.exceptions.RequestException as e:
            print(f"文本处理API请求异常: {e}")
            return text

class RuleGenerationClient:
    def __init__(self, model="deepseek-reasoner"):
        """
        初始化规则生成客户端，支持选择不同的LLM模型
        :param model: 使用的模型名称，默认使用deepseek-reasoner
        """
        self.api_url = "https://llmapi.lcpu.dev/v1/chat/completions"
        self.api_key = "YOUR_API_KEY"
        self.model = model

    def generate_rules(self, event_type, requirements):
        """
        调用规则逻辑生成API，使用指定LLM模型生成规则文本
        :param event_type: 活动类型
        :param requirements: 规则需求描述
        :return: 生成的规则文本
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        messages = [
            {"role": "system", "content": "你是一个专业的活动规则设计助手。"},
            {"role": "user", "content": f"请为活动类型'{event_type}'设计规则，要求如下：{requirements}"}
        ]
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=300)
            if response.status_code == 200:
                res_json = response.json()
                choices = res_json.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                else:
                    return ""
            else:
                print(f"规则生成API请求失败，状态码: {response.status_code}")
                return ""
        except requests.exceptions.RequestException as e:
            print(f"规则生成API请求异常: {e}")
            return ""
