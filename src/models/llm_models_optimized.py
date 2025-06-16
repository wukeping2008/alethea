"""
优化版LLM模型集成模块 - 专为中国网络环境优化
支持多AI模型智能选择，优先使用国内可直接访问的AI服务
"""

import os
import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple
import requests
import asyncio
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """LLM提供商抽象基类"""
    
    @abstractmethod
    def initialize(self, api_key: str, **kwargs) -> None:
        """初始化LLM提供商"""
        pass
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """基于提示生成回答"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """获取提供商名称"""
        pass
    
    @property
    @abstractmethod
    def provider_capabilities(self) -> List[str]:
        """获取提供商能力"""
        pass
    
    @property
    @abstractmethod
    def provider_cost_tier(self) -> int:
        """获取成本等级 (1-5, 1为最低成本)"""
        pass
    
    @property
    @abstractmethod
    def network_accessibility(self) -> str:
        """网络可访问性 ('domestic', 'international', 'local')"""
        pass


class DeepSeekProvider(LLMProvider):
    """DeepSeek API集成 - 国产大模型，优先推荐"""
    
    def __init__(self):
        self.api_key = ""
        self.api_url = ""
        self.default_model = "deepseek-chat"
        self.max_tokens = 2000
        self._capabilities = ["general", "math", "code", "chinese", "reasoning"]
        self._cost_tier = 2
        self._network_accessibility = "domestic"
    
    def initialize(self, api_key: str, **kwargs) -> None:
        self.api_key = api_key
        self.api_url = kwargs.get('api_url', 'https://api.deepseek.com/v1/chat/completions')
        self.default_model = kwargs.get('default_model', 'deepseek-chat')
        self.max_tokens = kwargs.get('max_tokens', 2000)
        logger.info("DeepSeek provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            
            if not self.api_key:
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自DeepSeek ({model})的模拟回答。DeepSeek是国产领先的大语言模型，擅长数学推理和代码生成。\n\n您的问题：{prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 过滤掉思考过程，只保留最终回答
                content = result["choices"][0]["message"]["content"]
                
                # 构建清理后的响应，移除reasoning_content等思考过程字段
                clean_response = {
                    "choices": result.get("choices", []),
                    "created": result.get("created"),
                    "id": result.get("id"),
                    "model": result.get("model"),
                    "object": result.get("object"),
                    "usage": result.get("usage")
                }
                
                # 确保choices中的message只包含content，不包含reasoning相关字段
                if clean_response["choices"]:
                    for choice in clean_response["choices"]:
                        if "message" in choice:
                            choice["message"] = {
                                "content": choice["message"].get("content", ""),
                                "role": choice["message"].get("role", "assistant")
                            }
                
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": content,
                    "raw_response": clean_response,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"DeepSeek API error: {response.status_code}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "DeepSeek服务暂时不可用，请稍后重试。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"DeepSeek error: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "DeepSeek服务连接失败，请检查网络连接。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        return ["deepseek-chat", "deepseek-coder", "deepseek-math"]
    
    @property
    def provider_name(self) -> str:
        return "deepseek"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier
    
    @property
    def network_accessibility(self) -> str:
        return self._network_accessibility


class AliQwenProvider(LLMProvider):
    """阿里云通义千问 API集成 - 国内主流AI服务"""
    
    def __init__(self):
        self.api_key = ""
        self.api_url = ""
        self.default_model = "qwen-plus"
        self.max_tokens = 2000
        self._capabilities = ["general", "chinese", "reasoning", "math", "code"]
        self._cost_tier = 2
        self._network_accessibility = "domestic"
    
    def initialize(self, api_key: str, **kwargs) -> None:
        self.api_key = api_key
        self.api_url = kwargs.get('api_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions')
        self.default_model = kwargs.get('default_model', 'qwen-plus')
        self.max_tokens = kwargs.get('max_tokens', 2000)
        logger.info("阿里云通义千问 provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            
            if not self.api_key:
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自阿里云通义千问 ({model})的模拟回答。通义千问是阿里云推出的大语言模型，在中文理解和生成方面表现优秀。\n\n您的问题：{prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": result["choices"][0]["message"]["content"],
                    "raw_response": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"阿里云通义千问 API error: {response.status_code}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "阿里云通义千问服务暂时不可用，请稍后重试。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"阿里云通义千问 error: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "阿里云通义千问服务连接失败，请检查网络连接。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        return ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"]
    
    @property
    def provider_name(self) -> str:
        return "ali_qwen"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier
    
    @property
    def network_accessibility(self) -> str:
        return self._network_accessibility


class BaiduWenxinProvider(LLMProvider):
    """百度文心一言 API集成 - 国内AI服务"""
    
    def __init__(self):
        self.api_key = ""
        self.secret_key = ""
        self.access_token = ""
        self.default_model = "ERNIE-4.0-8K"
        self._capabilities = ["general", "chinese", "reasoning"]
        self._cost_tier = 2
        self._network_accessibility = "domestic"
    
    def initialize(self, api_key: str, **kwargs) -> None:
        self.api_key = api_key
        self.secret_key = kwargs.get('secret_key', '')
        self.default_model = kwargs.get('default_model', 'ERNIE-4.0-8K')
        logger.info("百度文心一言 provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            
            if not self.api_key:
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自百度文心一言 ({model})的模拟回答。文心一言是百度推出的知识增强大语言模型，在中文对话和知识问答方面表现出色。\n\n您的问题：{prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 获取访问令牌
            if not self.access_token:
                self.access_token = await self._get_access_token()
            
            if not self.access_token:
                return {
                    "provider": self.provider_name,
                    "error": "Failed to get access token",
                    "content": "百度文心一言认证失败，请检查API密钥配置。",
                    "timestamp": datetime.now().isoformat()
                }
            
            headers = {"Content-Type": "application/json"}
            data = {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
            
            # 根据模型选择对应的API端点
            model_endpoints = {
                "ERNIE-4.0-8K": "completions_pro",
                "ERNIE-3.5-8K": "completions",
                "ERNIE-Speed": "ernie_speed"
            }
            endpoint = model_endpoints.get(model, "completions_pro")
            
            response = requests.post(
                f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{endpoint}?access_token={self.access_token}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": result.get("result", ""),
                    "raw_response": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"百度文心一言 API error: {response.status_code}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "百度文心一言服务暂时不可用，请稍后重试。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"百度文心一言 error: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "百度文心一言服务连接失败，请检查网络连接。",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_access_token(self) -> str:
        """获取百度API访问令牌"""
        try:
            url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json().get("access_token", "")
            else:
                logger.error(f"获取百度访问令牌失败: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"获取百度访问令牌异常: {str(e)}")
            return ""
    
    def get_available_models(self) -> List[str]:
        return ["ERNIE-4.0-8K", "ERNIE-3.5-8K", "ERNIE-Speed"]
    
    @property
    def provider_name(self) -> str:
        return "baidu_wenxin"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier
    
    @property
    def network_accessibility(self) -> str:
        return self._network_accessibility


class ZhipuAIProvider(LLMProvider):
    """智谱AI GLM API集成 - 清华系国产AI"""
    
    def __init__(self):
        self.api_key = ""
        self.default_model = "glm-4"
        self._capabilities = ["general", "chinese", "reasoning", "code"]
        self._cost_tier = 2
        self._network_accessibility = "domestic"
    
    def initialize(self, api_key: str, **kwargs) -> None:
        self.api_key = api_key
        self.default_model = kwargs.get('default_model', 'glm-4')
        logger.info("智谱AI provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 2000)
            
            if not self.api_key:
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自智谱AI ({model})的模拟回答。智谱AI是清华大学技术成果转化的公司，GLM系列模型在中文理解和推理方面表现优秀。\n\n您的问题：{prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": result["choices"][0]["message"]["content"],
                    "raw_response": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"智谱AI API error: {response.status_code}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "智谱AI服务暂时不可用，请稍后重试。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"智谱AI error: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "智谱AI服务连接失败，请检查网络连接。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        return ["glm-4", "glm-4v", "glm-3-turbo"]
    
    @property
    def provider_name(self) -> str:
        return "zhipu_ai"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier
    
    @property
    def network_accessibility(self) -> str:
        return self._network_accessibility


class KimiProvider(LLMProvider):
    """Kimi (月之暗面) API集成 - 国产长文本AI"""
    
    def __init__(self):
        self.api_key = ""
        self.default_model = "moonshot-v1-8k"
        self._capabilities = ["general", "chinese", "long_context", "reasoning"]
        self._cost_tier = 2
        self._network_accessibility = "domestic"
    
    def initialize(self, api_key: str, **kwargs) -> None:
        self.api_key = api_key
        self.default_model = kwargs.get('default_model', 'moonshot-v1-8k')
        logger.info("Kimi (月之暗面) provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 2000)
            
            if not self.api_key:
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自Kimi ({model})的模拟回答。Kimi是月之暗面公司开发的大语言模型，擅长长文本理解和处理。\n\n您的问题：{prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                "https://api.moonshot.cn/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": result["choices"][0]["message"]["content"],
                    "raw_response": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Kimi API error: {response.status_code}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "Kimi服务暂时不可用，请稍后重试。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Kimi error: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "Kimi服务连接失败，请检查网络连接。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        return ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
    
    @property
    def provider_name(self) -> str:
        return "kimi"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier
    
    @property
    def network_accessibility(self) -> str:
        return self._network_accessibility


class OllamaDeepSeekProvider(LLMProvider):
    """Ollama DeepSeek本地部署集成 - 本地AI服务"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.default_model = "deepseek-r1:7b"
        self._capabilities = ["general", "math", "code", "chinese", "reasoning", "local"]
        self._cost_tier = 1  # 本地部署，成本最低
        self._network_accessibility = "local"
    
    def initialize(self, api_key: str = "", **kwargs) -> None:
        self.base_url = kwargs.get('base_url', 'http://localhost:11434')
        self.default_model = kwargs.get('default_model', 'deepseek-r1:7b')
        logger.info(f"Ollama DeepSeek provider initialized with base URL: {self.base_url}")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 2000)
            
            # 检查Ollama服务是否运行
            try:
                health_response = requests.get(f"{self.base_url}/api/tags", timeout=3)
                if health_response.status_code != 200:
                    raise Exception("Ollama service not available")
            except Exception as e:
                logger.warning(f"Ollama health check failed: {str(e)}")
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "error": "Ollama service not available",
                    "content": f"本地Ollama DeepSeek服务暂时不可用。请确保Ollama正在运行并且已安装{model}模型。\n\n如需安装，请运行：ollama pull {model}\n\n您的问题：{prompt}",
                    "timestamp": datetime.now().isoformat()
                }
            
            headers = {"Content-Type": "application/json"}
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": result["response"],
                    "raw_response": result,
                    "timestamp": datetime.now().isoformat(),
                    "local": True
                }
            else:
                logger.error(f"Ollama DeepSeek API error: {response.status_code}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": f"本地DeepSeek模型调用失败。错误代码: {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except requests.exceptions.Timeout:
            return {
                "provider": self.provider_name,
                "error": "Request timeout",
                "content": "本地DeepSeek模型响应超时，请稍后重试。",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Ollama DeepSeek error: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": f"本地DeepSeek模型调用出错: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if response.status_code == 200:
                models_data = response.json()
                deepseek_models = []
                for model in models_data.get("models", []):
                    model_name = model.get("name", "")
                    if "deepseek" in model_name.lower():
                        deepseek_models.append(model_name)
                
                return deepseek_models if deepseek_models else ["deepseek-r1:7b", "deepseek-r1:1.5b"]
            else:
                return ["deepseek-r1:7b", "deepseek-r1:1.5b"]
        except:
            return ["deepseek-r1:7b", "deepseek-r1:1.5b"]
    
    @property
    def provider_name(self) -> str:
        return "ollama_deepseek"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier
    
    @property
    def network_accessibility(self) -> str:
        return self._network_accessibility


# 国外AI服务商（保留代码但默认禁用）
class OpenAIProvider(LLMProvider):
    """OpenAI API集成 - 需要网络代理"""
    
    def __init__(self):
        self.api_key = ""
        self.default_model = "gpt-4o"
        self._capabilities = ["general", "math", "code", "reasoning", "science"]
        self._cost_tier = 4
        self._network_accessibility = "international"
        self._enabled = False  # 默认禁用
    
    def initialize(self, api_key: str, **kwargs) -> None:
        self.api_key = api_key
        self.default_model = kwargs.get('default_model', 'gpt-4o')
        self._enabled = kwargs.get('enabled', False)
        logger.info(f"OpenAI provider initialized (enabled: {self._enabled})")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        if not self._enabled:
            return {
                "provider": self.provider_name,
                "model": self.default_model,
                "error": "Provider disabled",
                "content": "OpenAI服务在中国大陆地区需要网络代理才能访问，当前已禁用。如需使用，请配置网络代理并在配置中启用。",
                "timestamp": datetime.now().isoformat()
            }
        
        # 网络连接检测
        try:
            test_response = requests.get("https://api.openai.com", timeout=5)
        except:
            return {
                "provider": self.provider_name,
                "model": self.default_model,
                "error": "Network unreachable",
                "content": "无法连接到OpenAI服务，请检查网络代理配置。",
                "timestamp": datetime.now().isoformat()
            }
        
        # 实际API调用逻辑（如果网络可达）
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 2000)
            
            if not self.api_key:
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自OpenAI ({model})的模拟回答。需要配置有效的API密钥才能使用真实服务。\n\n您的问题：{prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": result["choices"][0]["message"]["content"],
                    "raw_response": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "OpenAI服务暂时不可用，请稍后重试。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "OpenAI服务连接失败，请检查网络连接。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier
    
    @property
    def network_accessibility(self) -> str:
        return self._network_accessibility


class ClaudeProvider(LLMProvider):
    """Anthropic Claude API集成 - 需要网络代理"""
    
    def __init__(self):
        self.api_key = ""
        self.default_model = "claude-3-opus"
        self._capabilities = ["general", "reasoning", "math", "science", "analysis"]
        self._cost_tier = 5
        self._network_accessibility = "international"
        self._enabled = False  # 默认禁用
    
    def initialize(self, api_key: str, **kwargs) -> None:
        self.api_key = api_key
        self.default_model = kwargs.get('default_model', 'claude-3-opus')
        self._enabled = kwargs.get('enabled', False)
        logger.info(f"Claude provider initialized (enabled: {self._enabled})")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        if not self._enabled:
            return {
                "provider": self.provider_name,
                "model": self.default_model,
                "error": "Provider disabled",
                "content": "Claude服务在中国大陆地区需要网络代理才能访问，当前已禁用。如需使用，请配置网络代理并在配置中启用。",
                "timestamp": datetime.now().isoformat()
            }
        
        # 网络连接检测
        try:
            test_response = requests.get("https://api.anthropic.com", timeout=5)
        except:
            return {
                "provider": self.provider_name,
                "model": self.default_model,
                "error": "Network unreachable",
                "content": "无法连接到Claude服务，请检查网络代理配置。",
                "timestamp": datetime.now().isoformat()
            }
        
        # 实际API调用逻辑（如果网络可达）
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 2000)
            
            if not self.api_key:
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自Claude ({model})的模拟回答。需要配置有效的API密钥才能使用真实服务。\n\n您的问题：{prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": result["content"][0]["text"],
                    "raw_response": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Claude API error: {response.status_code}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "Claude服务暂时不可用，请稍后重试。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Claude error: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "Claude服务连接失败，请检查网络连接。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        return ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    
    @property
    def provider_name(self) -> str:
        return "claude"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier
    
    @property
    def network_accessibility(self) -> str:
        return self._network_accessibility


class GeminiProvider(LLMProvider):
    """Google Gemini API集成 - 需要网络代理"""
    
    def __init__(self):
        self.api_key = ""
        self.default_model = "gemini-pro"
        self._capabilities = ["general", "reasoning", "code", "multimodal"]
        self._cost_tier = 3
        self._network_accessibility = "international"
        self._enabled = False  # 默认禁用
    
    def initialize(self, api_key: str, **kwargs) -> None:
        self.api_key = api_key
        self.default_model = kwargs.get('default_model', 'gemini-pro')
        self._enabled = kwargs.get('enabled', False)
        logger.info(f"Gemini provider initialized (enabled: {self._enabled})")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        if not self._enabled:
            return {
                "provider": self.provider_name,
                "model": self.default_model,
                "error": "Provider disabled",
                "content": "Gemini服务在中国大陆地区需要网络代理才能访问，当前已禁用。如需使用，请配置网络代理并在配置中启用。",
                "timestamp": datetime.now().isoformat()
            }
        
        # 网络连接检测
        try:
            test_response = requests.get("https://generativelanguage.googleapis.com", timeout=5)
        except:
            return {
                "provider": self.provider_name,
                "model": self.default_model,
                "error": "Network unreachable",
                "content": "无法连接到Gemini服务，请检查网络代理配置。",
                "timestamp": datetime.now().isoformat()
            }
        
        # 实际API调用逻辑（如果网络可达）
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 2000)
            
            if not self.api_key:
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自Gemini ({model})的模拟回答。需要配置有效的API密钥才能使用真实服务。\n\n您的问题：{prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": result["candidates"][0]["content"]["parts"][0]["text"],
                    "raw_response": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Gemini API error: {response.status_code}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "Gemini服务暂时不可用，请稍后重试。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "Gemini服务连接失败，请检查网络连接。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        return ["gemini-pro", "gemini-ultra", "gemini-pro-vision"]
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier
    
    @property
    def network_accessibility(self) -> str:
        return self._network_accessibility


# 智能模型选择器
class OptimizedModelSelector:
    """优化版智能模型选择器 - 专为中国网络环境优化"""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.patterns = {
            "math": r"(数学|方程|计算|积分|微分|导数|矩阵|向量|概率|统计|几何|代数|三角|函数)",
            "code": r"(代码|编程|函数|算法|程序|开发|软件|编写|实现|调试|API|接口|类|对象|变量|循环|条件|语法)",
            "electronics": r"(电路|电子|电工|电压|电流|电阻|电容|电感|晶体管|二极管|逻辑门|数字电路|模拟电路|信号|频率|波形|示波器|仿真)",
            "physics": r"(物理|力学|动力学|热力学|电磁学|光学|量子|相对论|能量|功率|速度|加速度|质量|动量|波动|振动)",
            "chemistry": r"(化学|元素|分子|原子|化合物|反应|酸碱|氧化|还原|溶液|浓度|催化剂|有机|无机|物质)",
            "chinese": r"[\u4e00-\u9fa5]{10,}"  # 至少10个中文字符
        }
    
    def select_model(self, query: str, user_preference: Optional[str] = None) -> Tuple[str, str, str]:
        """
        选择最佳模型
        
        Args:
            query: 用户问题
            user_preference: 用户偏好提供商
            
        Returns:
            Tuple of (provider_name, model_name, selection_reason)
        """
        # 如果用户指定了偏好且可用，使用用户偏好
        if user_preference and user_preference in self.llm_manager.get_all_providers():
            provider = self.llm_manager.providers[user_preference]
            return user_preference, provider.default_model, "用户指定模型"
        
        # 检测问题特征
        characteristics = self._detect_characteristics(query)
        logger.info(f"检测到的特征: {characteristics}")
        
        # 优先级策略：国内AI服务 > 本地AI > 国外AI服务（如果启用）
        domestic_providers = ['deepseek', 'ali_qwen', 'baidu_wenxin', 'zhipu_ai', 'kimi']
        local_providers = ['ollama_deepseek']
        international_providers = ['openai', 'claude', 'gemini']
        
        # 首先尝试国内AI服务
        available_domestic = [p for p in domestic_providers if p in self.llm_manager.get_all_providers()]
        
        if available_domestic:
            # 根据问题特征选择最适合的国内AI服务
            best_provider = self._select_best_domestic_provider(available_domestic, characteristics)
            provider = self.llm_manager.providers[best_provider]
            
            # 生成选择理由
            provider_names = {
                'deepseek': 'DeepSeek',
                'ali_qwen': '阿里云通义千问',
                'baidu_wenxin': '百度文心一言',
                'zhipu_ai': '智谱AI',
                'kimi': 'Kimi'
            }
            
            reason_parts = []
            if 'code' in characteristics:
                reason_parts.append("编程")
            if 'math' in characteristics:
                reason_parts.append("数学")
            if 'chinese' in characteristics:
                reason_parts.append("中文")
            if not reason_parts:
                reason_parts.append("通用")
            
            provider_display_name = provider_names.get(best_provider, best_provider)
            reason = f"{'/'.join(reason_parts)}问题，使用国内{provider_display_name}模型"
            
            logger.info(f"选择国内AI服务: {best_provider}, 模型: {provider.default_model}")
            return best_provider, provider.default_model, reason
        
        # 如果国内AI服务不可用，尝试本地AI
        available_local = [p for p in local_providers if p in self.llm_manager.get_all_providers()]
        
        if available_local:
            # 检查本地服务是否真的可用
            for local_provider in available_local:
                try:
                    # 快速健康检查
                    if local_provider == 'ollama_deepseek':
                        import requests
                        health_response = requests.get("http://localhost:11434/api/tags", timeout=2)
                        if health_response.status_code == 200:
                            provider = self.llm_manager.providers[local_provider]
                            reason = "国内AI服务不可用，使用本地DeepSeek模型"
                            logger.info(f"选择本地AI服务: {local_provider}")
                            return local_provider, provider.default_model, reason
                except:
                    continue
        
        # 最后尝试国外AI服务（如果启用）
        available_international = []
        for int_provider in international_providers:
            if int_provider in self.llm_manager.get_all_providers():
                provider = self.llm_manager.providers[int_provider]
                if hasattr(provider, '_enabled') and provider._enabled:
                    available_international.append(int_provider)
        
        if available_international:
            # 选择最佳国外AI服务
            best_provider = available_international[0]  # 简单选择第一个可用的
            provider = self.llm_manager.providers[best_provider]
            reason = f"使用国外{best_provider.upper()}模型（需要网络代理）"
            
            logger.info(f"选择国外AI服务: {best_provider}")
            return best_provider, provider.default_model, reason
        
        # 如果所有服务都不可用，返回默认错误
        logger.error("没有可用的AI服务")
        return "none", "none", "没有可用的AI服务"
    
    def _detect_characteristics(self, query: str) -> List[str]:
        """检测问题特征"""
        characteristics = []
        
        for category, pattern in self.patterns.items():
            if re.search(pattern, query):
                characteristics.append(category)
        
        characteristics.append("general")
        
        if len(query) > 200:
            characteristics.append("complex")
        
        return characteristics
    
    def _select_best_domestic_provider(self, providers: List[str], characteristics: List[str]) -> str:
        """选择最佳国内AI服务提供商"""
        # 首先检查哪些提供商有有效的API密钥
        providers_with_keys = []
        providers_without_keys = []
        
        for provider_name in providers:
            provider = self.llm_manager.providers[provider_name]
            # 检查是否有API密钥
            if hasattr(provider, 'api_key') and provider.api_key and provider.api_key.strip():
                providers_with_keys.append(provider_name)
            else:
                providers_without_keys.append(provider_name)
        
        # 优先从有API密钥的提供商中选择
        target_providers = providers_with_keys if providers_with_keys else providers_without_keys
        
        # 根据特征匹配选择最佳提供商
        scores = {}
        
        for provider_name in target_providers:
            provider = self.llm_manager.providers[provider_name]
            score = 0
            
            # 如果有API密钥，给予额外分数
            if provider_name in providers_with_keys:
                score += 10  # 有API密钥的提供商优先级更高
            
            # 基于能力匹配计算分数
            for characteristic in characteristics:
                if characteristic in provider.provider_capabilities:
                    score += 1
            
            # 特殊优化规则
            if 'code' in characteristics and provider_name == 'deepseek':
                score += 2  # DeepSeek在代码方面表现优秀
            if 'math' in characteristics and provider_name == 'deepseek':
                score += 2  # DeepSeek在数学方面表现优秀
            if 'chinese' in characteristics and provider_name in ['ali_qwen', 'baidu_wenxin']:
                score += 1  # 阿里云和百度在中文方面表现优秀
            
            scores[provider_name] = score
        
        # 返回得分最高的提供商
        best_provider = max(scores.items(), key=lambda x: x[1])[0]
        
        # 调试信息
        print(f"Available providers: {providers}")
        print(f"Providers with API keys: {providers_with_keys}")
        print(f"Providers without API keys: {providers_without_keys}")
        print(f"Provider scores: {scores}")
        print(f"Selected provider: {best_provider}")
        
        return best_provider


# 优化版LLM管理器
class OptimizedLLMManager:
    """优化版LLM管理器 - 专为中国网络环境优化"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self.model_selector = None
    
    def register_provider(self, name: str, provider: LLMProvider) -> None:
        """注册LLM提供商"""
        self.providers[name] = provider
        if self.default_provider is None:
            self.default_provider = name
        logger.info(f"注册提供商: {name}")
    
    def set_default_provider(self, name: str) -> None:
        """设置默认LLM提供商"""
        if name in self.providers:
            self.default_provider = name
            logger.info(f"默认提供商设置为: {name}")
        else:
            raise ValueError(f"提供商 '{name}' 未注册")
    
    def initialize_model_selector(self) -> None:
        """初始化模型选择器"""
        self.model_selector = OptimizedModelSelector(self)
        logger.info("模型选择器已初始化")
    
    async def generate_response(self, prompt: str, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """生成回答"""
        selection_reason = "默认模型"
        
        # 使用模型选择器自动选择最佳提供商
        if self.model_selector and not provider:
            selected_provider, selected_model, selection_reason = self.model_selector.select_model(prompt, None)
            
            if selected_provider == "none":
                return {
                    "error": "No available providers",
                    "content": "抱歉，当前没有可用的AI服务。请检查网络连接或联系管理员。",
                    "timestamp": datetime.now().isoformat(),
                    "selection_reason": selection_reason
                }
            
            provider = selected_provider
            kwargs['model'] = selected_model
            logger.info(f"自动选择提供商: {selected_provider}, 模型: {selected_model}")
        else:
            provider = provider or self.default_provider
            if provider:
                selection_reason = "用户指定模型"
        
        if provider not in self.providers:
            logger.error(f"提供商 '{provider}' 未找到")
            return {
                "error": f"Provider '{provider}' not found",
                "content": "抱歉，请求的AI模型不可用。",
                "timestamp": datetime.now().isoformat(),
                "selection_reason": "模型不可用"
            }
        
        # 生成回答
        response = await self.providers[provider].generate_response(prompt, **kwargs)
        
        # 智能备用机制
        if "error" in response:
            fallback_response = await self._try_fallback(prompt, provider, **kwargs)
            if fallback_response:
                return fallback_response
        
        response["selection_reason"] = selection_reason
        response["selected_provider"] = provider
        
        return response
    
    async def _try_fallback(self, prompt: str, failed_provider: str, **kwargs) -> Optional[Dict[str, Any]]:
        """尝试备用服务"""
        # 备用优先级：国内AI > 本地AI > 其他
        fallback_order = ['deepseek', 'ali_qwen', 'baidu_wenxin', 'zhipu_ai', 'kimi', 'ollama_deepseek']
        
        for backup_provider in fallback_order:
            if backup_provider != failed_provider and backup_provider in self.providers:
                try:
                    logger.info(f"尝试备用服务: {backup_provider}")
                    
                    # 特殊处理本地DeepSeek
                    if backup_provider == 'ollama_deepseek':
                        import requests
                        health_response = requests.get("http://localhost:11434/api/tags", timeout=2)
                        if health_response.status_code != 200:
                            continue
                    
                    # 使用备用服务
                    fallback_kwargs = kwargs.copy()
                    fallback_kwargs['model'] = self.providers[backup_provider].default_model
                    fallback_response = await self.providers[backup_provider].generate_response(prompt, **fallback_kwargs)
                    
                    if "error" not in fallback_response:
                        provider_names = {
                            'deepseek': 'DeepSeek',
                            'ali_qwen': '阿里云通义千问',
                            'baidu_wenxin': '百度文心一言',
                            'zhipu_ai': '智谱AI',
                            'kimi': 'Kimi',
                            'ollama_deepseek': '本地DeepSeek'
                        }
                        
                        fallback_response["selection_reason"] = f"主要AI服务不可用，自动切换到备用{provider_names.get(backup_provider, backup_provider)}服务"
                        fallback_response["selected_provider"] = backup_provider
                        fallback_response["fallback_from"] = failed_provider
                        logger.info(f"成功切换到备用服务: {backup_provider}")
                        return fallback_response
                    
                except Exception as e:
                    logger.warning(f"备用服务 {backup_provider} 失败: {str(e)}")
                    continue
        
        return None
    
    def get_all_providers(self) -> List[str]:
        """获取所有注册的提供商"""
        return list(self.providers.keys())
    
    def get_provider_models(self, provider: str) -> List[str]:
        """获取指定提供商的可用模型"""
        if provider not in self.providers:
            return []
        return self.providers[provider].get_available_models()
    
    def get_provider_capabilities(self, provider: str) -> List[str]:
        """获取指定提供商的能力"""
        if provider not in self.providers:
            return []
        return self.providers[provider].provider_capabilities


# 创建优化版LLM管理器单例
optimized_llm_manager = OptimizedLLMManager()

def initialize_optimized_llm_providers(config: Dict[str, Any]) -> None:
    """初始化优化版LLM提供商 - 专为中国网络环境优化"""
    
    # 初始化国内AI服务（优先级最高）
    
    # 1. DeepSeek - 国产领先大模型
    deepseek_provider = DeepSeekProvider()
    deepseek_provider.initialize(
        api_key=config.get('deepseek', {}).get('api_key', ''),
        api_url=config.get('deepseek', {}).get('api_url', 'https://api.deepseek.com/v1/chat/completions'),
        default_model=config.get('deepseek', {}).get('default_model', 'deepseek-chat'),
        max_tokens=config.get('deepseek', {}).get('max_tokens', 2000)
    )
    optimized_llm_manager.register_provider('deepseek', deepseek_provider)
    
    # 2. 阿里云通义千问
    ali_qwen_provider = AliQwenProvider()
    ali_qwen_provider.initialize(
        api_key=config.get('ali_qwen', {}).get('api_key', ''),
        api_url=config.get('ali_qwen', {}).get('api_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'),
        default_model=config.get('ali_qwen', {}).get('default_model', 'qwen-plus'),
        max_tokens=config.get('ali_qwen', {}).get('max_tokens', 2000)
    )
    optimized_llm_manager.register_provider('ali_qwen', ali_qwen_provider)
    
    # 3. 百度文心一言
    baidu_wenxin_provider = BaiduWenxinProvider()
    baidu_wenxin_provider.initialize(
        api_key=config.get('baidu_wenxin', {}).get('api_key', ''),
        secret_key=config.get('baidu_wenxin', {}).get('secret_key', ''),
        default_model=config.get('baidu_wenxin', {}).get('default_model', 'ERNIE-4.0-8K')
    )
    optimized_llm_manager.register_provider('baidu_wenxin', baidu_wenxin_provider)
    
    # 4. 智谱AI
    zhipu_ai_provider = ZhipuAIProvider()
    zhipu_ai_provider.initialize(
        api_key=config.get('zhipu_ai', {}).get('api_key', ''),
        default_model=config.get('zhipu_ai', {}).get('default_model', 'glm-4')
    )
    optimized_llm_manager.register_provider('zhipu_ai', zhipu_ai_provider)
    
    # 5. Kimi (月之暗面)
    kimi_provider = KimiProvider()
    kimi_provider.initialize(
        api_key=config.get('kimi', {}).get('api_key', ''),
        default_model=config.get('kimi', {}).get('default_model', 'moonshot-v1-8k')
    )
    optimized_llm_manager.register_provider('kimi', kimi_provider)
    
    # 初始化本地AI服务
    
    # 6. Ollama DeepSeek (本地)
    ollama_deepseek_provider = OllamaDeepSeekProvider()
    ollama_deepseek_provider.initialize(
        base_url=config.get('ollama_deepseek', {}).get('base_url', 'http://localhost:11434'),
        default_model=config.get('ollama_deepseek', {}).get('default_model', 'deepseek-r1:7b')
    )
    optimized_llm_manager.register_provider('ollama_deepseek', ollama_deepseek_provider)
    
    # 初始化国外AI服务（默认禁用，需要手动启用）
    
    # 7. OpenAI (需要网络代理)
    openai_provider = OpenAIProvider()
    openai_provider.initialize(
        api_key=config.get('openai', {}).get('api_key', ''),
        default_model=config.get('openai', {}).get('default_model', 'gpt-4o'),
        enabled=config.get('openai', {}).get('enabled', False)
    )
    optimized_llm_manager.register_provider('openai', openai_provider)
    
    # 8. Claude (需要网络代理)
    claude_provider = ClaudeProvider()
    claude_provider.initialize(
        api_key=config.get('claude', {}).get('api_key', ''),
        default_model=config.get('claude', {}).get('default_model', 'claude-3-opus'),
        enabled=config.get('claude', {}).get('enabled', False)
    )
    optimized_llm_manager.register_provider('claude', claude_provider)
    
    # 9. Gemini (需要网络代理)
    gemini_provider = GeminiProvider()
    gemini_provider.initialize(
        api_key=config.get('gemini', {}).get('api_key', ''),
        default_model=config.get('gemini', {}).get('default_model', 'gemini-pro'),
        enabled=config.get('gemini', {}).get('enabled', False)
    )
    optimized_llm_manager.register_provider('gemini', gemini_provider)
    
    # 设置默认提供商（优先使用国内AI服务）
    default_provider = config.get('default_provider', 'deepseek')
    if default_provider in optimized_llm_manager.get_all_providers():
        optimized_llm_manager.set_default_provider(default_provider)
    
    # 初始化模型选择器
    optimized_llm_manager.initialize_model_selector()
    
    logger.info(f"已初始化优化版LLM提供商: {optimized_llm_manager.get_all_providers()}")
    logger.info("优化版LLM管理器已就绪 - 专为中国网络环境优化")
