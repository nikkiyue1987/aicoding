# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    req = urllib.request.Request(
        'http://127.0.0.1:5030/sse',
        headers={'Accept': 'text/event-stream'}
    )
    with urllib.request.urlopen(req, timeout=2) as response:
        print("MCP server is running")
        print(f"Status: {response.status}")
        print(f"Headers: {dict(response.headers)}")
        # Read first few bytes
        data = response.read(500)
        print(f"Response preview: {data[:200]}")
except Exception as e:
    print(f"Error: {e}")
