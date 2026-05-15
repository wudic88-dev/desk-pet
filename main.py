import sys

from PySide6.QtWidgets import QApplication

from ui.chat_bubble import ChatBubble
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

    # 气泡对话框单例管理
    bubble = None

    def on_pet_clicked():
        nonlocal bubble
        logger.info("猫咪被点击了！")

        if bubble is not None and bubble.isVisible():
            # 气泡已显示则关闭
            bubble.close()
            bubble = None
            return

        # 创建并显示气泡
        bubble = ChatBubble(pet)
        bubble.closed.connect(lambda: None)
        bubble.show()

    pet.pet_clicked = on_pet_clicked

    logger.info("桌宠启动完成")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
