import os
from typing import Dict

# 用户凭证配置
USERS: Dict[str, str] = {
    "admin": "admin",  # 用户名: 密码
    "user1": "admin888"
}

# 会话状态键
SESSION_STATE_USER = "user"
SESSION_STATE_AUTHENTICATED = "authenticated"

# 页面配置
PAGE_TITLE = "CSV文件分析系统"
PAGE_ICON = "📊"

# 其他配置
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB 