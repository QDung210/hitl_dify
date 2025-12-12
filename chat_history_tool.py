"""
Tool FastMCP để lưu lịch sử chat vào file .md
Sử dụng @mcp.tool decorator
"""
import os
import re
from datetime import datetime
from typing import Optional
from fastmcp import FastMCP

# Khởi tạo FastMCP server
mcp = FastMCP("Chat History Tool")

# Đường dẫn file lưu lịch sử
CHAT_HISTORY_FILE = "chat_history.md"


def ensure_chat_file():
    """Đảm bảo file chat_history.md tồn tại"""
    if not os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write("# Lịch sử Chat\n\n")
            f.write(f"*File được tạo vào: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write("---\n\n")


@mcp.tool()
def get_chat_history(limit: Optional[int] = None) -> str:
    """
    Lấy lịch sử chat từ file .md
    Nếu không có limit, sẽ trả về câu hỏi của người dùng gần thứ 2
    
    Args:
        limit: Số lượng tin nhắn gần nhất cần lấy (None = lấy câu hỏi người dùng gần thứ 2)
    
    Returns:
        str: Nội dung lịch sử chat dưới dạng Markdown hoặc câu hỏi người dùng gần thứ 2
    """
    ensure_chat_file()
    
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        if limit:
            # Lấy N dòng cuối cùng
            lines = content.split('\n')
            content = '\n'.join(lines[-limit:])
            return content
        
        # Parse file để lấy các tin nhắn của người dùng
        # Tìm tất cả các tin nhắn với pattern: ## timestamp\n\n**user**: message
        pattern = r'##\s+([^\n]+)\n\n\*\*([^\*]+)\*\*:\s+([^\n]+)'
        matches = re.findall(pattern, content)
        
        # Lọc các tin nhắn của người dùng (loại bỏ các tin nhắn từ AI/assistant/system)
        user_messages = []
        exclude_users = ['assistant', 'ai', 'system', 'bot', 'Assistant', 'AI', 'System', 'Bot']
        
        for timestamp, user, message in matches:
            user_lower = user.strip().lower()
            if not any(excluded in user_lower for excluded in exclude_users):
                user_messages.append({
                    'timestamp': timestamp.strip(),
                    'user': user.strip(),
                    'message': message.strip()
                })
        
        # Lấy câu hỏi thứ 2 gần nhất (từ cuối lên)
        if len(user_messages) >= 2:
            second_last = user_messages[-2]
            return second_last['message']
        elif len(user_messages) == 1:
            return user_messages[0]['message']
        else:
            return "Không tìm thấy câu hỏi nào của người dùng"
            
    except Exception as e:
        return f"Lỗi khi đọc file: {str(e)}"


@mcp.tool()
def save_chat_message(user: str, message: str, timestamp: Optional[str] = None) -> str:
    """
    Lưu một tin nhắn mới vào lịch sử chat
    
    Args:
        user: Tên người dùng
        message: Nội dung tin nhắn
        timestamp: Thời gian (nếu None sẽ dùng thời gian hiện tại)
    
    Returns:
        str: Thông báo xác nhận
    """
    ensure_chat_file()
    
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(CHAT_HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"## {timestamp}\n\n")
            f.write(f"**{user}**: {message}\n\n")
            f.write("---\n\n")
        
        return f"Đã lưu tin nhắn của {user} vào {CHAT_HISTORY_FILE}"
    except Exception as e:
        return f"Lỗi khi lưu tin nhắn: {str(e)}"


@mcp.tool()
def save_chat_messages(messages: list) -> str:
    """
    Lưu nhiều tin nhắn cùng lúc vào lịch sử chat
    
    Args:
        messages: Danh sách các tin nhắn, mỗi tin nhắn là dict với keys: user, message, timestamp (optional)
    
    Returns:
        str: Thông báo xác nhận
    """
    ensure_chat_file()
    
    try:
        saved_count = 0
        with open(CHAT_HISTORY_FILE, "a", encoding="utf-8") as f:
            for msg in messages:
                user = msg.get("user", "Unknown")
                message = msg.get("message", "")
                timestamp = msg.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                f.write(f"## {timestamp}\n\n")
                f.write(f"**{user}**: {message}\n\n")
                f.write("---\n\n")
                saved_count += 1
        
        return f"Đã lưu {saved_count} tin nhắn vào {CHAT_HISTORY_FILE}"
    except Exception as e:
        return f"Lỗi khi lưu tin nhắn: {str(e)}"


@mcp.tool()
def clear_chat_history() -> str:
    """
    Xóa toàn bộ lịch sử chat
    
    Returns:
        str: Thông báo xác nhận
    """
    try:
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write("# Lịch sử Chat\n\n")
            f.write(f"*File được tạo lại vào: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write("---\n\n")
        
        return f"Đã xóa toàn bộ lịch sử chat trong {CHAT_HISTORY_FILE}"
    except Exception as e:
        return f"Lỗi khi xóa lịch sử: {str(e)}"


if __name__ == "__main__":
    # Chạy server
    mcp.run()

