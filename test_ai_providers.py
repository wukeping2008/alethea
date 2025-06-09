#!/usr/bin/env python3
"""
AI提供商测试脚本
测试所有已配置的AI提供商是否能正常调用
"""

import requests
import json
import time
import sys
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8083"
TEST_QUESTIONS = [
    {
        "question": "什么是PID控制器？",
        "expected_keywords": ["比例", "积分", "微分", "控制"],
        "category": "控制理论"
    },
    {
        "question": "解释欧姆定律",
        "expected_keywords": ["电压", "电流", "电阻", "V=IR"],
        "category": "电路理论"
    },
    {
        "question": "什么是机器学习？",
        "expected_keywords": ["算法", "数据", "模型", "学习"],
        "category": "人工智能"
    }
]

# 所有AI提供商列表
AI_PROVIDERS = [
    "openai",
    "deepseek", 
    "volces_deepseek",
    "ollama_deepseek",
    "qianwen",
    "ali_qwen",
    "claude",
    "gemini",
    "llama"
]

def test_ai_provider(provider, question_data):
    """测试单个AI提供商"""
    print(f"\n🤖 测试提供商: {provider}")
    print(f"📝 问题: {question_data['question']}")
    
    try:
        # 构建请求数据
        request_data = {
            "question": question_data["question"],
            "provider": provider,
            "model": None,
            "options": {
                "language": "zh-CN",
                "response_language": "chinese"
            }
        }
        
        # 发送请求
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/llm/ask",
            json=request_data,
            timeout=60
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("content", "")
            
            # 检查响应内容
            if content and len(content.strip()) > 10:
                # 检查是否包含期望的关键词
                keyword_found = any(keyword in content for keyword in question_data["expected_keywords"])
                
                print(f"✅ 成功 - 响应时间: {response_time:.2f}秒")
                print(f"📊 内容长度: {len(content)}字符")
                print(f"🔍 关键词匹配: {'是' if keyword_found else '否'}")
                print(f"📄 响应预览: {content[:100]}...")
                
                return {
                    "provider": provider,
                    "status": "success",
                    "response_time": response_time,
                    "content_length": len(content),
                    "keyword_match": keyword_found,
                    "selected_model": result.get("model", "unknown"),
                    "error": None
                }
            else:
                print(f"❌ 失败 - 响应内容为空或过短")
                return {
                    "provider": provider,
                    "status": "empty_response",
                    "response_time": response_time,
                    "error": "Empty or too short response"
                }
        else:
            print(f"❌ 失败 - HTTP状态码: {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get("error", "Unknown error")
            except:
                error_msg = response.text
            
            return {
                "provider": provider,
                "status": "http_error",
                "response_time": response_time,
                "error": f"HTTP {response.status_code}: {error_msg}"
            }
            
    except requests.exceptions.Timeout:
        print(f"⏰ 超时 - 请求超过60秒")
        return {
            "provider": provider,
            "status": "timeout",
            "error": "Request timeout (60s)"
        }
    except requests.exceptions.ConnectionError:
        print(f"🔌 连接错误 - 无法连接到服务器")
        return {
            "provider": provider,
            "status": "connection_error",
            "error": "Connection error"
        }
    except Exception as e:
        print(f"💥 异常 - {str(e)}")
        return {
            "provider": provider,
            "status": "exception",
            "error": str(e)
        }

def test_auto_selection():
    """测试自动模型选择功能"""
    print(f"\n🎯 测试自动模型选择功能")
    
    test_cases = [
        {
            "question": "计算积分 ∫x²dx",
            "expected_provider": ["deepseek", "ollama_deepseek"],  # 数学问题
            "category": "数学"
        },
        {
            "question": "写一个Python冒泡排序算法",
            "expected_provider": ["deepseek", "ollama_deepseek"],  # 编程问题
            "category": "编程"
        },
        {
            "question": "今天天气怎么样？",
            "expected_provider": ["claude", "gemini"],  # 一般问题
            "category": "一般"
        }
    ]
    
    results = []
    for case in test_cases:
        print(f"\n📝 测试问题: {case['question']}")
        
        try:
            request_data = {
                "question": case["question"],
                "provider": None,  # 让系统自动选择
                "model": None,
                "options": {
                    "language": "zh-CN",
                    "response_language": "chinese"
                }
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/llm/ask",
                json=request_data,
                timeout=60
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                selected_provider = result.get("selected_provider", "unknown")
                selected_model = result.get("model", "unknown")
                selection_reason = result.get("selection_reason", "No reason provided")
                
                print(f"✅ 自动选择: {selected_provider} ({selected_model})")
                print(f"🤔 选择理由: {selection_reason}")
                
                # 检查是否选择了合适的提供商
                is_appropriate = selected_provider in case["expected_provider"]
                print(f"🎯 选择合适性: {'是' if is_appropriate else '否'}")
                
                results.append({
                    "question": case["question"],
                    "category": case["category"],
                    "selected_provider": selected_provider,
                    "selected_model": selected_model,
                    "selection_reason": selection_reason,
                    "is_appropriate": is_appropriate,
                    "response_time": end_time - start_time
                })
            else:
                print(f"❌ 自动选择失败 - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"💥 自动选择测试异常: {str(e)}")
    
    return results

def generate_report(all_results, auto_selection_results):
    """生成测试报告"""
    print(f"\n" + "="*80)
    print(f"📊 AI提供商测试报告")
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"="*80)
    
    # 统计成功率
    total_tests = len(all_results)
    successful_tests = len([r for r in all_results if r["status"] == "success"])
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n📈 总体统计:")
    print(f"   总测试数: {total_tests}")
    print(f"   成功数: {successful_tests}")
    print(f"   成功率: {success_rate:.1f}%")
    
    # 按状态分组
    status_groups = {}
    for result in all_results:
        status = result["status"]
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(result)
    
    print(f"\n📋 详细结果:")
    for status, results in status_groups.items():
        print(f"\n   {status.upper()} ({len(results)}个):")
        for result in results:
            provider = result["provider"]
            if status == "success":
                response_time = result.get("response_time", 0)
                content_length = result.get("content_length", 0)
                keyword_match = result.get("keyword_match", False)
                model = result.get("selected_model", "unknown")
                print(f"     ✅ {provider} - {response_time:.2f}s, {content_length}字符, 关键词:{'✓' if keyword_match else '✗'}, 模型:{model}")
            else:
                error = result.get("error", "Unknown error")
                print(f"     ❌ {provider} - {error}")
    
    # 自动选择测试结果
    if auto_selection_results:
        print(f"\n🎯 自动模型选择测试:")
        for result in auto_selection_results:
            category = result["category"]
            selected = result["selected_provider"]
            appropriate = result["is_appropriate"]
            response_time = result["response_time"]
            print(f"   {category}: {selected} ({'✓' if appropriate else '✗'}) - {response_time:.2f}s")
    
    # 推荐修复措施
    failed_providers = [r["provider"] for r in all_results if r["status"] != "success"]
    if failed_providers:
        print(f"\n🔧 需要修复的提供商:")
        for provider in failed_providers:
            failed_result = next(r for r in all_results if r["provider"] == provider)
            error = failed_result.get("error", "Unknown error")
            print(f"   ❌ {provider}: {error}")
            
            # 提供修复建议
            if "timeout" in error.lower():
                print(f"      💡 建议: 检查网络连接或增加超时时间")
            elif "connection" in error.lower():
                print(f"      💡 建议: 检查API密钥配置和网络连接")
            elif "401" in error or "unauthorized" in error.lower():
                print(f"      💡 建议: 检查API密钥是否正确配置")
            elif "404" in error:
                print(f"      💡 建议: 检查API端点URL是否正确")
            elif "empty" in error.lower():
                print(f"      💡 建议: 检查模型配置和请求参数")

def main():
    """主测试函数"""
    print(f"🚀 开始AI提供商全面测试")
    print(f"🌐 服务器地址: {BASE_URL}")
    print(f"📝 测试问题数: {len(TEST_QUESTIONS)}")
    print(f"🤖 AI提供商数: {len(AI_PROVIDERS)}")
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ 服务器未正常运行，状态码: {response.status_code}")
            return
    except:
        print(f"❌ 无法连接到服务器 {BASE_URL}")
        print(f"💡 请确保服务器正在运行: python3 src/main.py")
        return
    
    print(f"✅ 服务器连接正常")
    
    # 测试所有提供商
    all_results = []
    
    for i, question_data in enumerate(TEST_QUESTIONS, 1):
        print(f"\n" + "="*60)
        print(f"📋 测试轮次 {i}/{len(TEST_QUESTIONS)}: {question_data['category']}")
        print(f"="*60)
        
        for provider in AI_PROVIDERS:
            result = test_ai_provider(provider, question_data)
            result["question_category"] = question_data["category"]
            result["question"] = question_data["question"]
            all_results.append(result)
            
            # 在测试之间稍作停顿，避免请求过于频繁
            time.sleep(1)
    
    # 测试自动模型选择
    print(f"\n" + "="*60)
    print(f"🎯 自动模型选择测试")
    print(f"="*60)
    auto_selection_results = test_auto_selection()
    
    # 生成报告
    generate_report(all_results, auto_selection_results)
    
    # 保存详细结果到文件
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "server_url": BASE_URL,
        "test_questions": TEST_QUESTIONS,
        "ai_providers": AI_PROVIDERS,
        "detailed_results": all_results,
        "auto_selection_results": auto_selection_results
    }
    
    with open("/Users/kepingwu/Desktop/alethea_enhanced/ai_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细测试报告已保存到: ai_test_report.json")
    print(f"🎉 测试完成！")

if __name__ == "__main__":
    main()
