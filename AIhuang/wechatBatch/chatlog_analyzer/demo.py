#!/usr/bin/env python3
"""
演示模式 - 使用模拟数据展示批量群聊分析功能
"""

import sys
import os
from datetime import datetime, timedelta
from batch_analyzer import BatchAnalyzer

# 模拟聊天数据
SAMPLE_MESSAGES = [
    {'timestamp': '2024-12-12 09:00:00', 'user': '张三', 'content': '大家好，今天我们讨论一下新项目的进展'},
    {'timestamp': '2024-12-12 09:05:00', 'user': '李四', 'content': '好的，我这里准备了一份技术方案'},
    {'timestamp': '2024-12-12 09:10:00', 'user': '王五', 'content': '这个方案看起来不错，但我担心时间会不够'},
    {'timestamp': '2024-12-12 09:15:00', 'user': '赵六', 'content': '我们可以先做MVP版本，核心功能优先'},
    {'timestamp': '2024-12-12 09:20:00', 'user': '张三', 'content': '同意，我们先确定一下需求和优先级'},
    {'timestamp': '2024-12-12 09:25:00', 'user': '李四', 'content': '我整理了一份需求文档，大家看一下'},
    {'timestamp': '2024-12-12 09:30:00', 'user': '王五', 'content': '文档很详细，但我们需要考虑用户反馈'},
    {'timestamp': '2024-12-12 14:00:00', 'user': '张三', 'content': '下午好，我们继续上午的讨论'},
    {'timestamp': '2024-12-12 14:05:00', 'user': '赵六', 'content': '我测试了一下，发现几个需要优化的地方'},
    {'timestamp': '2024-12-12 14:10:00', 'user': '李四', 'content': '具体是哪些地方？我们一起讨论一下'},
    {'timestamp': '2024-12-12 14:15:00', 'user': '王五', 'content': '首先是性能问题，然后是用户体验'},
    {'timestamp': '2024-12-12 14:20:00', 'user': '张三', 'content': '好，我们逐一解决这些问题'},
    {'timestamp': '2024-12-12 14:25:00', 'user': '赵六', 'content': '我建议先优化数据库查询'},
    {'timestamp': '2024-12-12 14:30:00', 'user': '李四', 'content': '同意，然后优化前端渲染'},
    {'timestamp': '2024-12-12 19:00:00', 'user': '张三', 'content': '今天辛苦大家了，我们明天继续'},
    {'timestamp': '2024-12-12 19:05:00', 'user': '王五', 'content': '好的，明天见！'},
    {'timestamp': '2024-12-12 19:10:00', 'user': '李四', 'content': '晚安，大家明天见'},
]


class MockMCPClient:
    """模拟MCP客户端"""

    def test_connection(self):
        return True

    def batch_get_messages(self, groups):
        """返回模拟数据"""
        return {
            groups[0]['name']: SAMPLE_MESSAGES
        }


def demo():
    """运行演示"""
    print("=" * 60)
    print("[DEMO] 批量群聊分析工具 - 演示模式")
    print("=" * 60)
    print()

    # 创建分析器实例
    analyzer = BatchAnalyzer()

    # 替换MCP客户端为模拟客户端
    analyzer.mcp_client = MockMCPClient()

    # 读取群聊清单
    list_file = '../群聊清单.md'
    output_dir = './demo_reports'

    try:
        # 运行分析
        output_files = analyzer.run(
            list_file=list_file,
            output_dir=output_dir,
            date='yesterday',
            format_type='html'
        )

        print("\n" + "=" * 60)
        print("[SUCCESS] 演示完成！")
        print("=" * 60)
        print("\n生成的报告文件:")
        for group_name, file_path in output_files.items():
            print(f"  - {group_name}: {file_path}")
        print("\n请打开HTML文件查看分析结果！")

    except Exception as e:
        print(f"\n[ERROR] 演示失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    demo()
