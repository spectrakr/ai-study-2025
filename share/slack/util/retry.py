import time
from functools import wraps
from typing import Type, Union, Tuple, Callable, Any
from share.slack.exception.slack_exception import SlackAPIError
from share.slack.util.logger import setup_logger

logger = setup_logger(__name__)


class RetryUtil:
    """재시도 유틸리티 클래스"""

    @staticmethod
    def retry(
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (
            SlackAPIError,
        ),
    ) -> Callable:
        """
        재시도 데코레이터

        Args:
            max_retries: 최대 재시도 횟수
            delay: 초기 대기 시간 (초)
            backoff: 재시도 간 대기 시간 증가 배수
            exceptions: 재시도할 예외 타입들
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                retries = 0
                current_delay = delay

                while True:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        retries += 1
                        if retries > max_retries:
                            logger.error(
                                f"최대 재시도 횟수({max_retries}) 초과: {str(e)}"
                            )
                            raise

                        logger.warning(
                            f"재시도 {retries}/{max_retries} - {current_delay}초 후 재시도: {str(e)}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff

            return wrapper

        return decorator
