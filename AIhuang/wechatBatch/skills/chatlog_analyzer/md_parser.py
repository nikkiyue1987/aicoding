"""
Markdown解析模块 - 解析群聊清单文件
"""

import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)


class MarkdownParser:
    """Markdown清单解析器"""

    def parse(self, md_file: Path) -> List[Tuple[str, Dict[str, Any]]]:
        """解析群聊清单markdown文件

        支持的格式：
        ```
        ## 群聊清单

        ### 群聊1
        - 日期：昨天
        - 格式：HTML

        ### 群聊2
        - 日期：2024-12-09
        - 格式：JSON
        ```

        Args:
            md_file: markdown文件路径

        Returns:
            (群聊名称, 配置字典) 的列表
        """
        content = md_file.read_text(encoding='utf-8')
        chats = []

        # 按 # 标题分段（支持 ## 和 ### 格式）
        sections = re.split(r'^#{1,3}\s+', content, flags=re.MULTILINE)

        for section in sections[1:]:  # 跳过第一个空部分
            lines = section.split('\n')

            if not lines:
                continue

            # 第一行是群聊名称
            chat_name = lines[0].strip()

            if not chat_name:
                continue

            # 解析配置
            config = self._parse_config(lines[1:])

            chats.append((chat_name, config))

            logger.debug(f"解析群聊: {chat_name}, 配置: {config}")

        logger.info(f"共解析 {len(chats)} 个群聊")
        return chats

    @staticmethod
    def _parse_config(lines: List[str]) -> Dict[str, Any]:
        """从配置行解析配置字典

        Args:
            lines: 配置行列表

        Returns:
            配置字典
        """
        config = {
            'date': 'yesterday',  # 默认日期
            'format': 'json'      # 默认格式
        }

        for line in lines:
            line = line.strip()

            # 解析 "- 键：值" 格式
            match = re.match(r'-\s*([^：:]+)[：:]\s*(.+)', line)
            if match:
                key = match.group(1).lower().strip()
                value = match.group(2).strip()

                if key in ['date', 'time', '日期', '时间']:
                    config['date'] = value
                elif key in ['format', 'fmt', '格式']:
                    config['format'] = value.lower()
                else:
                    # 存储其他自定义配置
                    config[key] = value

        return config

    @staticmethod
    def create_template(output_file: Path = None) -> str:
        """生成清单文件模板

        Args:
            output_file: 可选，输出文件路径

        Returns:
            模板内容
        """
        template = '''# 群聊分析清单

## 配置说明

在下方列出要分析的群聊，每个群聊一个小节（###）。

**支持的日期格式：**
- `yesterday` - 昨天
- `today` - 今天
- `N days ago` - N天前（如 `3 days ago`）
- `YYYY-MM-DD` - 具体日期（如 `2024-12-09`）

**支持的格式：**
- `json` - JSON格式
- `html` - HTML格式
- `text` - 纯文本格式

---

## 群聊列表

### 群聊名称1
- 日期：昨天
- 格式：JSON

### 群聊名称2
- 日期：3 days ago
- 格式：HTML

### 群聊名称3
- 日期：2024-12-09
- 格式：JSON
'''

        if output_file:
            output_file = Path(output_file)
            output_file.write_text(template, encoding='utf-8')
            logger.info(f"模板已保存: {output_file}")

        return template
