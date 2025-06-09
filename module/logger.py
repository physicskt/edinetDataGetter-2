import logging
import time
import threading
import os
from pathlib import Path

def setup_logger(log_file: str = None, max_lines: int = 10000, delete_lines: int = 2000):
    # Default log file path if not provided
    if log_file is None:
        # Create log directory in parent directory (project root)
        log_dir = Path(__file__).parent.parent / 'log'
        log_dir.mkdir(exist_ok=True)
        log_file = str(log_dir / 'logfile.log')
    
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # ロガーの設定
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # コンソール出力用のハンドラーを設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # ログファイル出力用のハンドラーを設定
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # フォーマッターを設定（ファイル名と行数を含む）
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # ハンドラーをロガーに追加
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.info("")
    logger.info("ログを開始します。")
    logger.info("")

    # バックグラウンドスレッドでファイル監視を開始
    monitor_thread = threading.Thread(target=monitor_log_file, args=(log_file, max_lines, delete_lines), daemon=True)
    monitor_thread.start()

    return logger

def monitor_log_file(log_file: str, max_lines: int, delete_lines: int):
    """
    ログファイルを監視し、行数が指定した最大数を超えた場合に行を削除します。
    バックグラウンドで実行されます。
    """
    while True:
        if check_file_lines(log_file, max_lines):
            trim_file(log_file, delete_lines)
        
        time.sleep(5)  # 1秒ごとに監視を行う

def check_file_lines(log_file: str, max_lines: int) -> bool:
    try:
        with open(log_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        return len(lines) > max_lines
    except FileNotFoundError:
        return False

def trim_file(log_file: str, delete_lines: int):
    try:
        with open(log_file, 'r+', encoding='utf-8') as file:
            lines = file.readlines()
            if len(lines) > delete_lines:
                # 最初の2000行を削除
                lines = lines[delete_lines:]
                # ファイルを書き換え
                file.seek(0)
                file.truncate(0)
                file.writelines(lines)
                print(f"Removed the first {delete_lines} lines from the log file.")
            else:
                print("No lines to delete.")
    except FileNotFoundError:
        print("Log file does not exist.")

def log_long_msg(msg: str):
    logger.info("")
    logger.info("##################################")
    logger.info(f"{msg}")
    logger.info("##################################")

def log_user_error(user_msg: str, technical_context: str = None, exception: Exception = None):
    """
    Log a user-friendly error message to console and detailed technical info to file.
    
    Args:
        user_msg: Simple, clear message for general users
        technical_context: Additional context for debugging (optional)  
        exception: Exception object for detailed logging (optional)
    """
    # User-friendly message to console and file
    logger.error(f"❌ {user_msg}")
    
    # Technical details only to file for debugging
    if technical_context or exception:
        # Create a temporary logger that only writes to file
        file_logger = logging.getLogger('technical_details')
        file_logger.setLevel(logging.DEBUG)
        
        # Only add file handler if not already present
        if not file_logger.handlers:
            log_dir = Path(__file__).parent.parent / 'log'
            log_dir.mkdir(exist_ok=True)
            log_file = str(log_dir / 'logfile.log')
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
            file_handler.setFormatter(formatter)
            file_logger.addHandler(file_handler)
            file_logger.propagate = False  # Prevent duplicating to root logger
        
        # Log technical details to file
        if technical_context:
            file_logger.debug(f"Technical context: {technical_context}")
        if exception:
            file_logger.exception("Detailed error information:")

def log_user_warning(user_msg: str, technical_context: str = None):
    """
    Log a user-friendly warning message.
    
    Args:
        user_msg: Simple, clear warning message for general users
        technical_context: Additional context for debugging (optional)
    """
    logger.warning(f"⚠️ {user_msg}")
    
    if technical_context:
        # Log technical details to file only
        file_logger = logging.getLogger('technical_details')
        if file_logger.handlers:  # Only if already set up
            file_logger.debug(f"Warning context: {technical_context}")

def log_user_success(user_msg: str):
    """Log a user-friendly success message."""
    logger.info(f"✅ {user_msg}")

log_file = str(Path(__file__).parent / 'log' / 'logfile.log')
logger = setup_logger(log_file)

if __name__ == "__main__":
    logger.info("This is a log message!")

    # メインスレッドが終了しないようにするため、ここで待機
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated.")
