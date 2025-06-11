"""
Enhanced LLM Models Integration Module for Alethea Platform
Supports multiple AI models with intelligent model selection
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def initialize(self, api_key: str, **kwargs) -> None:
        """Initialize the LLM provider with API key and other parameters"""
        pass
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response from the LLM based on the prompt"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get a list of available models from this provider"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of the provider"""
        pass
    
    @property
    @abstractmethod
    def provider_capabilities(self) -> List[str]:
        """Get the capabilities of this provider (e.g., 'code', 'math', 'reasoning')"""
        pass
    
    @property
    @abstractmethod
    def provider_cost_tier(self) -> int:
        """Get the cost tier of this provider (1-5, where 1 is lowest cost)"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API integration"""
    
    def __init__(self):
        self.api_key = ""
        self.default_model = "gpt-4o"
        self.api_base = "https://api.openai.com/v1"
        self._capabilities = ["general", "math", "code", "reasoning", "science"]
        self._cost_tier = 4
    
    def initialize(self, api_key: str, **kwargs) -> None:
        """Initialize OpenAI client with API key"""
        self.api_key = api_key
        self.default_model = kwargs.get('default_model', 'gpt-4o')
        self.api_base = kwargs.get('api_base', 'https://api.openai.com/v1')
        logger.info("OpenAI provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using OpenAI models"""
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1000)
            
            # For development/testing without API key
            if not self.api_key or self.api_key == "":
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自OpenAI ({model})的模拟回答。在生产环境中配置API密钥后，这里将显示真实的AI回答。\n\n您的问题是: {prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the request
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
            
            # Make the API call
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data
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
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "抱歉，在处理您的请求时遇到了问题。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "抱歉，在生成回答时遇到了错误。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        try:
            if not self.api_key or self.api_key == "":
                return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
                
            # Make API call to list models
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.api_base}/models", headers=headers)
            
            if response.status_code == 200:
                models = response.json()["data"]
                # Filter for chat models
                chat_models = [model["id"] for model in models if "gpt" in model["id"]]
                return chat_models
            else:
                logger.error(f"Error fetching OpenAI models: {response.status_code}")
                return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
                
        except Exception as e:
            logger.error(f"Error fetching OpenAI models: {str(e)}")
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


