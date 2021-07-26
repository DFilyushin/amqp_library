class MQHandlerException(Exception):
    """Queue base error exception"""

    def __init__(self, message: str) -> None:
        self.message = message

    def __repr__(self) -> str:
        return f'Queue error message: "{self.message}".'
