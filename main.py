#!/usr/bin/env python3
"""
Task Management Application
Main entry point for the application.
"""

import sys
import os
import logging

# Setup logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, "app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QFont
        from ui.main_window import MainWindow

        logger.info("Starting Task Management Application")

        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("タスク管理")
        app.setStyle("Fusion")

        # Set default font
        font = QFont("Segoe UI", 10)
        app.setFont(font)

        # Create and show main window
        window = MainWindow()
        window.show()

        logger.info("Application started successfully")

        # Run event loop
        exit_code = app.exec()

        logger.info("Application closed with exit code: %d", exit_code)
        return exit_code

    except ImportError as e:
        logger.error("Failed to import required modules: %s", e)
        print(f"エラー: 必要なモジュールがインストールされていません: {e}")
        print("pip install PyQt6 を実行してください。")
        return 1
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"エラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