class DeepSeekProvider(LLMProvider):
    """DeepSeek API integration"""
    
    def __init__(self):
        self.api_key = ""
        self.default_model = "deepseek-chat"
        self._capabilities = ["general", "math", "code", "chinese"]
        self._cost_tier = 3
    
    def initialize(self, api_key: str, **kwargs) -> None:
        """Initialize DeepSeek client with API key"""
        self.api_key = api_key
        self.default_model = kwargs.get('default_model', 'deepseek-chat')
        logger.info("DeepSeek provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using DeepSeek models"""
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1000)
            
            # For development/testing without API key
            if not self.api_key or self.api_key == "":
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自DeepSeek ({model})的模拟回答。在生产环境中配置API密钥后，这里将显示真实的AI回答。\n\n您的问题是: {prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the request
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
            
            # Make the API call (adjust endpoint as needed)
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
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
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "抱歉，在处理您的请求时遇到了问题。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating response from DeepSeek: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "抱歉，在生成回答时遇到了错误。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        """Get available DeepSeek models"""
        # DeepSeek API might not provide a model list endpoint
        # Return known models instead
        return ["deepseek-chat", "deepseek-coder", "deepseek-llm-67b"]
    
    @property
    def provider_name(self) -> str:
        return "deepseek"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier


class VolcesDeepSeekProvider(LLMProvider):
    """Volces DeepSeek API integration (火山引擎DeepSeek)"""
    
    def __init__(self):
        self.api_key = ""
        self.api_url = ""
        self.default_model = "deepseek-r1-250528"
        self._capabilities = ["general", "math", "code", "chinese", "reasoning"]
        self._cost_tier = 2  # Lower cost tier for backup service
    
    def initialize(self, api_key: str, **kwargs) -> None:
        """Initialize Volces DeepSeek client with API key"""
        self.api_key = api_key
        self.api_url = kwargs.get('api_url', 'https://ark.cn-beijing.volces.com/api/v3/chat/completions')
        self.default_model = kwargs.get('default_model', 'deepseek-r1-250528')
        logger.info("Volces DeepSeek provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using Volces DeepSeek models"""
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 16191)
            
            # For development/testing without API key
            if not self.api_key or self.api_key == "":
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自火山引擎DeepSeek ({model})的模拟回答。在生产环境中配置API密钥后，这里将显示真实的AI回答。\n\n您的问题是: {prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the request
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
            
            # Make the API call
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60  # Increased timeout for better reliability
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
                logger.error(f"Volces DeepSeek API error: {response.status_code} - {response.text}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "抱歉，在处理您的请求时遇到了问题。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating response from Volces DeepSeek: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "抱歉，在生成回答时遇到了错误。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        """Get available Volces DeepSeek models"""
        return ["deepseek-r1-250528", "deepseek-r1", "deepseek-chat"]
    
    @property
    def provider_name(self) -> str:
        return "volces_deepseek"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier


class QianwenProvider(LLMProvider):
    """Qianwen (通用千问) API integration"""
    
    def __init__(self):
        self.api_key = ""
        self.secret_key = ""
        self.default_model = "ERNIE-Bot-4"
        self._capabilities = ["general", "chinese", "reasoning"]
        self._cost_tier = 2
    
    def initialize(self, api_key: str, **kwargs) -> None:
        """Initialize Qianwen client with API key"""
        self.api_key = api_key
        self.secret_key = kwargs.get('secret_key', '')
        self.default_model = kwargs.get('default_model', 'ERNIE-Bot-4')
        logger.info("Qianwen provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using Qianwen models"""
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            
            # For development/testing without API key
            if not self.api_key or self.api_key == "":
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自通用千问 ({model})的模拟回答。在生产环境中配置API密钥后，这里将显示真实的AI回答。\n\n您的问题是: {prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the request
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
            
            # Make the API call (adjust endpoint as needed)
            # Note: Qianwen/Baidu API might require different authentication method
            response = requests.post(
                f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}?access_token={self._get_access_token()}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": result["result"],
                    "raw_response": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Qianwen API error: {response.status_code} - {response.text}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "抱歉，在处理您的请求时遇到了问题。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating response from Qianwen: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "抱歉，在生成回答时遇到了错误。",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_access_token(self) -> str:
        """Get access token for Baidu API"""
        try:
            url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                logger.error(f"Error getting Baidu access token: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            logger.error(f"Error getting Baidu access token: {str(e)}")
            return ""
    
    def get_available_models(self) -> List[str]:
        """Get available Qianwen models"""
        # Qianwen API might not provide a model list endpoint
        # Return known models instead
        return ["ERNIE-Bot-4", "ERNIE-Bot", "ERNIE-Bot-8k", "ERNIE-Speed"]
    
    @property
    def provider_name(self) -> str:
        return "qianwen"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier


class AliQwenProvider(LLMProvider):
    """阿里云通义千问 API integration"""
    
    def __init__(self):
        self.api_key = ""
        self.api_url = ""
        self.default_model = "qwen-plus-2025-04-28"
        self._capabilities = ["general", "chinese", "reasoning", "math", "code"]
        self._cost_tier = 2  # Lower cost tier for backup service
    
    def initialize(self, api_key: str, **kwargs) -> None:
        """Initialize AliQwen client with API key"""
        self.api_key = api_key
        self.api_url = kwargs.get('api_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions')
        self.default_model = kwargs.get('default_model', 'qwen-plus-2025-04-28')
        logger.info("AliQwen provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using AliQwen models"""
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 16191)
            
            # For development/testing without API key
            if not self.api_key or self.api_key == "":
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自阿里云通义千问 ({model})的模拟回答。在生产环境中配置API密钥后，这里将显示真实的AI回答。\n\n您的问题是: {prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the request
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
            
            # Make the API call
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
                logger.error(f"AliQwen API error: {response.status_code} - {response.text}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "抱歉，在处理您的请求时遇到了问题。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating response from AliQwen: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "抱歉，在生成回答时遇到了错误。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        """Get available AliQwen models"""
        return ["qwen-plus-2025-04-28", "qwen-plus", "qwen-turbo", "qwen-max"]
    
    @property
    def provider_name(self) -> str:
        return "ali_qwen"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier


class ClaudeProvider(LLMProvider):
    """Anthropic Claude API integration"""
    
    def __init__(self):
        self.api_key = ""
        self.default_model = "claude-3-opus"
        self._capabilities = ["general", "reasoning", "math", "science", "analysis"]
        self._cost_tier = 5
    
    def initialize(self, api_key: str, **kwargs) -> None:
        """Initialize Claude client with API key"""
        self.api_key = api_key
        self.default_model = kwargs.get('default_model', 'claude-3-opus')
        logger.info("Claude provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using Claude models"""
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1000)
            
            # For development/testing without API key
            if not self.api_key or self.api_key == "":
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自Claude ({model})的模拟回答。在生产环境中配置API密钥后，这里将显示真实的AI回答。\n\n您的问题是: {prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the request
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
            
            # Make the API call
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
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
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "抱歉，在处理您的请求时遇到了问题。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating response from Claude: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "抱歉，在生成回答时遇到了错误。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        """Get available Claude models"""
        return ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-2.1"]
    
    @property
    def provider_name(self) -> str:
        return "claude"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier


class GeminiProvider(LLMProvider):
    """Google Gemini API integration"""
    
    def __init__(self):
        self.api_key = ""
        self.default_model = "gemini-pro"
        self._capabilities = ["general", "reasoning", "code", "multimodal"]
        self._cost_tier = 3
    
    def initialize(self, api_key: str, **kwargs) -> None:
        """Initialize Gemini client with API key"""
        self.api_key = api_key
        self.default_model = kwargs.get('default_model', 'gemini-pro')
        logger.info("Gemini provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using Gemini models"""
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1000)
            
            # For development/testing without API key
            if not self.api_key or self.api_key == "":
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自Gemini ({model})的模拟回答。在生产环境中配置API密钥后，这里将显示真实的AI回答。\n\n您的问题是: {prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            }
            
            # Make the API call
            response = requests.post(url, headers=headers, json=data)
            
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
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "抱歉，在处理您的请求时遇到了问题。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating response from Gemini: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "抱歉，在生成回答时遇到了错误。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        """Get available Gemini models"""
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


class LlamaProvider(LLMProvider):
    """Meta Llama API integration"""
    
    def __init__(self):
        self.api_key = ""
        self.default_model = "llama-3-70b"
        self._capabilities = ["general", "code", "reasoning"]
        self._cost_tier = 2
    
    def initialize(self, api_key: str, **kwargs) -> None:
        """Initialize Llama client with API key"""
        self.api_key = api_key
        self.default_model = kwargs.get('default_model', 'llama-3-70b')
        logger.info("Llama provider initialized")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using Llama models"""
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1000)
            
            # For development/testing without API key
            if not self.api_key or self.api_key == "":
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "content": f"这是来自Llama ({model})的模拟回答。在生产环境中配置API密钥后，这里将显示真实的AI回答。\n\n您的问题是: {prompt}",
                    "raw_response": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the request
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
            
            # Make the API call (adjust endpoint as needed)
            response = requests.post(
                "https://api.meta.ai/v1/chat/completions",
                headers=headers,
                json=data
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
                logger.error(f"Llama API error: {response.status_code} - {response.text}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": "抱歉，在处理您的请求时遇到了问题。",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating response from Llama: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": "抱歉，在生成回答时遇到了错误。",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        """Get available Llama models"""
        return ["llama-3-70b", "llama-3-8b", "llama-2-70b", "llama-2-13b"]
    
    @property
    def provider_name(self) -> str:
        return "llama"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier


class OllamaDeepSeekProvider(LLMProvider):
    """Ollama DeepSeek local deployment integration"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.default_model = "deepseek-r1:7b"
        self._capabilities = ["general", "math", "code", "chinese", "reasoning", "local"]
        self._cost_tier = 1  # Local deployment, lowest cost
    
    def initialize(self, api_key: str = "", **kwargs) -> None:
        """Initialize Ollama DeepSeek client"""
        self.base_url = kwargs.get('base_url', 'http://localhost:11434')
        self.default_model = kwargs.get('default_model', 'deepseek-r1:7b')
        logger.info(f"Ollama DeepSeek provider initialized with base URL: {self.base_url}")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using local Ollama DeepSeek models"""
        try:
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1000)
            
            # Check if Ollama is running
            try:
                health_response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if health_response.status_code != 200:
                    raise Exception("Ollama service not available")
            except Exception as e:
                logger.warning(f"Ollama health check failed: {str(e)}")
                return {
                    "provider": self.provider_name,
                    "model": model,
                    "error": "Ollama service not available",
                    "content": f"本地Ollama DeepSeek服务暂时不可用。请确保Ollama正在运行并且已安装{model}模型。\n\n您的问题是: {prompt}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the request for Ollama API
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
            
            # Make the API call to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                headers=headers,
                json=data,
                timeout=60  # Longer timeout for local generation
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
                logger.error(f"Ollama DeepSeek API error: {response.status_code} - {response.text}")
                return {
                    "provider": self.provider_name,
                    "error": f"API error: {response.status_code}",
                    "content": f"本地DeepSeek模型调用失败。错误代码: {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except requests.exceptions.Timeout:
            logger.error("Ollama DeepSeek request timeout")
            return {
                "provider": self.provider_name,
                "error": "Request timeout",
                "content": "本地DeepSeek模型响应超时，请稍后重试。",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating response from Ollama DeepSeek: {str(e)}")
            return {
                "provider": self.provider_name,
                "error": str(e),
                "content": f"本地DeepSeek模型调用出错: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        """Get available Ollama DeepSeek models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                # Filter for DeepSeek models
                deepseek_models = []
                for model in models_data.get("models", []):
                    model_name = model.get("name", "")
                    if "deepseek" in model_name.lower():
                        deepseek_models.append(model_name)
                
                if deepseek_models:
                    return deepseek_models
                else:
                    # Return common DeepSeek model names if none found
                    return ["deepseek-r1:7b", "deepseek-r1:1.5b", "deepseek-coder:6.7b"]
            else:
                logger.warning(f"Failed to fetch Ollama models: {response.status_code}")
                return ["deepseek-r1:7b", "deepseek-r1:1.5b", "deepseek-coder:6.7b"]
                
        except Exception as e:
            logger.warning(f"Error fetching Ollama models: {str(e)}")
            return ["deepseek-r1:7b", "deepseek-r1:1.5b", "deepseek-coder:6.7b"]
    
    @property
    def provider_name(self) -> str:
        return "ollama_deepseek"
    
    @property
    def provider_capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def provider_cost_tier(self) -> int:
        return self._cost_tier


class ModelSelector:
    """Intelligent model selector for choosing the best model based on query content"""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.patterns = {
            "math": r"(数学|方程|计算|积分|微分|导数|矩阵|向量|概率|统计|几何|代数|三角|函数)",
            "code": r"(代码|编程|函数|算法|程序|开发|软件|编写|实现|调试|API|接口|类|对象|变量|循环|条件|语法)",
            "electronics": r"(电路|电子|电工|电压|电流|电阻|电容|电感|晶体管|二极管|逻辑门|数字电路|模拟电路|信号|频率|波形|示波器|仿真)",
            "physics": r"(物理|力学|动力学|热力学|电磁学|光学|量子|相对论|能量|功率|速度|加速度|质量|动量|波动|振动)",
            "chemistry": r"(化学|元素|分子|原子|化合物|反应|酸碱|氧化|还原|溶液|浓度|催化剂|有机|无机|物质)",
            "biology": r"(生物|细胞|基因|蛋白质|DNA|RNA|酶|代谢|遗传|进化|生态|微生物|植物|动物|人体|组织|器官)",
            "chinese": r"[\u4e00-\u9fa5]{10,}"  # At least 10 Chinese characters
        }
    
    def select_model(self, query: str, user_preference: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Select the best model based on query content and user preference
        
        Args:
            query: The user's question
            user_preference: Optional user preferred provider
            
        Returns:
            Tuple of (provider_name, model_name, selection_reason)
        """
        # If user has a preference and it's available, use it
        if user_preference and user_preference in self.llm_manager.get_all_providers():
            provider = self.llm_manager.providers[user_preference]
            return user_preference, provider.default_model, "用户指定模型"
        
        # Detect query characteristics
        characteristics = self._detect_characteristics(query)
        logger.info(f"Detected characteristics: {characteristics}")
        
        # Check if should use Ollama DeepSeek (only for specific cases)
        if 'ollama_deepseek' in self.llm_manager.get_all_providers():
            ollama_provider = self.llm_manager.providers['ollama_deepseek']
            
            # Use Ollama DeepSeek only for:
            # 1. Code/programming questions
            # 2. Math/mathematical questions  
            # 3. When internet/cloud providers are not available
            should_use_ollama = False
            reason = ""
            
            if 'code' in characteristics:
                should_use_ollama = True
                reason = "编程问题，使用本地DeepSeek专业代码模型"
                logger.info("Using Ollama DeepSeek for code content")
            elif 'math' in characteristics:
                should_use_ollama = True
                reason = "数学问题，使用本地DeepSeek数学计算模型"
                logger.info("Using Ollama DeepSeek for math content")
            else:
                # Check if cloud providers are available
                real_api_providers = ['claude', 'gemini']
                available_real_providers = [p for p in real_api_providers if p in self.llm_manager.get_all_providers()]
                
                if not available_real_providers:
                    should_use_ollama = True
                    reason = "云端模型不可用，降级到本地DeepSeek"
                    logger.info("Using Ollama DeepSeek as fallback (no cloud providers available)")
            
            if should_use_ollama:
                try:
                    # Quick health check for Ollama
                    import requests
                    health_response = requests.get("http://localhost:11434/api/tags", timeout=2)
                    if health_response.status_code == 200:
                        logger.info(f"Selected Ollama DeepSeek, model: {ollama_provider.default_model}")
                        return 'ollama_deepseek', ollama_provider.default_model, reason
                    else:
                        logger.info("Ollama DeepSeek not available, falling back to cloud providers")
                except:
                    logger.info("Ollama DeepSeek not available, falling back to cloud providers")
        
        # 优先级顺序：Claude/Gemini > 备用AI服务(Qwen/DeepSeek) > 其他
        primary_providers = ['claude', 'gemini']
        backup_providers = ['volces_deepseek', 'ali_qwen']  # 备用AI服务
        
        # 首先尝试主要提供商 (Claude和Gemini)
        available_primary_providers = [p for p in primary_providers if p in self.llm_manager.get_all_providers()]
        
        if available_primary_providers:
            # 评分主要提供商
            providers = {name: self.llm_manager.providers[name] for name in available_primary_providers}
            scores = {}
            for name, provider in providers.items():
                score = self._calculate_provider_score(provider, characteristics)
                scores[name] = score
            
            logger.info(f"Primary provider scores: {scores}")
            
            # 选择最佳主要提供商
            best_provider_name = max(scores.items(), key=lambda x: x[1])[0]
            best_provider = self.llm_manager.providers[best_provider_name]
            
            # 生成选择理由
            reason_parts = []
            if 'physics' in characteristics:
                reason_parts.append("物理学")
            if 'chemistry' in characteristics:
                reason_parts.append("化学")
            if 'biology' in characteristics:
                reason_parts.append("生物学")
            if 'electronics' in characteristics:
                reason_parts.append("电子学")
            if 'general' in characteristics and not reason_parts:
                reason_parts.append("通用")
            
            if reason_parts:
                reason = f"{'/'.join(reason_parts)}问题，使用云端{best_provider_name.title()}专业模型"
            else:
                reason = f"使用云端{best_provider_name.title()}模型"
            
            logger.info(f"Selected primary provider: {best_provider_name}, model: {best_provider.default_model}")
            return best_provider_name, best_provider.default_model, reason
        
        # 如果主要提供商不可用，尝试备用AI服务
        available_backup_providers = [p for p in backup_providers if p in self.llm_manager.get_all_providers()]
        
        if available_backup_providers:
            # 评分备用提供商
            providers = {name: self.llm_manager.providers[name] for name in available_backup_providers}
            scores = {}
            for name, provider in providers.items():
                score = self._calculate_provider_score(provider, characteristics)
                scores[name] = score
            
            logger.info(f"Backup provider scores: {scores}")
            
            # 选择最佳备用提供商
            best_provider_name = max(scores.items(), key=lambda x: x[1])[0]
            best_provider = self.llm_manager.providers[best_provider_name]
            
            # 生成备用服务选择理由
            provider_names = {
                'volces_deepseek': '火山引擎DeepSeek',
                'ali_qwen': '阿里云通义千问'
            }
            
            reason_parts = []
            if 'code' in characteristics:
                reason_parts.append("编程")
            if 'math' in characteristics:
                reason_parts.append("数学")
            if 'chinese' in characteristics:
                reason_parts.append("中文")
            if 'general' in characteristics and not reason_parts:
                reason_parts.append("通用")
            
            provider_display_name = provider_names.get(best_provider_name, best_provider_name)
            if reason_parts:
                reason = f"{'/'.join(reason_parts)}问题，主要AI服务不可用，使用备用{provider_display_name}模型"
            else:
                reason = f"主要AI服务不可用，使用备用{provider_display_name}模型"
            
            logger.info(f"Selected backup provider: {best_provider_name}, model: {best_provider.default_model}")
            return best_provider_name, best_provider.default_model, reason
        
        # Fallback to all providers if no real API providers available
        providers = {name: self.llm_manager.providers[name] for name in self.llm_manager.get_all_providers()}
        scores = {}
        for name, provider in providers.items():
            score = self._calculate_provider_score(provider, characteristics)
            scores[name] = score
        
        logger.info(f"Fallback provider scores: {scores}")
        
        # Select the provider with the highest score
        if not scores:
            # Final fallback to default provider
            return self.llm_manager.default_provider, self.llm_manager.providers[self.llm_manager.default_provider].default_model, "默认模型"
        
        best_provider_name = max(scores.items(), key=lambda x: x[1])[0]
        best_provider = self.llm_manager.providers[best_provider_name]
        
        logger.info(f"Final fallback selected: {best_provider_name}, model: {best_provider.default_model}")
        return best_provider_name, best_provider.default_model, "备选模型"
    
    def _detect_characteristics(self, query: str) -> List[str]:
        """Detect characteristics of the query"""
        characteristics = []
        
        # Check for each pattern
        for category, pattern in self.patterns.items():
            if re.search(pattern, query):
                characteristics.append(category)
        
        # Add general by default
        characteristics.append("general")
        
        # Check query length for complexity
        if len(query) > 200:
            characteristics.append("complex")
        
        return characteristics
    
    def _calculate_provider_score(self, provider: LLMProvider, characteristics: List[str]) -> float:
        """Calculate score for a provider based on characteristics match"""
        score = 0.0
        
        # Base score from capabilities match
        for characteristic in characteristics:
            if characteristic in provider.provider_capabilities:
                score += 1.0
        
        # Adjust score based on cost tier (higher tier models get slight preference for complex queries)
        if "complex" in characteristics:
            score += provider.provider_cost_tier * 0.1
        else:
            # For simple queries, prefer lower cost models
            score += (6 - provider.provider_cost_tier) * 0.1
        
        return score


class LLMManager:
    """Manager class to handle multiple LLM providers with intelligent model selection"""
    
    def __init__(self):
        """Initialize LLM manager"""
        self.providers = {}
        self.default_provider = None
        self.model_selector = None
    
    def register_provider(self, name: str, provider: LLMProvider) -> None:
        """Register a new LLM provider"""
        self.providers[name] = provider
        if self.default_provider is None:
            self.default_provider = name
        logger.info(f"Registered provider: {name}")
    
    def set_default_provider(self, name: str) -> None:
        """Set the default LLM provider"""
        if name in self.providers:
            self.default_provider = name
            logger.info(f"Default provider set to: {name}")
        else:
            raise ValueError(f"Provider '{name}' not registered")
    
    def initialize_model_selector(self) -> None:
        """Initialize the model selector"""
        self.model_selector = ModelSelector(self)
        logger.info("Model selector initialized")
    
    async def generate_response(self, prompt: str, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate a response using the specified or auto-selected provider"""
        selection_reason = "默认模型"
        
        # Use model selector if available and no specific provider requested
        if self.model_selector and not provider:
            selected_provider, selected_model, selection_reason = self.model_selector.select_model(prompt, None)
            provider = selected_provider
            kwargs['model'] = selected_model
            logger.info(f"Auto-selected provider: {selected_provider}, model: {selected_model}")
        else:
            provider_name = provider or self.default_provider
            if provider:
                selection_reason = "用户指定模型"
            
        if provider not in self.providers:
            logger.error(f"Provider '{provider}' not found")
            return {
                "error": f"Provider '{provider}' not found",
                "content": "抱歉，请求的AI模型不可用。",
                "timestamp": datetime.now().isoformat(),
                "selection_reason": "模型不可用"
            }
        
        # Generate response and add selection information
        response = await self.providers[provider].generate_response(prompt, **kwargs)
        
        # 智能备用机制：当主要AI服务失败时自动切换到备用服务
        if "error" in response:
            error_msg = str(response.get("error", "")).lower()
            should_fallback = False
            fallback_reason = ""
            
            # 检查是否需要备用服务
            if provider in ['claude', 'gemini']:  # 主要AI服务失败
                should_fallback = True
                fallback_reason = "主要AI服务不可用，自动切换到备用AI服务"
                logger.warning(f"Primary AI service {provider} failed, attempting fallback to backup services")
            elif any(keyword in error_msg for keyword in ['connection', 'network', 'resolve', 'timeout', 'unreachable']):
                should_fallback = True
                fallback_reason = "网络连接失败，自动切换到备用AI服务"
                logger.warning(f"Network error detected with {provider}, attempting fallback")
            
            if should_fallback:
                # 备用服务优先级：火山引擎DeepSeek > 阿里云通义千问 > 本地DeepSeek
                backup_services = ['volces_deepseek', 'ali_qwen', 'ollama_deepseek']
                
                for backup_service in backup_services:
                    if backup_service in self.providers:
                        try:
                            logger.info(f"Attempting fallback to {backup_service}")
                            
                            # 特殊处理本地DeepSeek的健康检查
                            if backup_service == 'ollama_deepseek':
                                import requests
                                health_response = requests.get("http://localhost:11434/api/tags", timeout=2)
                                if health_response.status_code != 200:
                                    logger.warning("Ollama DeepSeek not available, trying next backup")
                                    continue
                            
                            # 使用备用服务生成回答
                            fallback_kwargs = kwargs.copy()
                            fallback_kwargs['model'] = self.providers[backup_service].default_model
                            fallback_response = await self.providers[backup_service].generate_response(prompt, **fallback_kwargs)
                            
                            # 如果备用服务成功，返回结果
                            if "error" not in fallback_response:
                                service_names = {
                                    'volces_deepseek': '火山引擎DeepSeek',
                                    'ali_qwen': '阿里云通义千问',
                                    'ollama_deepseek': '本地DeepSeek'
                                }
                                fallback_response["selection_reason"] = f"{fallback_reason}({service_names.get(backup_service, backup_service)})"
                                fallback_response["selected_provider"] = backup_service
                                fallback_response["fallback_from"] = provider
                                logger.info(f"Successfully fell back to {backup_service}")
                                return fallback_response
                            else:
                                logger.warning(f"Backup service {backup_service} also failed: {fallback_response.get('error', 'Unknown error')}")
                                
                        except Exception as e:
                            logger.warning(f"Failed to connect to backup service {backup_service}: {str(e)}")
                            continue
                
                # 如果所有备用服务都失败，在原始错误响应中添加备用尝试信息
                response["fallback_attempted"] = True
                response["fallback_services_tried"] = backup_services
                response["selection_reason"] = "所有AI服务均不可用"
        
        response["selection_reason"] = selection_reason
        response["selected_provider"] = provider
        
        return response
    
    def get_all_providers(self) -> List[str]:
        """Get a list of all registered providers"""
        return list(self.providers.keys())
    
    def get_provider_models(self, provider: str) -> List[str]:
        """Get available models for a specific provider"""
        if provider not in self.providers:
            logger.error(f"Provider '{provider}' not found")
            return []
        
        return self.providers[provider].get_available_models()
    
    def get_provider_capabilities(self, provider: str) -> List[str]:
        """Get capabilities for a specific provider"""
        if provider not in self.providers:
            logger.error(f"Provider '{provider}' not found")
            return []
        
        return self.providers[provider].provider_capabilities


# Create a singleton instance of LLMManager
llm_manager = LLMManager()

def initialize_llm_providers(config: Dict[str, Any]) -> None:
    """Initialize all LLM providers from configuration"""
    # Initialize OpenAI
    openai_provider = OpenAIProvider()
    openai_provider.initialize(
        api_key=config.get('openai', {}).get('api_key', ''),
        default_model=config.get('openai', {}).get('default_model', 'gpt-4o')
    )
    llm_manager.register_provider('openai', openai_provider)
    
    # Initialize DeepSeek
    deepseek_provider = DeepSeekProvider()
    deepseek_provider.initialize(
        api_key=config.get('deepseek', {}).get('api_key', ''),
        default_model=config.get('deepseek', {}).get('default_model', 'deepseek-chat')
    )
    llm_manager.register_provider('deepseek', deepseek_provider)
    
    # Initialize Volces DeepSeek (火山引擎DeepSeek) - 备用服务
    volces_deepseek_provider = VolcesDeepSeekProvider()
    volces_deepseek_provider.initialize(
        api_key=config.get('volces_deepseek', {}).get('api_key', '9c4b2be6-1c6f-4da4-b81d-41a1899136ca'),
        api_url=config.get('volces_deepseek', {}).get('api_url', 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'),
        default_model=config.get('volces_deepseek', {}).get('default_model', 'deepseek-r1-250528')
    )
    llm_manager.register_provider('volces_deepseek', volces_deepseek_provider)
    
    # Initialize Ollama DeepSeek (Local)
    ollama_deepseek_provider = OllamaDeepSeekProvider()
    ollama_deepseek_provider.initialize(
        base_url=config.get('ollama_deepseek', {}).get('base_url', 'http://localhost:11434'),
        default_model=config.get('ollama_deepseek', {}).get('default_model', 'deepseek-r1:7b')
    )
    llm_manager.register_provider('ollama_deepseek', ollama_deepseek_provider)
    
    # Initialize Qianwen (百度千问)
    qianwen_provider = QianwenProvider()
    qianwen_provider.initialize(
        api_key=config.get('qianwen', {}).get('api_key', ''),
        secret_key=config.get('qianwen', {}).get('secret_key', ''),
        default_model=config.get('qianwen', {}).get('default_model', 'ERNIE-Bot-4')
    )
    llm_manager.register_provider('qianwen', qianwen_provider)
    
    # Initialize AliQwen (阿里云通义千问) - 备用服务
    ali_qwen_provider = AliQwenProvider()
    ali_qwen_provider.initialize(
        api_key=config.get('ali_qwen', {}).get('api_key', 'sk-b2353c2803ba4d0395f91ee12100d964'),
        api_url=config.get('ali_qwen', {}).get('api_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'),
        default_model=config.get('ali_qwen', {}).get('default_model', 'qwen-plus-2025-04-28')
    )
    llm_manager.register_provider('ali_qwen', ali_qwen_provider)
    
    # Initialize Claude
    claude_provider = ClaudeProvider()
    claude_provider.initialize(
        api_key=config.get('claude', {}).get('api_key', ''),
        default_model=config.get('claude', {}).get('default_model', 'claude-3-opus')
    )
    llm_manager.register_provider('claude', claude_provider)
    
    # Initialize Gemini
    gemini_provider = GeminiProvider()
    gemini_provider.initialize(
        api_key=config.get('gemini', {}).get('api_key', ''),
        default_model=config.get('gemini', {}).get('default_model', 'gemini-pro')
    )
    llm_manager.register_provider('gemini', gemini_provider)
    
    # Initialize Llama
    llama_provider = LlamaProvider()
    llama_provider.initialize(
        api_key=config.get('llama', {}).get('api_key', ''),
        default_model=config.get('llama', {}).get('default_model', 'llama-3-70b')
    )
    llm_manager.register_provider('llama', llama_provider)
    
    # Set default provider if specified
    default_provider = config.get('default_provider', 'claude')
    if default_provider in llm_manager.get_all_providers():
        llm_manager.set_default_provider(default_provider)
    
    # Initialize model selector
    llm_manager.initialize_model_selector()
    
    logger.info(f"Initialized LLM providers: {llm_manager.get_all_providers()}")
