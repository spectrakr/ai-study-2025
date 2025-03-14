class SlackException(Exception):
    """Slack 관련 기본 예외 클래스"""
    pass

class SlackAPIError(SlackException):
    """Slack API 호출 중 발생하는 에러"""
    def __init__(self, error_message: str, status_code: int = None):
        self.error_message = error_message
        self.status_code = status_code
        super().__init__(f"Slack API Error: {error_message} (Status: {status_code})")

class SlackAuthenticationError(SlackException):
    """Slack 인증 관련 에러"""
    def __init__(self, error_message: str):
        super().__init__(f"Slack Authentication Error: {error_message}")

class SlackChannelError(SlackException):
    """Slack 채널 관련 에러"""
    def __init__(self, error_message: str):
        super().__init__(f"Slack Channel Error: {error_message}")

class SlackMessageError(SlackException):
    """Slack 메시지 관련 에러"""
    def __init__(self, error_message: str):
        super().__init__(f"Slack Message Error: {error_message}")

class SlackThreadError(SlackException):
    """Slack 스레드 관련 에러"""
    def __init__(self, error_message: str):
        super().__init__(f"Slack Thread Error: {error_message}") 