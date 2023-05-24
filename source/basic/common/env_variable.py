import os


def get_integer_variable(name: str, default: int = None) -> int:
    """
    读取int类型的环境变量
    """
    var = int(os.getenv(name.upper(), 0))
    return var if var else default


def get_string_variable(name: str, default: str = None) -> str:
    """
    读取string类型的环境变量
    """
    var = os.getenv(name.upper())
    return var if var else default
