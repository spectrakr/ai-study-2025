import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 글로벌 로거 인스턴스를 저장할 딕셔너리
_logger_instance = None


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    로거를 설정하고 반환합니다. 모든 서비스가 동일한 로그 파일을 공유합니다.

    Args:
        name: 로거 이름
        level: 로깅 레벨 (기본값: logging.INFO)
        log_dir: 로그 파일이 저장될 디렉토리 (기본값: "logs")
        max_bytes: 로그 파일의 최대 크기 (기본값: 10MB)
        backup_count: 보관할 백업 파일의 개수 (기본값: 5)

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    global _logger_instance

    if _logger_instance is not None:
        # 기존 로거가 있다면 이름만 변경하여 반환
        logger = logging.getLogger(name)
        logger.handlers = _logger_instance.handlers
        logger.setLevel(_logger_instance.level)
        return logger

    # 최상위 로거 생성
    logger = logging.getLogger("slack")
    _logger_instance = logger

    if not logger.handlers:  # 핸들러가 없는 경우에만 설정
        logger.setLevel(level)

        # 로그 디렉토리 생성
        os.makedirs(log_dir, exist_ok=True)

        # 로그 파일명 설정 (날짜만 포함)
        current_date = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"slack_{current_date}.log")

        # 파일 핸들러 설정 (로테이션)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(level)

        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # 포맷터 설정 - 서비스 이름을 로그에 포함
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 핸들러 추가
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.info(f"Logger initialized with file handler: {log_file}")

    # 서비스별 로거 생성 (핸들러 공유)
    service_logger = logging.getLogger(name)
    service_logger.handlers = logger.handlers
    service_logger.setLevel(level)

    return service_logger
