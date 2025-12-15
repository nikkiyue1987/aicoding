"""
批量群聊分析工具 - 主程序
整合所有模块，实现批量分析和报告生成
"""

import argparse
import sys
import os
from datetime import datetime
from typing import List, Dict
import json

# 导入自定义模块
from md_parser import MarkdownParser, GroupChatConfig
from chatlog_client import ChatlogMCPClient
from topic_analyzer import TopicAnalyzer
from html_generator import HTMLGenerator


class BatchAnalyzer:
    """批量群聊分析器"""

    def __init__(self, mcp_url: str = "http://127.0.0.1:5030"):
        """
        初始化分析器

        Args:
            mcp_url: Chatlog MCP服务器URL
        """
        self.mcp_client = ChatlogMCPClient(mcp_url)
        self.topic_analyzer = TopicAnalyzer()
        self.html_generator = HTMLGenerator()

    def run(
        self,
        list_file: str,
        output_dir: str = None,
        date: str = None,
        format_type: str = "html"
    ) -> Dict[str, str]:
        """
        运行批量分析

        Args:
            list_file: 群聊清单文件路径
            output_dir: 输出目录
            date: 默认日期（覆盖清单中的日期）
            format_type: 输出格式

        Returns:
            生成的文件路径映射
        """
        print("=" * 60)
        print("[START] 批量群聊分析工具启动")
        print("=" * 60)

        # 1. 解析群聊清单
        print("\n[INFO] 步骤1: 解析群聊清单...")
        try:
            group_chats = self._parse_group_list(list_file, date)
            print(f"  [OK] 成功解析 {len(group_chats)} 个群聊配置")
            for group in group_chats:
                print(f"    - {group.name} (日期: {group.date})")
        except Exception as e:
            print(f"  [ERROR] 解析失败: {str(e)}")
            raise

        # 2. 测试MCP连接
        print("\n[CONNECT] 步骤2: 测试MCP服务器连接...")
        if not self.mcp_client.test_connection():
            print(f"  [ERROR] 无法连接到MCP服务器 ({self.mcp_client.sse_url})")
            print("  请确保Chatlog MCP服务器正在运行")
            raise ConnectionError("MCP服务器连接失败")
        print("  [OK] MCP服务器连接正常")

        # 3. 获取聊天数据
        print("\n[FETCH] 步骤3: 获取聊天记录...")
        try:
            # 转换为字典格式
            groups_dict = [
                {
                    'name': g.name,
                    'date': g.date,
                    'format': g.format
                }
                for g in group_chats
            ]

            chat_data = self.mcp_client.batch_get_messages(groups_dict)
            print(f"  [OK] 成功获取 {len(chat_data)} 个群聊的数据")
        except Exception as e:
            print(f"  [ERROR] 获取数据失败: {str(e)}")
            raise

        # 4. 分析话题
        print("\n[ANALYZE] 步骤4: 分析话题...")
        analysis_results = {}
        for group_name, messages in chat_data.items():
            print(f"  正在分析: {group_name}...")
            try:
                result = self.topic_analyzer.analyze_chat_data(messages)
                analysis_results[group_name] = result
                topic_count = len(result.get('topics', []))
                print(f"    [OK] 找到 {topic_count} 个话题")
            except Exception as e:
                print(f"    [ERROR] 分析失败: {str(e)}")
                analysis_results[group_name] = {
                    'topics': [],
                    'total_messages': len(messages),
                    'total_participants': 0,
                    'error': str(e)
                }

        # 5. 生成HTML报告
        print("\n[REPORT] 步骤5: 生成HTML报告...")
        output_files = {}
        output_dir = output_dir or self._get_default_output_dir()

        for group_name, result in analysis_results.items():
            try:
                # 清理文件名
                safe_name = self._sanitize_filename(group_name)
                file_path = os.path.join(output_dir, f"{safe_name}.html")

                # 生成HTML
                self.html_generator.generate_report(group_name, result, file_path)
                output_files[group_name] = file_path
                print(f"  [OK] {group_name} -> {file_path}")
            except Exception as e:
                print(f"  [ERROR] {group_name} 生成失败: {str(e)}")

        # 6. 生成汇总报告
        print("\n[STATS] 步骤6: 生成汇总报告...")
        try:
            summary_file = self._generate_summary_report(
                group_chats,
                analysis_results,
                output_dir
            )
            output_files['summary'] = summary_file
            print(f"  [OK] 汇总报告: {summary_file}")
        except Exception as e:
            print(f"  [ERROR] 汇总报告生成失败: {str(e)}")

        # 完成
        print("\n" + "=" * 60)
        print(f"[DONE] 分析完成! 共生成 {len(output_files)} 个文件")
        print(f"[OUTPUT] 输出目录: {output_dir}")
        print("=" * 60)

        return output_files

    def _parse_group_list(self, list_file: str, override_date: str = None) -> List[GroupChatConfig]:
        """
        解析群聊清单

        Args:
            list_file: 清单文件路径
            override_date: 覆盖日期

        Returns:
            群聊配置列表
        """
        groups = MarkdownParser.parse_group_chats(list_file)

        # 如果指定了覆盖日期，更新所有群聊的日期
        if override_date:
            for group in groups:
                group.date = override_date

        return groups

    def _get_default_output_dir(self) -> str:
        """获取默认输出目录"""
        today = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(os.getcwd(), f"chatlog_reports_{today}")

    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名

        Args:
            filename: 原始文件名

        Returns:
            清理后的文件名
        """
        # 替换非法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # 限制长度
        if len(filename) > 100:
            filename = filename[:100]

        return filename

    def _generate_summary_report(
        self,
        group_chats: List[GroupChatConfig],
        analysis_results: Dict,
        output_dir: str
    ) -> str:
        """
        生成汇总报告

        Args:
            group_chats: 群聊配置列表
            analysis_results: 分析结果
            output_dir: 输出目录

        Returns:
            汇总报告文件路径
        """
        summary_data = {
            'total_groups': len(group_chats),
            'total_messages': sum(
                result.get('total_messages', 0)
                for result in analysis_results.values()
            ),
            'total_topics': sum(
                len(result.get('topics', []))
                for result in analysis_results.values()
            ),
            'groups': []
        }

        for group_name, result in analysis_results.items():
            group_info = {
                'name': group_name,
                'messages': result.get('total_messages', 0),
                'participants': result.get('total_participants', 0),
                'topics': len(result.get('topics', [])),
                'top_topic': None
            }

            # 获取最热门话题
            topics = result.get('topics', [])
            if topics:
                top_topic = topics[0]
                group_info['top_topic'] = {
                    'title': top_topic.get('title', ''),
                    'score': top_topic.get('score', 0),
                    'keywords': top_topic.get('keywords', [])
                }

            summary_data['groups'].append(group_info)

        # 生成汇总HTML
        summary_html = self._build_summary_html(summary_data)
        summary_file = os.path.join(output_dir, "summary.html")

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_html)

        # 保存JSON数据
        json_file = os.path.join(output_dir, "summary.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        return summary_file

    def _build_summary_html(self, data: Dict) -> str:
        """
        构建汇总HTML

        Args:
            data: 汇总数据

        Returns:
            HTML字符串
        """
        today = datetime.now().strftime('%Y-%m-%d')

        # 生成群聊卡片
        group_cards = []
        for group in data['groups']:
            top_topic = group.get('top_topic')
            topic_info = f"""
            <div style="background: rgba(102, 126, 234, 0.1); padding: 10px; border-radius: 8px; margin-top: 10px;">
                <strong>🔥 热门话题:</strong> {top_topic.get('title', 'N/A')}<br>
                <strong>评分:</strong> ⭐ {top_topic.get('score', 0):.1f} |
                <strong>关键词:</strong> {', '.join(top_topic.get('keywords', [])[:3])}
            </div>
            """ if top_topic else '<div style="color: #999; margin-top: 10px;">暂无话题数据</div>'

            card = f"""
            <div style="background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                <h3 style="color: #667eea; margin-bottom: 15px;">{group['name']}</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px;">
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #667eea;">{group['messages']}</div>
                        <div style="font-size: 12px; color: #666;">消息数</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #667eea;">{group['participants']}</div>
                        <div style="font-size: 12px; color: #666;">参与者</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #667eea;">{group['topics']}</div>
                        <div style="font-size: 12px; color: #666;">话题数</div>
                    </div>
                </div>
                {topic_info}
            </div>
            """
            group_cards.append(card)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>群聊分析汇总报告 - {today}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            margin: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #667eea;
            font-size: 36px;
            margin-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .groups {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .groups h2 {{
            color: #667eea;
            margin-bottom: 20px;
        }}
        @media (max-width: 768px) {{
            .stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 群聊分析汇总报告</h1>
            <p style="color: #666; font-size: 16px;">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{data['total_groups']}</div>
                <div class="stat-label">分析群聊数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['total_messages']}</div>
                <div class="stat-label">总消息数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['total_topics']}</div>
                <div class="stat-label">总话题数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['total_messages'] // max(data['total_groups'], 1)}</div>
                <div class="stat-label">平均消息数</div>
            </div>
        </div>

        <div class="groups">
            <h2>📋 群聊详情</h2>
            {''.join(group_cards) if group_cards else '<p style="color: #999; text-align: center; padding: 40px;">暂无数据</p>'}
        </div>
    </div>
</body>
</html>"""
        return html


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='批量群聊分析工具 - 通过Chatlog MCP获取聊天记录并生成分析报告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 分析指定清单文件
  python batch_analyzer.py --list 群聊清单.md

  # 指定输出目录
  python batch_analyzer.py --list 群聊清单.md --output ./reports

  # 覆盖所有群聊的日期
  python batch_analyzer.py --list 群聊清单.md --date 2024-01-15

  # 自定义MCP服务器地址
  python batch_analyzer.py --list 群聊清单.md --mcp-url http://192.168.1.100:5030
        """
    )

    parser.add_argument(
        '--list',
        '-l',
        type=str,
        default='群聊清单.md',
        help='群聊清单文件路径 (默认: 群聊清单.md)'
    )

    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='输出目录路径 (默认: ./chatlog_reports_YYYY-MM-DD)'
    )

    parser.add_argument(
        '--date',
        '-d',
        type=str,
        help='覆盖所有群聊的日期 (today, yesterday, YYYY-MM-DD)'
    )

    parser.add_argument(
        '--mcp-url',
        type=str,
        default='http://127.0.0.1:5030',
        help='Chatlog MCP服务器URL (默认: http://127.0.0.1:5030)'
    )

    parser.add_argument(
        '--format',
        type=str,
        default='html',
        choices=['html', 'json'],
        help='输出格式 (默认: html)'
    )

    parser.add_argument(
        '--template',
        action='store_true',
        help='生成群聊清单模板文件'
    )

    args = parser.parse_args()

    # 生成模板
    if args.template:
        template = MarkdownParser.get_template()
        with open('群聊清单模板.md', 'w', encoding='utf-8') as f:
            f.write(template)
        print("[OK] 已生成群聊清单模板文件: 群聊清单模板.md")
        return

    # 检查清单文件
    if not os.path.exists(args.list):
        print(f"[ERROR] 错误: 群聊清单文件不存在: {args.list}")
        print("  使用 --template 生成模板文件")
        sys.exit(1)

    # 运行分析
    try:
        analyzer = BatchAnalyzer(mcp_url=args.mcp_url)
        output_files = analyzer.run(
            list_file=args.list,
            output_dir=args.output,
            date=args.date,
            format_type=args.format
        )

        # 输出结果
        print("\n📄 生成的文件:")
        for group_name, file_path in output_files.items():
            print(f"  - {group_name}: {file_path}")

    except Exception as e:
        print(f"\n[ERROR] 分析失败: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
