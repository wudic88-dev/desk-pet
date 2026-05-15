import sys

from PySide6.QtWidgets import QApplication

from ui.pet_window import PetWindow
from ui.tray_manager import TrayManager
from utils.logger import setup_logger

logger = setup_logger()


def main():
    logger.info("=" * 40)
    logger.info("  桌宠小橘 启动中...")
    logger.info("=" * 40)

    # 创建应用
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出，只有托盘退出才退出

    # 创建宠物窗口
    pet = PetWindow()
    pet.show()

    # 创建系统托盘
    tray = TrayManager(app, parent=pet)
    tray.show()
    tray.show_message("桌宠小橘", "小橘已来到你的桌面！点击它试试~")

    # 绑定点击事件（后续会弹出气泡对话框）
    def on_pet_clicked():
        logger.info("猫咪被点击了！")
        # Day 4 会在这里弹出气泡对话框

    pet.pet_clicked = on_pet_clicked

    logger.info("桌宠启动完成")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
