#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alethea平台页面批量优化脚本
自动将在线CDN资源替换为本地资源
"""

import os
import re
import glob

def optimize_html_file(file_path):
    """优化单个HTML文件"""
    print(f"正在优化: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    backup_path = file_path.replace('.html', '-original.html')
    if not os.path.exists(backup_path):
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 替换在线CDN资源为本地资源
    replacements = [
        # Tailwind CSS
        (r'<script src="https://cdn\.tailwindcss\.com"></script>', 
         '<link href="/static/libs/css/tailwind.min.css" rel="stylesheet">'),
        
        # Font Awesome
        (r'<link rel="stylesheet" href="https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/6\.4\.0/css/all\.min\.css">', 
         '<link rel="stylesheet" href="/static/libs/css/fontawesome.min.css">'),
        
        # Highlight.js CSS
        (r'<link rel="stylesheet"\s+href="https://cdnjs\.cloudflare\.com/ajax/libs/highlight\.js/11\.7\.0/styles/atom-one-dark\.min\.css">', 
         '<link rel="stylesheet" href="/static/libs/css/highlight.min.css">'),
        
        # Chart.js
        (r'<script src="https://cdn\.jsdelivr\.net/npm/chart\.js"></script>', 
         '<!-- Chart.js will be loaded dynamically -->'),
        
        # Highlight.js
        (r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/highlight\.js/11\.7\.0/highlight\.min\.js"></script>', 
         '<!-- Highlight.js will be loaded dynamically -->'),
        
        # MathJax
        (r'<script src="https://polyfill\.io/v3/polyfill\.min\.js\?features=es6"></script>', ''),
        (r'<script id="MathJax-script" async src="https://cdn\.jsdelivr\.net/npm/mathjax@3/es5/tex-mml-chtml\.js"></script>', 
         '<!-- MathJax will be loaded dynamically -->'),
        
        # Google Fonts
        (r"@import url\('https://fonts\.googleapis\.com/css2\?family=Noto\+Sans\+SC:wght@300;400;500;700&display=swap'\);", 
         '''@font-face {
            font-family: 'Noto Sans SC';
            font-style: normal;
            font-weight: 400;
            font-display: swap;
            src: local('Noto Sans SC Regular'), local('NotoSansSC-Regular'),
                 url('/static/libs/fonts/noto-sans-sc-v36-chinese-simplified-regular.woff2') format('woff2');
        }'''),
    ]
    
    # 应用替换
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # 添加延迟加载脚本（如果还没有）
    if 'loadScript' not in content and '</body>' in content:
        load_script = '''
    <script>
        // 延迟加载脚本函数
        function loadScript(src, callback) {
            const script = document.createElement('script');
            script.src = src;
            script.onload = callback;
            document.head.appendChild(script);
        }

        // 页面加载完成后加载非关键资源
        window.addEventListener('load', function() {
            // 延迟加载Chart.js
            if (document.querySelector('canvas')) {
                loadScript('/static/libs/js/chart.min.js');
            }
            
            // 延迟加载Highlight.js
            if (document.querySelector('pre code')) {
                loadScript('/static/libs/js/highlight.min.js', function() {
                    if (window.hljs) {
                        hljs.highlightAll();
                    }
                });
            }

            // 延迟加载MathJax
            if (document.querySelector('.math') || document.querySelector('[data-math]')) {
                loadScript('/static/libs/js/mathjax.min.js');
            }
        });
    </script>
</body>'''
        content = content.replace('</body>', load_script)
    
    # 添加字体fallback到body样式
    if 'font-family:' in content and 'Noto Sans SC' in content:
        content = re.sub(
            r"font-family:\s*'Noto Sans SC',\s*sans-serif;",
            "font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
            content
        )
    
    # 创建优化版本
    optimized_path = file_path.replace('.html', '-optimized.html')
    with open(optimized_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"优化完成: {optimized_path}")
    return optimized_path

def main():
    """主函数"""
    print("Alethea平台页面批量优化工具")
    print("=" * 50)
    
    # 获取所有HTML文件
    html_files = glob.glob('src/static/*.html')
    
    # 排除已经优化的文件和备份文件
    html_files = [f for f in html_files if not f.endswith('-optimized.html') and not f.endswith('-original.html')]
    
    print(f"找到 {len(html_files)} 个HTML文件需要优化")
    
    optimized_files = []
    
    for file_path in html_files:
        try:
            optimized_path = optimize_html_file(file_path)
            optimized_files.append(optimized_path)
        except Exception as e:
            print(f"优化失败 {file_path}: {e}")
    
    print("\n" + "=" * 50)
    print("批量优化完成！")
    print(f"成功优化 {len(optimized_files)} 个文件")
    
    print("\n优化后的文件列表:")
    for file_path in optimized_files:
        print(f"  - {file_path}")
    
    print("\n使用说明:")
    print("1. 所有原文件已备份为 *-original.html")
    print("2. 优化后的文件为 *-optimized.html")
    print("3. 如需部署，请将优化版本重命名为原文件名")
    print("4. 确保 src/static/libs/ 目录下有所需的本地资源文件")

if __name__ == "__main__":
    main()
