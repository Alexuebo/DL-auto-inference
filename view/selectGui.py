from functools import partial

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget

from tools import Utils
from ui.select import Ui_select

Model_Num = 6
stylecss = "E:\Dev\Code\Pycharm\pred_QT\\resouces\css\pic.css"


# 多继承方式构造ui
class SelectGui(QWidget, Ui_select):
    opentype = QtCore.pyqtSignal(str)

    def __init__(self, top_window):
        super().__init__()
        self.setupUi(top_window)
        self.style = Utils.readfile(stylecss)
        self.addslots()
        # self.label_1.setStyleSheet("background-image: url(../resouces/images/CT_Renal.png);") #这样设图片会导致后续css失效

    # 添加槽函数
    def addslots(self):
        for i in range(1, Model_Num + 1):
            lb = "label_" + str(i)
            label = self.__getattribute__(lb)
            # lambda会动态传label 导致6个都是一样的，需要用partial
            label.setStyleSheet(self.style)
            label.clicked.connect(partial(self.OpenWindow, label.text()))
            # label.mouse_in.connect(self.Mousein)
            # label.mouse_out.connect(self.Mouseout)

    def OpenWindow(self, labelname):
        print(labelname)
        self.opentype.emit(labelname)

    # def Mousein(self):
    #     print("mousein")
    #
    # def Mouseout(self):
    #     print("mouseout")
