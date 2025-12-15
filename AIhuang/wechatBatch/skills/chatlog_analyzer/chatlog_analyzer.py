#!/usr/bin/env python3
"""
批量群聊分析工具 - 主程序
功能：读取群聊清单、查询记录、智能分析、生成HTML报告
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re
import time
from collections import defaultdict
from typing import List, Dict, Any, Tuple
import logging

# 处理相对导入
try:
    # 尝试相对导入
    from .api_handler import ChatlogAPIHandler
    from .md_parser import MarkdownParser
    from .analyzer import ChatAnalyzer
    from .html_generator import HTMLGenerator
except ImportError:
    # 如果相对导入失败，使用绝对导入（直接执行时）
    from api_handler import ChatlogAPIHandler
    from md_parser import MarkdownParser
    from analyzer import ChatAnalyzer
    from html_generator import HTMLGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatlogBatchAnalyzer:
    """批量群聊分析主类"""

    def __init__(self, md_file: str, api_url: str = "http://127.0.0.1:5030"):
        """初始化分析器

        Args:
            md_file: 群聊清单markdown文件路径
            api_url: chatlog MCP API地址
        """
        self.md_file = Path(md_file)
        self.api_handler = ChatlogAPIHandler(api_url)
        self.md_parser = MarkdownParser()
        self.analyzer = ChatAnalyzer()
        self.html_generator = HTMLGenerator()
        self.results = []

        if not self.md_file.exists():
            raise FileNotFoundError(f"清单文件不存在: {self.md_file}")

    def parse_manifest(self) -> List[Dict[str, Any]]:
        """解析群聊清单markdown文件

        Returns:
            群聊配置列表
        """
        logger.info(f"解析清单文件: {self.md_file}")
        chats = self.md_parser.parse(self.md_file)
        logger.info(f"找到 {len(chats)} 个群聊")
        return chats

    def fetch_chat_data(self, chat_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取单个群聊的聊天数据

        Args:
            chat_name: 群聊名称
            config: 群聊配置（日期、格式等）

        Returns:
            聊天数据
        """
        logger.info(f"获取群聊数据: {chat_name}")

        try:
            # 解析日期
            date_str = config.get('date', 'yesterday')
            target_date = self._parse_date(date_str)

            # 调用API获取数据
            messages = self.api_handler.get_chat_messages(
                chat_name=chat_name,
                date=target_date.strftime('%Y-%m-%d')
            )

            logger.info(f"获取了 {len(messages)} 条消息")

            return {
                'name': chat_name,
                'date': target_date.strftime('%Y-%m-%d'),
                'messages': messages,
                'config': config
            }

        except Exception as e:
            logger.error(f"获取群聊 {chat_name} 数据失败: {e}")
            return {
                'name': chat_name,
                'date': self._parse_date(config.get('date', 'yesterday')).strftime('%Y-%m-%d'),
                'messages': [],
                'error': str(e),
                'config': config
            }

    def analyze_chat(self, chat_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个群聊数据

        Args:
            chat_data: 群聊数据

        Returns:
            分析结果
        """
        logger.info(f"分析群聊: {chat_data['name']}")

        messages = chat_data.get('messages', [])
        if not messages:
            logger.warning(f"群聊 {chat_data['name']} 没有消息")
            return {
                'name': chat_data['name'],
                'date': chat_data['date'],
                'error': '没有聊天数据',
                'topics': []
            }

        # 按30分钟分组消息
        grouped_messages = self.analyzer.group_messages_by_time(
            messages,
            interval_minutes=30
        )

        # 从分组中提取话题
        topics = self.analyzer.extract_topics(grouped_messages, top_n=3)

        return {
            'name': chat_data['name'],
            'date': chat_data['date'],
            'total_messages': len(messages),
            'topics': topics,
            'message_groups': grouped_messages,
            'config': chat_data['config']
        }

    def generate_report(self, analysis_result: Dict[str, Any], output_dir: Path) -> Path:
        """生成HTML报告

        Args:
            analysis_result: 分析结果
            output_dir: 输出目录

        Returns:
            生成的HTML文件路径
        """
        logger.info(f"生成报告: {analysis_result['name']}")

        # 生成HTML
        html_content = self.html_generator.generate(analysis_result)

        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', analysis_result['name'])
        output_file = output_dir / f"{safe_name}_{analysis_result['date']}.html"

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"报告已保存: {output_file}")
        return output_file

    def run(self, output_dir: str = None) -> List[Path]:
        """执行完整的分析流程

        Args:
            output_dir: 输出目录，默认为 reports/YYYY-MM-DD

        Returns:
            生成的HTML文件列表
        """
        try:
            # 解析清单
            chats = self.parse_manifest()

            if not chats:
                logger.warning("清单中没有群聊")
                return []

            # 确定输出目录
            if not output_dir:
                today = datetime.now().strftime('%Y-%m-%d')
                output_dir = Path('reports') / today
            else:
                output_dir = Path(output_dir)

            output_files = []

            # 处理每个群聊
            for chat_name, config in chats:
                # 获取数据
                chat_data = self.fetch_chat_data(chat_name, config)

                # 分析
                analysis = self.analyze_chat(chat_data)

                # 生成报告
                report_file = self.generate_report(analysis, output_dir)
                output_files.append(report_file)

                # 添加延迟，避免过快请求
                time.sleep(1)

            logger.info(f"完成！共生成 {len(output_files)} 个报告")
            return output_files

        except Exception as e:
            logger.error(f"分析失败: {e}", exc_info=True)
            raise

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """解析日期字符串

        Args:
            date_str: 日期字符串（如 'yesterday', '2024-12-09', '3 days ago'）

        Returns:
            datetime对象
        """
        date_str = date_str.lower().strip()
        today = datetime.now().date()

        if date_str == 'yesterday':
            return datetime.combine(today - timedelta(days=1), datetime.min.time())
        elif date_str == 'today':
            return datetime.combine(today, datetime.min.time())
        elif 'day' in date_str and 'ago' in date_str:
            # 解析 "N days ago"
            match = re.search(r'(\d+)\s+days?\s+ago', date_str)
            if match:
                days = int(match.group(1))
                return datetime.combine(today - timedelta(days=days), datetime.min.time())
        else:
            # 尝试解析标准日期格式
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m-%d', '%m/%d']:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    if parsed.year == 1900:  # 如果没指定年份
                        parsed = parsed.replace(year=today.year)
                    return parsed
                except ValueError:
                    continue

        logger.warning(f"无法解析日期: {date_str}，使用今天")
        return datetime.combine(today, datetime.min.time())


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='批量群聊分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  python chatlog_analyzer.py 群聊清单.md
  python chatlog_analyzer.py 群聊清单.md -o reports/custom
  python chatlog_analyzer.py 群聊清单.md --api http://localhost:5030
        '''
    )

    parser.add_argument('manifest', help='群聊清单markdown文件路径')
    parser.add_argument('-o', '--output', help='输出目录', default=None)
    parser.add_argument('--api', help='chatlog MCP API地址', default='http://127.0.0.1:5030')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        analyzer = ChatlogBatchAnalyzer(args.manifest, args.api)
        output_files = analyzer.run(args.output)

        print(f"\n✓ 分析完成！生成了 {len(output_files)} 个报告")
        for f in output_files:
            print(f"  - {f}")

        return 0

    except Exception as e:
        logger.error(f"错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
