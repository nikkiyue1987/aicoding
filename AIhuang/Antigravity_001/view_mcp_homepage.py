# -*- coding: utf-8 -*-
"""
获取 MCP 服务器主页内容
"""

import requests
from bs4 import BeautifulSoup
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'http://127.0.0.1:5030'

print("正在获取 MCP 服务器主页...")
print()

try:
    response = requests.get(base_url, timeout=5)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题
        title = soup.find('title')
        print(f"页面标题: {title.text if title else 'N/A'}")
        print()
        
        # 提取所有链接
        print("=" * 70)
        print("可用的链接:")
        print("=" * 70)
        links = soup.find_all('a')
        for link in links:
            href = link.get('href', '')
            text = link.text.strip()
            if href and text:
                print(f"  {text}: {href}")
        
        print()
        print("=" * 70)
        print("页面主要内容:")
        print("=" * 70)
        
        # 提取主要文本内容
        # 移除 script 和 style 标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        print(text[:2000])  # 打印前 2000 个字符
        
except Exception as e:
    print(f"错误: {e}")
