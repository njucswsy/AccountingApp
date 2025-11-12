from PyQt5.QtWidgets import QApplication
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.app import MoneyManagerApp


def main() -> None:
    app = QApplication(sys.argv)
    window = MoneyManagerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
