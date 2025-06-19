#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alethea平台API密钥配置助手
帮助用户快速配置AI提供商的API密钥
"""

import json
import os
import sys
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🚀 Alethea平台API密钥配置助手")
    print("=" * 60)
    print("本工具将帮助您配置AI提供商的API密钥")
    print("确保AI功能正常运行")
    print()

def get_config_path():
    """获取配置文件路径"""
    script_dir = Path(__file__).parent
    config_path = script_dir / "src" / "config.json"
    example_path = script_dir / "src" / "config.json.example"
    
    return config_path, example_path

def load_existing_config(config_path):
    """加载现有配置"""
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  警告：现有配置文件格式错误: {e}")
            return None
    return None

def get_default_config():
    """获取默认配置模板"""
    return {
        "claude": {
            "api_key": "",
            "default_model": "claude-3-sonnet-20240229"
        },
        "gemini": {
            "api_key": "",
            "default_model": "gemini-1.5-flash"
        },
        "volces_deepseek": {
            "api_key": "",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            "default_model": "deepseek-r1-250528",
            "max_tokens": 16191
        },
        "qwen_plus": {
            "api_key": "",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "default_model": "qwen-plus-2025-04-28",
            "max_tokens": 16191
        },
        "openai": {
            "api_key": "",
            "default_model": "gpt-4o"
        },
        "default_provider": "gemini"
    }

def show_provider_info():
    """显示提供商信息"""
    providers = {
        "1": {
            "name": "Google Gemini",
            "key": "gemini",
            "description": "免费额度较高，响应快速，推荐新手使用",
            "get_key": "https://makersuite.google.com/app/apikey",
            "example": "AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        },
        "2": {
            "name": "火山引擎DeepSeek",
            "key": "volces_deepseek", 
            "description": "中文优化，推理能力强，适合中文场景",
            "get_key": "https://console.volcengine.com/ark",
            "example": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        },
        "3": {
            "name": "阿里云通义千问Plus",
            "key": "qwen_plus",
            "description": "中文理解优秀，成本较低",
            "get_key": "https://dashscope.aliyuncs.com/",
            "example": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        },
        "4": {
            "name": "Claude (Anthropic)",
            "key": "claude",
            "description": "高质量回答，适合复杂推理，但成本较高",
            "get_key": "https://console.anthropic.com/",
            "example": "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        },
        "5": {
            "name": "OpenAI",
            "key": "openai",
            "description": "通用性强，但需要科学上网",
            "get_key": "https://platform.openai.com/api-keys",
            "example": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }
    }
    
    print("📋 支持的AI提供商：")
    print()
    for num, info in providers.items():
        print(f"{num}. {info['name']}")
        print(f"   特点：{info['description']}")
        print(f"   获取密钥：{info['get_key']}")
        print(f"   密钥格式：{info['example']}")
        print()
    
    return providers

def configure_provider(provider_info, config, current_key=""):
    """配置单个提供商"""
    name = provider_info['name']
    key = provider_info['key']
    
    print(f"🔧 配置 {name}")
    print(f"获取API密钥：{provider_info['get_key']}")
    print(f"密钥格式示例：{provider_info['example']}")
    
    if current_key:
        print(f"当前密钥：{current_key[:10]}...{current_key[-10:] if len(current_key) > 20 else current_key}")
        choice = input("是否更新密钥？(y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            return config
    
    while True:
        api_key = input(f"请输入{name}的API密钥 (留空跳过): ").strip()
        
        if not api_key:
            print(f"跳过{name}配置")
            return config
        
        # 基本验证
        if len(api_key) < 10:
            print("❌ API密钥长度太短，请检查")
            continue
        
        # 格式验证
        valid_format = False
        if key == "gemini" and api_key.startswith("AIzaSy"):
            valid_format = True
        elif key == "claude" and api_key.startswith("sk-ant-"):
            valid_format = True
        elif key == "openai" and api_key.startswith("sk-"):
            valid_format = True
        elif key in ["volces_deepseek", "qwen_plus"]:
            valid_format = True  # 这些提供商格式较多样
        
        if not valid_format and key in ["gemini", "claude", "openai"]:
            print(f"⚠️  警告：API密钥格式可能不正确")
            choice = input("是否继续？(y/N): ").strip().lower()
            if choice not in ['y', 'yes']:
                continue
        
        # 保存配置
        config[key]["api_key"] = api_key
        print(f"✅ {name} API密钥配置成功")
        return config

def choose_default_provider(config):
    """选择默认提供商"""
    configured_providers = []
    provider_names = {
        "gemini": "Google Gemini",
        "volces_deepseek": "火山引擎DeepSeek", 
        "qwen_plus": "阿里云通义千问Plus",
        "claude": "Claude",
        "openai": "OpenAI"
    }
    
    for key, provider_config in config.items():
        if isinstance(provider_config, dict) and provider_config.get("api_key"):
            configured_providers.append(key)
    
    if not configured_providers:
        print("❌ 没有配置任何API密钥，无法设置默认提供商")
        return config
    
    print("\n🎯 选择默认AI提供商：")
    for i, provider in enumerate(configured_providers, 1):
        name = provider_names.get(provider, provider)
        print(f"{i}. {name}")
    
    while True:
        try:
            choice = input(f"请选择默认提供商 (1-{len(configured_providers)}): ").strip()
            if not choice:
                # 使用推荐的默认值
                if "gemini" in configured_providers:
                    config["default_provider"] = "gemini"
                else:
                    config["default_provider"] = configured_providers[0]
                break
            
            index = int(choice) - 1
            if 0 <= index < len(configured_providers):
                config["default_provider"] = configured_providers[index]
                break
            else:
                print("❌ 选择无效，请重新输入")
        except ValueError:
            print("❌ 请输入数字")
    
    provider_name = provider_names.get(config["default_provider"], config["default_provider"])
    print(f"✅ 默认提供商设置为：{provider_name}")
    return config

def save_config(config, config_path):
    """保存配置文件"""
    try:
        # 确保目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        # 设置文件权限（仅所有者可读写）
        try:
            os.chmod(config_path, 0o600)
        except:
            pass  # Windows可能不支持
        
        print(f"✅ 配置已保存到：{config_path}")
        return True
    except Exception as e:
        print(f"❌ 保存配置失败：{e}")
        return False

def validate_config(config):
    """验证配置"""
    issues = []
    
    # 检查是否至少有一个API密钥
    has_api_key = False
    for key, provider_config in config.items():
        if isinstance(provider_config, dict) and provider_config.get("api_key"):
            has_api_key = True
            break
    
    if not has_api_key:
        issues.append("❌ 至少需要配置一个AI提供商的API密钥")
    
    # 检查默认提供商是否有效
    default_provider = config.get("default_provider")
    if default_provider and default_provider in config:
        if not config[default_provider].get("api_key"):
            issues.append(f"⚠️  默认提供商 {default_provider} 没有配置API密钥")
    
    return issues

def show_summary(config):
    """显示配置摘要"""
    print("\n" + "=" * 50)
    print("📊 配置摘要")
    print("=" * 50)
    
    provider_names = {
        "gemini": "Google Gemini",
        "volces_deepseek": "火山引擎DeepSeek", 
        "qwen_plus": "阿里云通义千问Plus",
        "claude": "Claude",
        "openai": "OpenAI"
    }
    
    configured_count = 0
    for key, provider_config in config.items():
        if isinstance(provider_config, dict):
            name = provider_names.get(key, key)
            has_key = bool(provider_config.get("api_key"))
            status = "✅ 已配置" if has_key else "❌ 未配置"
            print(f"{name}: {status}")
            if has_key:
                configured_count += 1
    
    default_provider = config.get("default_provider", "未设置")
    default_name = provider_names.get(default_provider, default_provider)
    print(f"\n默认提供商: {default_name}")
    print(f"已配置提供商数量: {configured_count}")
    
    # 验证配置
    issues = validate_config(config)
    if issues:
        print("\n⚠️  配置问题：")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n🎉 配置验证通过！")

def main():
    """主函数"""
    print_banner()
    
    # 获取配置文件路径
    config_path, example_path = get_config_path()
    
    # 检查src目录是否存在
    if not config_path.parent.exists():
        print(f"❌ 错误：找不到src目录 ({config_path.parent})")
        print("请确保在Alethea项目根目录下运行此脚本")
        sys.exit(1)
    
    # 加载现有配置或使用默认配置
    config = load_existing_config(config_path)
    if config is None:
        config = get_default_config()
        print("📝 使用默认配置模板")
    else:
        print("📂 加载现有配置文件")
    
    # 显示提供商信息
    providers = show_provider_info()
    
    print("💡 建议：至少配置一个提供商，推荐配置2-3个作为备用")
    print("推荐优先级：Gemini > 火山引擎DeepSeek > 阿里云通义千问 > Claude")
    print()
    
    # 配置提供商
    while True:
        choice = input("选择要配置的提供商 (1-5) 或按回车完成配置: ").strip()
        
        if not choice:
            break
        
        if choice in providers:
            provider_info = providers[choice]
            current_key = config[provider_info['key']].get("api_key", "")
            config = configure_provider(provider_info, config, current_key)
        else:
            print("❌ 无效选择，请输入1-5")
    
    # 选择默认提供商
    config = choose_default_provider(config)
    
    # 显示配置摘要
    show_summary(config)
    
    # 保存配置
    if validate_config(config):
        save_choice = input("\n💾 是否保存配置？(Y/n): ").strip().lower()
        if save_choice not in ['n', 'no']:
            if save_config(config, config_path):
                print("\n🎉 配置完成！")
                print("现在可以启动Alethea平台：")
                print("  cd /path/to/alethea")
                print("  python src/main.py")
                print("\n访问平台：http://localhost:8083")
            else:
                print("\n❌ 配置保存失败")
                sys.exit(1)
        else:
            print("❌ 配置未保存")
    else:
        print("\n❌ 配置验证失败，请检查配置")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 配置已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
        sys.exit(1)
