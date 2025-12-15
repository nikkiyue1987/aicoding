@echo off
REM 设置环境变量
set ANTHROPIC_AUTH_TOKEN=sk-LkV0ul9Q0lyv7YI35AlcdOHygfgDJ1IfrI5mKC1H6HaVGCkB
REM 替换为您的实际令牌
set ANTHROPIC_BASE_URL=https://api.huiyan-ai.cn

REM 启动 Claude Code
claude --dangerously-skip-permissions

pause