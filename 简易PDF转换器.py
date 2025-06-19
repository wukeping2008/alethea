"""
简易PDF转换器 - 使用浏览器打印功能
将HTML文件转换为PDF的简单方法
"""

import os
import webbrowser
import time

def convert_html_to_pdf_manual():
    """手动转换HTML到PDF的指导"""
    
    html_file = "Alethea平台三层架构说明图.html"
    
    if not os.path.exists(html_file):
        print(f"错误: 找不到HTML文件 {html_file}")
        return
    
    # 获取HTML文件的绝对路径
    html_path = os.path.abspath(html_file)
    file_url = f"file:///{html_path.replace(os.sep, '/')}"
    
    print("=== 简易PDF转换指南 ===\n")
    print("由于自动PDF转换遇到技术问题，请按以下步骤手动转换：\n")
    
    print("步骤1: 即将在浏览器中打开HTML文件...")
    print(f"文件路径: {file_url}\n")
    
    # 在默认浏览器中打开HTML文件
    webbrowser.open(file_url)
    
    print("步骤2: 在浏览器中按 Ctrl+P (Windows) 或 Cmd+P (Mac) 打开打印对话框")
    print("步骤3: 在打印对话框中选择 '另存为PDF' 或 'Save as PDF'")
    print("步骤4: 设置以下打印选项：")
    print("   - 页面大小: A4")
    print("   - 边距: 最小")
    print("   - 背景图形: 开启")
    print("   - 页眉页脚: 关闭")
    print("步骤5: 点击 '保存' 并选择保存位置")
    print("步骤6: 将文件命名为 'Alethea平台三层架构说明图.pdf'\n")
    
    print("✓ HTML文件已在浏览器中打开")
    print("✓ Word文档已生成: Alethea平台三层架构说明图.docx")
    print("\n按照上述步骤即可手动生成PDF文件。")

if __name__ == "__main__":
    convert_html_to_pdf_manual()
