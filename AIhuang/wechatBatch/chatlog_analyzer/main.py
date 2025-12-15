#!/usr/bin/env python3
"""
批量群聊分析工具 - 主入口
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入并运行主程序
from batch_analyzer import main

if __name__ == '__main__':
    main()
