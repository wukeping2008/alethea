#!/usr/bin/env python3
"""
Ollama DeepSeek 连接测试脚本
用于验证本地 Ollama DeepSeek 模型的可用性
"""

import requests
import json
import sys
from datetime import datetime

def test_ollama_connection():
    """测试 Ollama 服务连接"""
    print("🔍 测试 Ollama 服务连接...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama 服务运行正常")
            return True, response.json()
        else:
            print(f"❌ Ollama 服务响应异常: {response.status_code}")
            return False, None
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 Ollama 服务 (http://localhost:11434)")
        print("   请确保 Ollama 已启动: ollama serve")
        return False, None
    except requests.exceptions.Timeout:
        print("❌ Ollama 服务连接超时")
        return False, None
    except Exception as e:
        print(f"❌ 连接错误: {str(e)}")
        return False, None

def check_deepseek_models(models_data):
    """检查可用的 DeepSeek 模型"""
    print("\n🔍 检查 DeepSeek 模型...")
    
    if not models_data or "models" not in models_data:
        print("❌ 无法获取模型列表")
        return []
    
    deepseek_models = []
    for model in models_data["models"]:
        model_name = model.get("name", "")
        if "deepseek" in model_name.lower():
            deepseek_models.append(model_name)
            size_gb = model.get("size", 0) / (1024**3)
            modified = model.get("modified_at", "")
            print(f"✅ 发现 DeepSeek 模型: {model_name}")
            print(f"   大小: {size_gb:.1f} GB")
            print(f"   修改时间: {modified}")
    
    if not deepseek_models:
        print("❌ 未找到 DeepSeek 模型")
        print("   请安装 DeepSeek 模型:")
        print("   ollama pull deepseek-r1:7b")
        print("   或")
        print("   ollama pull deepseek-r1:1.5b")
    
    return deepseek_models

def test_deepseek_generation(model_name):
    """测试 DeepSeek 模型生成"""
    print(f"\n🔍 测试 {model_name} 模型生成...")
    
    test_prompt = "请简单介绍一下Python编程语言的特点"
    
    try:
        data = {
            "model": model_name,
            "prompt": test_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 100
            }
        }
        
        print(f"📤 发送测试请求: {test_prompt}")
        response = requests.post(
            "http://localhost:11434/api/generate",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "")
            print("✅ 模型生成成功!")
            print(f"📝 生成内容: {generated_text[:200]}...")
            return True
        else:
            print(f"❌ 生成失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 生成请求超时")
        return False
    except Exception as e:
        print(f"❌ 生成错误: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 Ollama DeepSeek 连接测试")
    print("=" * 60)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试 Ollama 连接
    is_connected, models_data = test_ollama_connection()
    if not is_connected:
        print("\n❌ 测试失败: Ollama 服务不可用")
        print("\n📋 解决方案:")
        print("1. 安装 Ollama: https://ollama.ai/")
        print("2. 启动 Ollama 服务: ollama serve")
        print("3. 安装 DeepSeek 模型: ollama pull deepseek-r1:7b")
        sys.exit(1)
    
    # 检查 DeepSeek 模型
    deepseek_models = check_deepseek_models(models_data)
    if not deepseek_models:
        print("\n❌ 测试失败: 未找到 DeepSeek 模型")
        sys.exit(1)
    
    # 测试模型生成
    test_model = deepseek_models[0]
    generation_success = test_deepseek_generation(test_model)
    
    print("\n" + "=" * 60)
    if generation_success:
        print("🎉 所有测试通过! Ollama DeepSeek 已准备就绪")
        print(f"🔧 推荐模型: {test_model}")
        print("🌐 Alethea Enhanced 将自动使用本地 DeepSeek 处理中文和代码问题")
    else:
        print("❌ 测试失败: 模型生成异常")
    print("=" * 60)

if __name__ == "__main__":
    main()
