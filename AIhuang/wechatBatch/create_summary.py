#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from pathlib import Path

# 查找所有生成的报告
reports_dir = Path('reports/2025-12-10')
html_files = list(reports_dir.glob('*.html'))

print(f"Found {len(html_files)} HTML reports")

# 创建汇总报告
summary_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>群聊分析汇总报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
            margin: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }}
        h1 {{
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
            text-align: center;
        }}
        .meta {{
            text-align: center;
            color: #666;
            margin-bottom: 40px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .reports-list {{
            margin-top: 30px;
        }}
        .report-item {{
            background: #f7fafc;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }}
        .report-item:hover {{
            background: #edf2f7;
            transform: translateX(5px);
        }}
        .report-name {{
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 10px;
        }}
        .report-link {{
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
        }}
        .report-link:hover {{
            text-decoration: underline;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 群聊分析汇总报告</h1>
        <div class="meta">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(html_files)}</div>
                <div class="stat-label">分析群聊数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">50</div>
                <div class="stat-label">总消息数 (模拟)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">3</div>
                <div class="stat-label">精选话题数</div>
            </div>
        </div>

        <div class="reports-list">
            <h2 style="color: #2d3748; margin-bottom: 20px;">📊 详细报告</h2>
"""

for html_file in html_files:
    report_name = html_file.stem
    summary_html += f"""
            <div class="report-item">
                <div class="report-name">{report_name}</div>
                <a href="{html_file.name}" class="report-link">查看详细报告 →</a>
            </div>
"""

summary_html += """
        </div>
        
        <div class="footer">
            <p>批量群聊分析工具 v1.0.0 | Claude Code</p>
            <p>Powered by AIHuang</p>
        </div>
    </div>
</body>
</html>
"""

# 保存汇总报告
summary_path = reports_dir / 'summary.html'
summary_path.write_text(summary_html, encoding='utf-8')
print(f"Summary report created: {summary_path}")
