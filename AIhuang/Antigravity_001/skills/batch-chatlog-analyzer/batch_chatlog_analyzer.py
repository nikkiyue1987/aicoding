#!/usr/bin/env python3
"""
Batch Chatlog Analyzer
======================
Production-grade batch analysis tool for group chat logs.

Features:
- Reads markdown checklist for batch processing
- Queries chat data via MCP (Model Context Protocol)
- Intelligent topic extraction and ranking
- Generates modern, responsive HTML reports
- Zero-interruption execution (Log & Continue strategy)

Author: Claude Skills Architect
Version: 1.0.0
License: MIT
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import logging

# Fix Windows console encoding for Chinese characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class ChecklistParser:
    """Parse markdown checklist and normalize dates."""
    
    TEMPLATE = """# 群聊清单

请按以下格式列出要分析的群聊:

- 群聊名称: 技术讨论组
  日期: 昨天
  格式: HTML

- 群聊名称: 产品团队
  日期: 2025-12-11
  格式: HTML

- 群聊名称: 设计组
  日期: 今天
  格式: HTML

## 说明
- 群聊名称: 必填,需与MCP中的群聊名称完全一致
- 日期: 支持"昨天"、"今天"、"前天"或"YYYY-MM-DD"格式,默认为"昨天"
- 格式: 目前仅支持HTML,可省略
"""
    
    def __init__(self, filepath: str = "群聊清单.md"):
        self.filepath = Path(filepath)
    
    def exists(self) -> bool:
        """Check if checklist file exists."""
        return self.filepath.exists()
    
    def create_template(self) -> None:
        """Create template checklist file."""
        self.filepath.write_text(self.TEMPLATE, encoding='utf-8')
        logger.info(f"✅ Created template file: {self.filepath}")
        logger.info("📝 Please fill in the checklist and re-run the command.")
    
    def parse(self) -> List[Dict[str, str]]:
        """Parse checklist and return list of chat configs."""
        content = self.filepath.read_text(encoding='utf-8')
        chats = []
        
        # Parse each chat entry
        pattern = r'-\s*群聊名称:\s*(.+?)(?:\n\s+日期:\s*(.+?))?(?:\n\s+格式:\s*(.+?))?(?=\n-|\n#|\Z)'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            name = match.group(1).strip()
            date_str = match.group(2).strip() if match.group(2) else "昨天"
            format_type = match.group(3).strip() if match.group(3) else "HTML"
            
            date = self._normalize_date(date_str)
            
            chats.append({
                'name': name,
                'date': date,
                'date_str': date_str,
                'format': format_type
            })
        
        logger.info(f"📋 Parsed {len(chats)} chat(s) from checklist")
        return chats
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD or date range format.
        
        Returns:
            For single dates: 'YYYY-MM-DD'
            For ranges (like 本月): 'YYYY-MM-DD,YYYY-MM-DD'
        """
        today = datetime.now()
        
        # Handle relative dates
        if date_str == "今天":
            return today.strftime("%Y-%m-%d")
        elif date_str == "昨天":
            return (today - timedelta(days=1)).strftime("%Y-%m-%d")
        elif date_str == "前天":
            return (today - timedelta(days=2)).strftime("%Y-%m-%d")
        elif date_str == "本月" or date_str == "这个月":
            # Return date range: first day of month to today
            first_day = today.replace(day=1).strftime("%Y-%m-%d")
            today_str = today.strftime("%Y-%m-%d")
            return f"{first_day},{today_str}"
        
        # Handle absolute dates (assume already in YYYY-MM-DD format)
        # Basic validation
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            logger.warning(f"⚠️ Invalid date format '{date_str}', using yesterday")
            return (today - timedelta(days=1)).strftime("%Y-%m-%d")






