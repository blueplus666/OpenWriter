# embedding_adapters.py
# -*- coding: utf-8 -*-
import logging
import traceback
from typing import List
import requests
from langchain_openai import OpenAIEmbeddings


def ensure_openai_base_url_has_v1(url: str) -> str:
    """
    若用户输入的 url 不包含 '/v1'，则在末尾追加 '/v1'。
    """
    import re

    url = url.strip()
    if not url:
        return url
    if not re.search(r"/v\d+$", url):
        if "/v1" not in url:
            url = url.rstrip("/") + "/v1"
    return url


class BaseEmbeddingAdapter:
    """
    Embedding 接口统一基类
    """

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_query(self, query: str) -> List[float]:
        raise NotImplementedError


class OpenAIEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 OpenAIEmbeddings（或兼容接口）的适配器
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        self._embedding = OpenAIEmbeddings(
            openai_api_key=api_key,
            openai_api_base=ensure_openai_base_url_has_v1(base_url),
            model=model_name,
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embedding.embed_documents(texts)

    def embed_query(self, query: str) -> List[float]:
        return self._embedding.embed_query(query)


class OllamaEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    Ollama 本地 Embedding 接口
    """

    def __init__(self, model_name: str, base_url: str):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            vec = self._embed_single(text)
            embeddings.append(vec)
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        return self._embed_single(query)

    def _embed_single(self, text: str) -> List[float]:
        """
        调用 Ollama 本地服务 /api/embeddings 接口
        """
        url = self.base_url.rstrip("/")
        if "/api/embeddings" not in url:
            if "/api" in url:
                url = f"{url}/embeddings"
            else:
                if "/v1" in url:
                    url = url[: url.index("/v1")]
                url = f"{url}/api/embeddings"

        data = {"model": self.model_name, "prompt": text}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            if "embedding" not in result:
                raise ValueError("No 'embedding' field in Ollama response.")
            return result["embedding"]
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Ollama embeddings request error: {e}\n{traceback.format_exc()}"
            )
            return []


class SiliconFlowEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 SiliconFlow 的 embedding 适配器
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = "https://" + base_url
        self.url = base_url if base_url else "https://api.siliconflow.cn/v1/embeddings"
        self.api_key = api_key
        self.model_name = model_name

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            vec = self._embed_single(text)
            embeddings.append(vec)
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        return self._embed_single(query)

    def _embed_single(self, text: str) -> List[float]:
        payload = {"model": self.model_name, "input": text, "encoding_format": "float"}
        try:
            response = requests.post(
                self.url, json=payload, headers=self._get_headers()
            )
            response.raise_for_status()
            result = response.json()
            if not result or "data" not in result or not result["data"]:
                logging.error(f"Invalid response format from SiliconFlow API: {result}")
                return []
            return result["data"][0].get("embedding", [])
        except requests.exceptions.RequestException as e:
            logging.error(f"SiliconFlow API request failed: {str(e)}")
            return []
        except (KeyError, IndexError, ValueError, TypeError) as e:
            logging.error(f"Error parsing SiliconFlow API response: {str(e)}")
            return []


class ZhipuAIEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    适配智谱AI Embedding 接口
    官方文档: https://docs.bigmodel.cn/cn/guide/embeddings/Embedding-Quickstart

    API端点: https://open.bigmodel.cn/api/paas/v4/embeddings
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        if not base_url:
            base_url = "https://open.bigmodel.cn/api/paas/v4"
        base_url = base_url.rstrip("/")
        if not base_url.endswith("/embeddings"):
            base_url = base_url + "/embeddings"
        self.url = base_url
        self.api_key = api_key
        self.model_name = model_name

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            vec = self._embed_single(text)
            embeddings.append(vec)
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        return self._embed_single(query)

    def _embed_single(self, text: str) -> List[float]:
        payload = {"model": self.model_name, "input": text}
        try:
            logging.info(f"智谱Embedding调用 - URL: {self.url}")
            logging.info(f"智谱Embedding请求 - payload: {payload}")
            logging.info(f"智谱Embedding请求 - headers: {self._get_headers()}")
            response = requests.post(
                self.url, json=payload, headers=self._get_headers(), timeout=30
            )
            logging.info(f"智谱Embedding响应 - status: {response.status_code}")
            logging.info(f"智谱Embedding响应 - body: {response.text}")
            if response.status_code != 200:
                logging.error(
                    f"智谱Embedding API错误: {response.status_code} - {response.text}"
                )
                return []
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                return result["data"][0].get("embedding", [])
            logging.warning(f"智谱Embedding返回格式异常: {result}")
            return []
        except requests.exceptions.RequestException as e:
            logging.error(f"智谱Embedding请求失败: {str(e)}")
            return []
        except (KeyError, IndexError, ValueError, TypeError) as e:
            logging.error(f"智谱Embedding解析响应失败: {str(e)}")
            return []


class VolcanoEngineEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    适配火山引擎 Embedding 接口
    官方文档: https://www.volcengine.com/docs/6561/1816214
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = "https://" + base_url
        self.url = (
            base_url
            if base_url
            else "https://open.volcengineapi.com/api/paas/v1/embeddings"
        )
        self.api_key = api_key
        self.model_name = model_name

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            vec = self._embed_single(text)
            embeddings.append(vec)
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        return self._embed_single(query)

    def _embed_single(self, text: str) -> List[float]:
        payload = {"model": self.model_name, "input": text}
        try:
            response = requests.post(
                self.url, json=payload, headers=self._get_headers()
            )
            response.raise_for_status()
            result = response.json()
            if not result or "data" not in result or not result["data"]:
                logging.error(
                    f"Invalid response format from VolcanoEngine API: {result}"
                )
                return []
            return result["data"][0].get("embedding", [])
        except requests.exceptions.RequestException as e:
            logging.error(f"VolcanoEngine API request failed: {str(e)}")
            return []
        except (KeyError, IndexError, ValueError, TypeError) as e:
            logging.error(f"Error parsing VolcanoEngine API response: {str(e)}")
            return []


def create_embedding_adapter(
    interface_format: str, api_key: str, base_url: str, model_name: str
) -> BaseEmbeddingAdapter:
    """
    工厂函数：根据 interface_format 返回不同的 embedding 适配器实例
    支持的接口格式：
    - 智谱AI (ZhipuAI)
    - DeepSeek
    - 阿里云百炼
    - SiliconFlow
    - 火山引擎 (VolcanoEngine)
    - Ollama (本地部署)
    - ML Studio
    """
    fmt = interface_format.strip().lower()
    if "智谱" in fmt or "zhipu" in fmt:
        return ZhipuAIEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "火山引擎" or fmt == "volcano":
        return VolcanoEngineEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "siliconflow" or fmt == "硅基流动":
        return SiliconFlowEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "ollama":
        return OllamaEmbeddingAdapter(model_name, base_url)
    elif fmt == "阿里云百炼" or fmt == "deepseek":
        return OpenAIEmbeddingAdapter(api_key, base_url, model_name)
    else:
        return OpenAIEmbeddingAdapter(api_key, base_url, model_name)