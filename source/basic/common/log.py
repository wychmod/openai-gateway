import logging
import os

from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_project_path():
    cur_path = Path(__file__).resolve()

    return cur_path

project_path = get_project_path()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", logging.INFO),  # 设置日志级别，例如：DEBUG, INFO, WARNING, ERROR, CRITICAL
    # format="%(asctime)s [%(levelname)s] %(name)s %(message)s",  # 设置日志格式
    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
    handlers=[
        # logging.FileHandler(f"{project_path}/log/app.log"),  # 将日志保存到文件
        logging.StreamHandler(),  # 同时将日志输出到控制台
        # RotatingFileHandler(filename=f"{project_path}/log/app.log", maxBytes=1024 * 1024 * 5, backupCount=5)
    ]
)

logger = logging.getLogger(__name__)