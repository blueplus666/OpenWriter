# llm_adapters.py
# -*- coding: utf-8 -*-
import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from openai import OpenAI
import requests


def check_base_url(url: str) -> str:
    """
    处理base_url的规则：
    1. 如果url以#结尾，则移除#并直接使用用户提供的url
    2. 如果url已包含版本路径（如/v1/、/v4/），则保持原样
    3. 否则检查是否需要添加/v1后缀
    """
    import re

    url = url.strip()
    if not url:
        return url

    if url.endswith("#"):
        return url.rstrip("#").rstrip("/")

    if re.search(r"/v\d+/?$", url):
        return url.rstrip("/")

    if "/v1" not in url:
        url = url.rstrip("/") + "/v1"
    return url


class BaseLLMAdapter:
    """
    统一的 LLM 接口基类，为不同后端提供一致的方法签名。
    """

    def invoke(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement .invoke(prompt) method.")


class ZhipuAIAdapter(BaseLLMAdapter):
    """
    适配智谱AI (GLM) 接口
    官方文档: https://docs.bigmodel.cn/cn/guide/develop/http/introduction

    支持模型:
    - GLM-5: 最新旗舰基座模型
    - GLM-5-Turbo: 增强基座
    - GLM-4.7/4.6/4.5系列: 高性能模型
    - GLM-4系列: 稳定版本
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = base_url.rstrip("/") if base_url else "https://open.bigmodel.cn/api/paas/v4"
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=timeout
        )

    def invoke(self, prompt: str) -> str:
        try:
            full_url = f"{self.base_url}/chat/completions"
            logging.info(f"智谱AI调用 - URL: {full_url}, 模型: {self.model_name}")
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout,
            )
            if not response or not response.choices:
                logging.warning("智谱AI返回空响应")
                return ""
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"智谱AI API调用失败: {e}")
            import traceback
            logging.error(f"详细错误: {traceback.format_exc()}")
            raise e


class DeepSeekAdapter(BaseLLMAdapter):
    """
    适配 DeepSeek 接口
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        max_tokens: int,
        temperature: float = 0.7,
        timeout: Optional[int] = 600,
    ):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout,
        )

    def invoke(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from DeepSeekAdapter.")
            return ""
        return response.content


class VolcanoEngineAIAdapter(BaseLLMAdapter):
    """
    适配火山引擎 (豆包) 接口
    官方文档: https://www.volcengine.com/docs/82379/1330310

    免费额度:
    - 新用户: 5000万 Tokens 免费额度
    - Doubao-Lite 永久免费

    支持模型（2026年最新）:
    - Seed 2.0 系列: doubao-seed-2-0-pro/lite/mini/code-preview
    - Seed 1.8 系列: doubao-seed-1-8-251228
    - Seed 1.6 系列: doubao-seed-1-6-251015/lite/flash/vision
    - 1.5 系列: doubao-1-5-pro/lite/thinking/vision
    - DeepSeek 系列（火山方舟托管）

    API 地址: https://ark.cn-beijing.volces.com/api/v3/
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        max_tokens: int,
        temperature: float = 0.7,
        timeout: Optional[int] = 600,
    ):
        self.base_url = (
            base_url if base_url else "https://ark.cn-beijing.volces.com/api/v3/"
        )
        if not self.base_url.endswith("/"):
            self.base_url += "/"
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=self.base_url, api_key=self.api_key, timeout=timeout
        )

    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout,
            )
            if not response or not response.choices:
                logging.warning("No response from VolcanoEngineAIAdapter.")
                return ""
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"火山引擎API调用失败: {e}")
            return ""


class SiliconFlowAdapter(BaseLLMAdapter):
    """
    适配硅基流动接口
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        max_tokens: int,
        temperature: float = 0.7,
        timeout: Optional[int] = 600,
    ):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=self.base_url, api_key=self.api_key, timeout=timeout
        )

    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout,
            )
            if not response or not response.choices:
                logging.warning("No response from SiliconFlowAdapter.")
                return ""
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"硅基流动API调用失败: {e}")
            return ""


class OllamaAdapter(BaseLLMAdapter):
    """
    适配 Ollama 本地接口
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        max_tokens: int,
        temperature: float = 0.7,
        timeout: Optional[int] = 600,
    ):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key if api_key else "ollama"
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout,
        )

    def invoke(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from OllamaAdapter.")
            return ""
        return response.content


class AliBailianAdapter(BaseLLMAdapter):
    """
    适配阿里云百炼接口 (OpenAI兼容)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        max_tokens: int,
        temperature: float = 0.7,
        timeout: Optional[int] = 600,
    ):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout,
        )

    def invoke(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from AliBailianAdapter.")
            return ""
        return response.content


def create_llm_adapter(
    interface_format: str,
    base_url: str,
    model_name: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> BaseLLMAdapter:
    """
    工厂函数：根据 interface_format 返回不同的适配器实例。
    支持的接口格式：
    - 智谱AI (ZhipuAI)
    - DeepSeek
    - 火山引擎 (VolcanoEngine)
    - 硅基流动 (SiliconFlow)
    - 阿里云百炼 (AliBailian)
    - Ollama (本地部署)
    """
    fmt = interface_format.strip().lower()
    if fmt == "deepseek":
        return DeepSeekAdapter(
            api_key, base_url, model_name, max_tokens, temperature, timeout
        )
    elif fmt == "火山引擎":
        return VolcanoEngineAIAdapter(
            api_key, base_url, model_name, max_tokens, temperature, timeout
        )
    elif fmt == "硅基流动":
        return SiliconFlowAdapter(
            api_key, base_url, model_name, max_tokens, temperature, timeout
        )
    elif fmt == "阿里云百炼":
        return AliBailianAdapter(
            api_key, base_url, model_name, max_tokens, temperature, timeout
        )
    elif fmt == "ollama":
        return OllamaAdapter(
            api_key, base_url, model_name, max_tokens, temperature, timeout
        )
    elif "智谱" in fmt or "zhipu" in fmt or fmt == "glm":
        return ZhipuAIAdapter(
            api_key, base_url, model_name.lower(), max_tokens, temperature, timeout
        )
    else:
        raise ValueError(f"Unknown interface_format: {interface_format}")