import os
from typing import Dict, Any

# 로깅 기본 설정
DEFAULT_LOGGING_CONFIG: Dict[str, Any] = {
    "log_dir": os.getenv("SLACK_LOG_DIR", "logs"),
    "max_bytes": int(os.getenv("SLACK_LOG_MAX_BYTES", "10 * 1024 * 1024")),  # 10MB
    "backup_count": int(os.getenv("SLACK_LOG_BACKUP_COUNT", "5")),
    "level": os.getenv("SLACK_LOG_LEVEL", "INFO"),
}

# 개발 환경 설정
DEV_LOGGING_CONFIG: Dict[str, Any] = {
    **DEFAULT_LOGGING_CONFIG,
    "level": "DEBUG",
}

# 운영 환경 설정
PROD_LOGGING_CONFIG: Dict[str, Any] = {
    **DEFAULT_LOGGING_CONFIG,
    "level": "INFO",
}

# 현재 환경에 따른 설정 반환
def get_logging_config() -> Dict[str, Any]:
    env = os.getenv("SLACK_ENV", "dev")
    if env.lower() == "prod":
        return PROD_LOGGING_CONFIG
    return DEV_LOGGING_CONFIG 