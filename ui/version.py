from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QPushButton


class Version(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('深度学习推理软件版本0.1')
        # 创建按钮到新创建的dialog对象中
        self.btn = QPushButton('ok', self)
        self.btn.clicked.connect(self.close)
        # 移动按钮，设置dialog的标题
        self.resize(200, 100)
