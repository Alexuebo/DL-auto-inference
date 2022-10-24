from PyQt5 import QtWidgets, QtCore, QtGui


# 重写选择页面展示的图片label
from PyQt5.QtWidgets import QLabel


class PicQLabel(QLabel):
    # 自定义信号, 注意信号必须为类属性
    clicked = QtCore.pyqtSignal()
    mouse_in = QtCore.pyqtSignal()
    mouse_out = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(PicQLabel, self).__init__(parent)

    def mousePressEvent(self, ev: QtGui.QMouseEvent):
        self.clicked.emit()

    def enterEvent(self, a0: QtCore.QEvent):
        self.mouse_in.emit()

    def leaveEvent(self, a0: QtCore.QEvent):
        self.mouse_out.emit()
