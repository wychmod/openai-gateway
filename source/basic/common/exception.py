class BackoffException(Exception):
    """
    退避重试异常类
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"BackoffException: {self.message}"