class MCPClient:
    """Wrapper for MCP (Model Context Protocol) chat queries."""
    
    def __init__(self):
        """Initialize MCP client."""
        self.base_url = 'http://127.0.0.1:5030'
        self.mcp_available = False
        self.chatroom_cache = {}  # Cache for chatroom name -> ID mapping
        
        # Load custom chatroom mappings first
        self._load_custom_mappings()
        
        try:
            self.mcp_available = self._check_mcp_availability()
            if self.mcp_available:
                logger.info("✅ MCP server connection established")
                # Load chatroom list for name resolution
                self._load_chatroom_cache()
        except Exception as e:
            logger.warning(f"⚠️ MCP client initialization failed: {e}")
            self.mcp_available = False
    
    def _load_custom_mappings(self):
        """Load custom chatroom name mappings from chatroom_mapping.py"""
        try:
            # Try to import from project root
            import sys
            from pathlib import Path
            
            # Add project root to path
            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            # Import the mapping
            from chatroom_mapping import chatroom_mapping
            
            # Add to cache
            for display_name, chat_id in chatroom_mapping.items():
                self.chatroom_cache[display_name] = chat_id
            
            logger.info(f"📝 Loaded {len(chatroom_mapping)} custom chatroom mappings")
        except ImportError:
            logger.info("ℹ️ No custom chatroom mappings found (chatroom_mapping.py)")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load custom mappings: {e}")

    
    def _check_mcp_availability(self) -> bool:
        """Check if MCP server is available."""
        try:
            import urllib.request
            import urllib.error
            
            req = urllib.request.Request(
                f'{self.base_url}/sse',
                headers={'Accept': 'text/event-stream'}
            )
            
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except (urllib.error.URLError, Exception):
            return False
    
    def _load_chatroom_cache(self):
        """Load chatroom list and build name -> ID mapping cache."""
        try:
            import requests
            
            response = requests.get(
                f'{self.base_url}/api/v1/chatroom',
                params={'format': 'json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                chatrooms = data.get('items', [])
                
                # Build cache: both nickName and name can be used as keys
                for room in chatrooms:
                    room_id = room.get('name', '')
                    nick_name = room.get('nickName', '')
                    remark = room.get('remark', '')
                    
                    if room_id:
                        # Map ID to itself
                        self.chatroom_cache[room_id] = room_id
                        
                        # Map nickName to ID if available
                        if nick_name:
                            self.chatroom_cache[nick_name] = room_id
                        
                        # Map remark to ID if available
                        if remark:
                            self.chatroom_cache[remark] = room_id
                
                logger.info(f"📋 Loaded {len(chatrooms)} chatrooms into cache")
            else:
                logger.warning(f"⚠️ Failed to load chatroom list: HTTP {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to load chatroom cache: {e}")
    
    def _resolve_chat_name(self, chat_name: str) -> Optional[str]:
        """Resolve display name to chatroom ID."""
        # First, check exact match in cache
        if chat_name in self.chatroom_cache:
            resolved_id = self.chatroom_cache[chat_name]
            if resolved_id != chat_name:
                logger.info(f"📝 Resolved '{chat_name}' -> '{resolved_id}'")
            return resolved_id
        
        # If not found, try case-insensitive match
        for name, room_id in self.chatroom_cache.items():
            if name.lower() == chat_name.lower():
                logger.info(f"📝 Resolved '{chat_name}' -> '{room_id}' (case-insensitive)")
                return room_id
        
        # If still not found, try partial match
        for name, room_id in self.chatroom_cache.items():
            if chat_name in name or name in chat_name:
                logger.info(f"📝 Resolved '{chat_name}' -> '{room_id}' (partial match with '{name}')")
                return room_id
        
        # Not found - return original name (might be an ID already)
        logger.warning(f"⚠️ Could not resolve '{chat_name}' to chatroom ID")
        logger.warning(f"   Using original name as-is")
        return chat_name
    
    def query_messages(self, chat_name: str, date: str) -> Optional[List[Dict]]:
        """
        Query messages for a specific chat and date using Chatlog API.
        Automatically resolves display names to chatroom IDs.
        
        Args:
            chat_name: Name or display name of the chat
            date: Date in YYYY-MM-DD format
        
        Returns:
            List of message dicts or None if no data/error
        """
        try:
            logger.info(f"🔍 Querying Chatlog for '{chat_name}' on {date}...")
            
            # Resolve display name to chatroom ID
            chat_id = self._resolve_chat_name(chat_name)
            
            if not self.mcp_available:
                logger.error("❌ Chatlog server not available at http://127.0.0.1:5030")
                logger.error("   Please ensure:")
                logger.error("   1. Chatlog server is running")
                logger.error("   2. Server is listening on port 5030")
                logger.error("   3. Firewall allows connections")
                return None
            
            # Try to query via HTTP requests
            try:
                import requests
            except ImportError:
                logger.error("❌ 'requests' library not installed")
                logger.error("   Install with: pip install requests")
                return None
            
            # Use Chatlog API: GET /api/v1/chatlog
            # Parameters: time (date range), talker (chat object)
            try:
                # Chatlog API expects:
                # - time: 'YYYY-MM-DD' or 'YYYY-MM-DD~YYYY-MM-DD' (note: ~ not ,)
                # - talker: chat object identifier
                
                # Convert comma to tilde for Chatlog API
                if ',' in date:
                    time_param = date.replace(',', '~')  # Replace , with ~
                else:
                    time_param = f"{date}~{date}"  # Single day range with ~
                
                response = requests.get(
                    f'{self.base_url}/api/v1/chatlog',
                    params={
                        'time': time_param,  # Use 'time' not 'time_range'
                        'talker': chat_id,   # Use 'talker' not 'chat_object'
                        'format': 'json'  # Request JSON format
                    },
                    headers={'Accept': 'application/json'},
                    timeout=15
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Chatlog API returns data in specific format
                        # Extract messages from response
                        if isinstance(data, list):
                            messages = data
                        elif isinstance(data, dict):
                            # Try common field names
                            messages = (data.get('data') or 
                                      data.get('messages') or 
                                      data.get('records') or 
                                      data.get('chatlog') or
                                      [])
                        else:
                            messages = []
                        
                        if messages and len(messages) > 0:
                            logger.info(f"✅ Retrieved {len(messages)} messages from Chatlog")
                            return self._normalize_messages(messages)
                        else:
                            logger.warning(f"⚠️ No messages found for '{chat_name}' on {date}")
                            return None
                            
                    except json.JSONDecodeError:
                        logger.error(f"❌ Failed to parse JSON response")
                        return None
                else:
                    logger.warning(f"⚠️ Chatlog API returned status {response.status_code}")
                    if response.status_code == 404:
                        logger.warning(f"   Chat '{chat_name}' may not exist or has no messages on {date}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.error(f"❌ Request timeout - Chatlog server took too long to respond")
                return None
            except requests.exceptions.ConnectionError:
                logger.error(f"❌ Connection error - Could not connect to Chatlog server")
                return None
            except Exception as e:
                logger.error(f"❌ Chatlog API query failed: {e}")
                return None
            
        except Exception as e:
            logger.error(f"❌ MCP query failed for '{chat_name}': {e}")
            return None
    
    def _normalize_messages(self, messages: List) -> List[Dict]:
        """
        Normalize message format to ensure consistency.
        
        Expected format:
        {
            'timestamp': '2025-12-12T10:30:00',
            'sender': 'User Name',
            'content': 'Message content'
        }
        """
        normalized = []
        for msg in messages:
            if isinstance(msg, dict):
                # Try to extract standard fields
                normalized_msg = {
                    'timestamp': msg.get('timestamp') or msg.get('time') or msg.get('created_at') or '',
                    'sender': msg.get('sender') or msg.get('from') or msg.get('user') or msg.get('author') or 'Unknown',
                    'content': msg.get('content') or msg.get('text') or msg.get('message') or msg.get('body') or ''
                }
                normalized.append(normalized_msg)
        
        return normalized if normalized else messages




class TopicAnalyzer:
    """Analyze messages and extract top topics."""
    
    TIME_WINDOW_MINUTES = 30
    
    def __init__(self, messages: List[Dict]):
        self.messages = messages
    
    def analyze(self) -> List[Dict]:
        """
        Analyze messages and return top topics.
        
        Number of topics is dynamic based on message count:
        - Approximately 1 topic per 50 messages
        - Minimum 5 topics, maximum 20 topics
        
        Returns:
            List of topic dicts with title, summary, keywords, etc.
        """
        # Group messages by session windows (silence > 30 mins = new topic)
        sessions = self._group_by_session_windows()
        
        # Extract topics from each session
        topics = []
        for session_messages in sessions:
            topic = self._extract_topic(session_messages)
            if topic:  # Only add valid topics
                topics.append(topic)
        
        # Rank topics by score
        ranked_topics = sorted(topics, key=lambda t: t['score'], reverse=True)
        
        # Calculate dynamic topic count based on message volume
        # Approximately 1 topic per 50 messages, min 5, max 20
        total_messages = len(self.messages)
        target_topics = max(5, min(20, total_messages // 50))
        
        # Return top N topics
        top_topics = ranked_topics[:target_topics]
        
        logger.info(f"📊 Extracted {len(topics)} topics (sessions), selected top {len(top_topics)}")
        return top_topics
    
    def _group_by_session_windows(self) -> List[List[Dict]]:
        """Group messages into sessions based on time gaps.
        
        Start a new group if gap between messages > TIME_WINDOW_MINUTES.
        """
        if not self.messages:
            return []
            
        sessions = []
        current_session = []
        last_time = None
        
        # Ensure messages are sorted by time (they usually are, but just to be safe)
        # Note: timestamps are strings, so we need to parse them for comparison
        # But for stability, we assume they are roughly ordered or we rely on their order in list
        
        for msg in self.messages:
            try:
                # Handle various timestamp formats if needed, but assuming ISO-like
                current_time = datetime.fromisoformat(msg['timestamp'])
            except ValueError:
                # Try simple string parsing if isoformat fails (for safety)
                continue
                
            if last_time is None:
                current_session.append(msg)
            else:
                gap = current_time - last_time
                if gap > timedelta(minutes=self.TIME_WINDOW_MINUTES):
                    # Gap too large, start new session
                    sessions.append(current_session)
                    current_session = [msg]
                else:
                    # Within window, add to current session
                    current_session.append(msg)
            
            last_time = current_time
        
        # Add the last session
        if current_session:
            sessions.append(current_session)
            
        return sessions
    
    def _extract_topic(self, messages: List[Dict]) -> Optional[Dict]:
        """Extract topic information from a session of messages."""
        if not messages:
            return None
            
        # Calculate metrics
        msg_count = len(messages)
        total_length = sum(len(msg.get('content', '')) for msg in messages)
        participants = set(msg.get('sender', 'Unknown') for msg in messages)
        participant_count = len(participants)
        
        # Calculate score (weighted formula)
        # Bonus for topics with more participants (discussion) vs monologue
        diversity_bonus = 1.5 if participant_count > 2 else 1.0
        score = ((msg_count * 0.4) + (total_length * 0.1) + (participant_count * 5.0)) * diversity_bonus
        
        # Generate title
        title = self._generate_title(messages)
        
        # Generate summary
        summary = self._generate_summary(messages)
        
        # Extract keywords
        keywords = self._extract_keywords(messages)
        
        # Get start time of the topic
        start_time_str = messages[0].get('timestamp', '')
        try:
            start_time = datetime.fromisoformat(start_time_str).strftime("%H:%M")
        except:
            start_time = "Unknown"
            
        return {
            'title': title,
            'summary': summary,
            'keywords': keywords,
            'timestamp': start_time,
            'message_count': msg_count,
            'participant_count': participant_count,
            'score': score
        }
    
    def _generate_title(self, messages: List[Dict]) -> str:
        """Generate meaningful topic title from messages.
        
        Strategy: Find the most representative message (longest, with meaningful content)
        and extract a concise title from it.
        """
        # Find messages with substantial content
        substantial_msgs = []
        for msg in messages:
            content = msg.get('content', '').strip()
            # Filter out short messages, emoji-only, and system messages
            if len(content) > 15 and not self._is_noise(content):
                substantial_msgs.append(content)
        
        if not substantial_msgs:
            # Fallback: use any message with content
            for msg in messages:
                content = msg.get('content', '').strip()
                if len(content) > 5:
                    return self._extract_title_from_content(content)
            return "群聊讨论"
        
        # Find the most representative message (balance of length and position)
        # Earlier messages often set the topic, longer messages contain more info
        best_msg = substantial_msgs[0]
        for i, msg in enumerate(substantial_msgs[:5]):  # Look at first 5 substantial messages
            # Prefer earlier messages with good length
            if len(msg) > len(best_msg) * 0.7 and i < 3:
                best_msg = msg
                break
        
        return self._extract_title_from_content(best_msg)
    
    def _extract_title_from_content(self, content: str) -> str:
        """Extract a concise title from message content."""
        # Remove common noise patterns
        content = re.sub(r'\[.*?\]', '', content)  # Remove [emoji]
        content = re.sub(r'@\w+', '', content)  # Remove @mentions
        content = content.strip()
        
        # Try to find a sentence or phrase
        # Split by common Chinese/English punctuation
        sentences = re.split(r'[。！？\n，；：]', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if 8 <= len(sentence) <= 40:
                return sentence
        
        # Fallback: truncate the content
        if len(content) > 40:
            # Try to cut at a word boundary
            truncated = content[:40]
            # Find last space or punctuation
            for i in range(len(truncated) - 1, max(20, len(truncated) - 10), -1):
                if truncated[i] in ' ，。！？、':
                    return truncated[:i].strip() + "..."
            return truncated + "..."
        
        return content if content else "群聊讨论"
    
    def _is_noise(self, content: str) -> bool:
        """Check if content is noise (emoji-only, system message, etc.)."""
        noise_patterns = [
            r'^\[.*\]$',  # Only emoji like [微笑]
            r'^@\w+\s*$',  # Only @mention
            r'^[？?!！]+$',  # Only punctuation
            r'^\d+$',  # Only numbers
            r'^(嗯|哦|啊|呵呵|哈哈|好的|ok|OK|收到|谢谢|感谢)+$',  # Simple responses
        ]
        for pattern in noise_patterns:
            if re.match(pattern, content.strip()):
                return True
        return False
    
    def _generate_summary(self, messages: List[Dict]) -> str:
        """Generate intelligent topic summary.
        
        Strategy: Select 3-5 most representative messages that capture the discussion.
        """
        # Filter out noise and collect substantial messages
        substantial = []
        for msg in messages:
            content = msg.get('content', '').strip()
            if len(content) > 10 and not self._is_noise(content):
                substantial.append({
                    'content': content,
                    'sender': msg.get('sender', 'Unknown'),
                    'length': len(content)
                })
        
        if not substantial:
            return "暂无详细摘要"
        
        # Select diverse messages for summary
        # Strategy: pick messages from different parts of the conversation
        selected = []
        n = len(substantial)
        
        if n <= 3:
            selected = substantial
        else:
            # Pick from beginning, middle, and end
            indices = [0, n // 2, n - 1]
            # Also add longest messages if they're different
            sorted_by_length = sorted(range(n), key=lambda i: substantial[i]['length'], reverse=True)
            for idx in sorted_by_length[:2]:
                if idx not in indices:
                    indices.append(idx)
            
            indices = sorted(set(indices))[:4]
            selected = [substantial[i] for i in indices]
        
        # Build summary
        summary_parts = []
        for item in selected:
            content = item['content']
            # Clean and truncate
            content = re.sub(r'\[.*?\]', '', content).strip()
            if len(content) > 60:
                content = content[:60] + "..."
            if content:
                summary_parts.append(content)
        
        return " | ".join(summary_parts) if summary_parts else "暂无详细摘要"
    
    def _extract_keywords(self, messages: List[Dict]) -> List[str]:
        """Extract meaningful keywords from messages.
        
        Strategy: Use Chinese text patterns and filter common words.
        """
        # Common Chinese stop words to filter
        stop_words = {
            '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '他', '她', '它', '们', '什么', '怎么', '可以', '这个', '那个',
            '吗', '呢', '啊', '吧', '哦', '嗯', '哈', '呵', '嘻', '哼', '唉', '喂',
            '如果', '因为', '所以', '但是', '而且', '或者', '还是', '虽然', '不过',
            '这样', '那样', '这么', '那么', '什么样', '怎么样',
        }
        
        # Collect all text
        all_text = ' '.join(msg.get('content', '') for msg in messages)
        
        # Extract potential keywords using patterns
        keywords_candidates = defaultdict(int)
        
        # Pattern 1: Chinese phrases (2-6 characters)
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,6}', all_text)
        for word in chinese_words:
            if word not in stop_words and len(word) >= 2:
                keywords_candidates[word] += 1
        
        # Pattern 2: English words (3+ letters)
        english_words = re.findall(r'[a-zA-Z]{3,}', all_text)
        for word in english_words:
            word_lower = word.lower()
            if word_lower not in {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all'}:
                keywords_candidates[word] += 1
        
        # Pattern 3: Numbers with context (like "2024年" or "100万")
        num_patterns = re.findall(r'\d+[年月日万亿%]+', all_text)
        for pattern in num_patterns:
            keywords_candidates[pattern] += 1
        
        # Score keywords by frequency and length
        scored = []
        for word, freq in keywords_candidates.items():
            # Higher score for: more frequent, moderate length, multiple occurrences
            length_score = min(len(word) / 4, 1.5)  # Prefer 2-6 chars
            freq_score = min(freq / 3, 2.0)  # Value frequency
            score = length_score * freq_score
            if freq >= 2:  # Only include words that appear at least twice
                scored.append((word, score, freq))
        
        # Sort by score and get top keywords
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Get top 5 unique keywords
        keywords = []
        seen = set()
        for word, score, freq in scored:
            # Skip if too similar to existing keywords
            is_duplicate = False
            for existing in seen:
                if word in existing or existing in word:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                keywords.append(word)
                seen.add(word)
            
            if len(keywords) >= 5:
                break
        
        return keywords if keywords else ["讨论", "交流", "分享"]


class HTMLGenerator:
    """Generate modern, responsive HTML reports matching specific design."""
    
    TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chat_name} - 群聊总结</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
            padding-bottom: 40px;
        }}
        
        /* Header Section */
        .header {{
            background: linear-gradient(135deg, #6a4c9c 0%, #8e62ac 100%);
            color: white;
            text-align: center;
            padding: 60px 20px;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 0 20px;
            margin-top: -30px; /* Overlap header */
        }}
        
        /* Stats Section */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }}
        
        .stat-number {{
            display: block;
            font-size: 36px;
            font-weight: 700;
            color: #4a90e2;
            margin-bottom: 8px;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #666;
        }}
        
        /* Section Titles */
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            color: #333;
        }}
        
        .section-title.hot {{
            color: #333;
        }}
        
        /* Featured Topic Card */
        .featured-card {{
            background: linear-gradient(135deg, #7251a3 0%, #8a65b8 100%);
            border-radius: 12px;
            padding: 30px;
            color: white;
            margin-bottom: 40px;
            box-shadow: 0 10px 20px rgba(106, 76, 156, 0.2);
        }}
        
        .featured-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }}
        
        .featured-title {{
            font-size: 20px;
            font-weight: 600;
        }}
        
        .featured-content ul {{
            list-style: none;
            padding-left: 20px;
        }}
        
        .featured-content li {{
            margin-bottom: 12px;
            position: relative;
            font-size: 15px;
            opacity: 0.95;
        }}
        
        .featured-content li::before {{
            content: "•";
            position: absolute;
            left: -20px;
            color: rgba(255, 255, 255, 0.6);
        }}
        
        /* Discussion List */
        .discussion-list {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        
        .discussion-card {{
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
            border-left: 4px solid #4a90e2;
            position: relative;
        }}
        
        .discussion-header {{
            margin-bottom: 15px;
        }}
        
        .discussion-title {{
            font-size: 18px;
            font-weight: 600;
            color: #4a90e2;
            margin-bottom: 6px;
        }}
        
        .discussion-meta {{
            font-size: 12px;
            color: #999;
        }}
        
        .discussion-content ul {{
            list-style: disc;
            padding-left: 20px;
            color: #555;
        }}
        
        .discussion-content li {{
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 60px;
            color: #999;
            font-size: 12px;
        }}

        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <div class="header">
        <h1>{chat_name}</h1>
        <p>{date_range} 群聊总结</p>
    </div>

    <div class="container">
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{total_messages}</span>
                <span class="stat-label">总消息数</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{total_participants}</span>
                <span class="stat-label">活跃成员</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{time_span}</span>
                <span class="stat-label">活跃时段</span>
            </div>
        </div>

        <!-- Hot Topic (First Topic) -->
        {hot_topic_html}

        <!-- Technical Discussions (Rest Topics) -->
        {discussions_html}

        <div class="footer">
            <p>生成时间: {gen_time} · Powered by Batch Chatlog Analyzer</p>
        </div>
    </div>

</body>
</html>
"""

    def generate(self, chat_name: str, date: str, topics: List[Dict], 
                 message_count: int = 0, participant_count: int = 0) -> str:
        """Generate HTML report."""
        if not topics:
            return ""
            
        # Stats
        total_msgs = sum(t['message_count'] for t in topics)
        # Use provided total if available, otherwise sum (which is lower bound)
        if message_count > 0:
            total_msgs = message_count
            
        total_participants = max(t['participant_count'] for t in topics) if topics else 0
        if participant_count > 0:
            total_participants = participant_count
            
        # Time span
        times = [t['timestamp'] for t in topics if t['timestamp'] != 'Unknown']
        if times:
            try:
                time_objs = sorted([datetime.strptime(t, "%H:%M") for t in times])
                time_span = f"{time_objs[0].strftime('%H:%M')}-{time_objs[-1].strftime('%H:%M')}"
            except:
                 time_span = f"{min(times)} - {max(times)}"
        else:
            time_span = "全天"
        
        # Split topics
        hot_topic = topics[0]
        other_topics = topics[1:]
        
        # Generate Hot Topic HTML
        hot_topic_html = ""
        if hot_topic:
             # Convert summary to list items
            summary_items = hot_topic['summary'].split(' | ')
            list_html = "\n".join([f"<li>{item}</li>" for item in summary_items])
            
            hot_topic_html = f"""
            <div class="section-title hot">
                <span>📌</span> 今日热点话题
            </div>
            <div class="featured-card">
                <div class="featured-header">
                    <span style="font-size: 24px;">🔥</span>
                    <div class="featured-title">{hot_topic['title']}</div>
                </div>
                <div class="featured-content">
                    <ul>
                        {list_html}
                    </ul>
                </div>
                <div style="margin-top: 20px; font-size: 13px; opacity: 0.8;">
                    话题热度: {hot_topic['message_count']}条消息 · {hot_topic['participant_count']}人参与
                </div>
            </div>
            """

        # Generate Discussions HTML
        discussions_html = ""
        if other_topics:
            cards_html = []
            for i, topic in enumerate(other_topics, 1):
                # Convert summary to list items
                summary_items = topic['summary'].split(' | ')
                list_html = "\n".join([f"<li>{item}</li>" for item in summary_items])
                
                card = f"""
                <div class="discussion-card">
                    <div class="discussion-header">
                        <div class="discussion-title">{i}. {topic['title']}</div>
                        <div class="discussion-meta">{topic['timestamp']} · {topic['participant_count']}人参与 · {topic['message_count']}条消息</div>
                    </div>
                    <div class="discussion-content">
                        <ul>
                            {list_html}
                        </ul>
                    </div>
                </div>
                """
                cards_html.append(card)
            
            discussions_html = f"""
            <div class="section-title">
                <span>💡</span> 讨论精华
            </div>
            <div class="discussion-list">
                {"".join(cards_html)}
            </div>
            """

        return self.TEMPLATE.format(
            chat_name=chat_name,
            date_range=date,
            total_messages=total_msgs,
            total_participants=total_participants,
            time_span=time_span,
            hot_topic_html=hot_topic_html,
            discussions_html=discussions_html,
            gen_time=datetime.now().strftime("%H:%M:%S")
        )

    def save(self, html: str, output_path: Path) -> None:
        """Save HTML to file."""
        output_path.write_text(html, encoding='utf-8')
        logger.info(f"✅ Generated report: {output_path.name}")


class BatchChatlogAnalyzer:
    """Main orchestrator for batch chatlog analysis."""
    
    def __init__(self, checklist_path: str = "群聊清单.md"):
        self.checklist_path = checklist_path
        self.parser = ChecklistParser(checklist_path)
        self.mcp_client = MCPClient()
        self.html_generator = HTMLGenerator()
    
    def run(self) -> None:
        """Execute the complete batch analysis workflow."""
        logger.info("🚀 Starting Batch Chatlog Analyzer...")
        
        # Phase 1: Check and parse checklist
        if not self.parser.exists():
            logger.warning(f"⚠️ Checklist file not found: {self.checklist_path}")
            self.parser.create_template()
            return
        
        chats = self.parser.parse()
        if not chats:
            logger.error("❌ No chats found in checklist")
            return
        
        # Create output directory
        date_suffix = datetime.now().strftime("%Y%m%d")
        output_dir = Path(f"chatlog_reports_{date_suffix}")
        output_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Output directory: {output_dir}")
        
        # Phase 2-4: Process each chat
        success_count = 0
        skip_count = 0
        
        for chat in chats:
            try:
                result = self._process_chat(chat, output_dir)
                if result:
                    success_count += 1
                else:
                    skip_count += 1
            except Exception as e:
                logger.error(f"❌ Error processing '{chat['name']}': {e}")
                skip_count += 1
                continue  # Log & Continue strategy
        
        # Phase 5: Summary
        logger.info("=" * 60)
        logger.info(f"✅ Generated {success_count} report(s) in {output_dir}/")
        if skip_count > 0:
            logger.info(f"⚠️ Skipped {skip_count} chat(s) (see logs above)")
        logger.info("🎉 Batch analysis complete!")
    
    def _process_chat(self, chat: Dict, output_dir: Path) -> bool:
        """
        Process a single chat.
        
        Returns:
            True if successful, False if skipped
        """
        chat_name = chat['name']
        date = chat['date']
        
        logger.info(f"\\n📊 Processing: {chat_name} ({date})")
        
        # Query messages
        messages = self.mcp_client.query_messages(chat_name, date)
        if not messages:
            logger.warning(f"⚠️ No messages found for '{chat_name}' on {date}, skipping...")
            return False
        
        # Analyze topics
        analyzer = TopicAnalyzer(messages)
        topics = analyzer.analyze()
        
        if not topics:
            logger.warning(f"⚠️ No topics extracted for '{chat_name}', skipping...")
            return False
        
        # Calculate stats
        message_count = len(messages)
        participants = set(msg.get('sender', 'Unknown') for msg in messages)
        participant_count = len(participants)
        
        # Generate HTML
        html = self.html_generator.generate(
            chat_name=chat_name,
            date=date,
            topics=topics,
            message_count=message_count,
            participant_count=participant_count
        )
        
        # Save report
        output_filename = f"{chat_name}_{date.replace('-', '')}.html"
        output_path = output_dir / output_filename
        self.html_generator.save(html, output_path)
        
        return True


def main():
    """Main entry point."""
    # Parse command line arguments
    checklist_path = sys.argv[1] if len(sys.argv) > 1 else "群聊清单.md"
    
    # Run analyzer
    analyzer = BatchChatlogAnalyzer(checklist_path)
    analyzer.run()


if __name__ == "__main__":
    main()
