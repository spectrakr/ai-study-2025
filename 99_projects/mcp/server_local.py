import logging
from mcp_server import run_server

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("로컬 서버 실행 시작")
        run_server(transport="stdio")
    except Exception as e:
        logger.error(f"로컬 서버 실행 실패: {str(e)}")
        raise
