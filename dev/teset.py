import sys

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
from view.selectGui import SelectGui

class testWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.btn3 = MyBtn(text="一个标签")

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.btn3)

        self.setLayout(self.layout)

    def test(self):
        print("ok")


class MyBtn(QLabel):
    def __init__(self, text):
        super().__init__(text)

    def mouseMoveEvent(self, e):
        print("ok")

    def mousePressEvent(self, e):
        print("Not Ok")

    def enterEvent(self, a0):
        print("鼠标进入")
        return super().enterEvent(a0)

    def leaveEvent(self, a0):
        print("鼠标划出" + str(self))
        return super().leaveEvent(a0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    sg =SelectGui(w)
    w.show()

    sys.exit(app.exec_())
