import os

import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

today_now = datetime.now().strftime("%Y%m%d%H%M%S")

LOG_FORMAT = "%(asctime)s | %(levelname)8s | %(message)s"
LOG_FILE_PATH = f"logs/session_{today_now}/app.log"
LOG_ROOT = "/tmp" if os.environ.get('KUBERNETES_SERVICE_HOST') else "dev"
LOG_FILE_PATH = os.path.join(LOG_ROOT, LOG_FILE_PATH)
Path(LOG_FILE_PATH).parent.mkdir(exist_ok=True, parents=True)


def rollover_session_logs(backup_count=5):
    logs_dir = Path(LOG_FILE_PATH).parent.parent
    if not logs_dir.exists():
        return

    list_session_dirs = sorted(logs_dir.glob("session_*"))
    if len(list_session_dirs) <= backup_count:
        return

    for session_dir in list_session_dirs[:-backup_count]:
        for file in session_dir.glob("*"):
            file.unlink()
        session_dir.rmdir()


def set_logger(log_level=None):
    _logger = logging.Logger(name="web")
    _logger.setLevel(level=log_level)

    # 콘솔 핸들러 생성
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 파일 핸들러 생성
    file_handler = RotatingFileHandler(
        filename=LOG_FILE_PATH,
        encoding='utf-8',
        maxBytes=10 * 1024 * 1024,
        backupCount=4
    )
    file_handler.setLevel(logging.INFO)
    rollover_session_logs()

    # 핸들러에 로그 포맷 설정
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 로거에 핸들러 추가
    _logger.addHandler(console_handler)
    _logger.addHandler(file_handler)

    return _logger


logger = set_logger("INFO")
