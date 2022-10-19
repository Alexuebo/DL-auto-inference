import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QStyle, QDialog, QMessageBox

# 主界面处理的逻辑
from tools.Utils import alertmsg, autopendata, autopenmodel, errormsg
from ui.mainwindow import Ui_main
from ui.version import Version
from view.selectGui import SelectGui


class ReadThread(QThread):  # 建立一个任务线程类
    signal = QtCore.pyqtSignal(str)  # 设置触发信号传递的参数数据类型,这里是字符串

    def __init__(self):
        super(ReadThread, self).__init__()

    def run(self):  # 在启动线程后任务从这个函数里面开始执行
        for i in range(10):
            self.signal.emit(str(i))  # 任务线程发射信号用于与图形化界面进行交互,进度条之类的
            time.sleep(1)


class MainGui(QMainWindow, Ui_main):

    def __init__(self, parent, type_name=""):
        super().__init__(parent)
        self.qd = QDialog()  # 选择框，QDialog才有exec widget没有，只有show
        self.selectui = SelectGui(self.qd)  # 要通过self实例化为类变量，不然在函数内部会被回收
        self.setupUi(parent)
        self.timer = time
        self.type_name = type_name
        self.datapath = ""
        self.modelpath = ""
        self.inferesult = []
        self.readthread = ReadThread()  # 读取文件的线程
        self.readthread.signal.connect(self.read_data_callback)  # 设置任务线程发射信号触发的函数

        self.initActions()

    def initActions(self):
        style = QApplication.style()
        # =============Action绑定槽函数===========
        self.selectui.opentype.connect(self.set_typename)
        self.action_load_data.triggered.connect(self.load_data)
        self.action_load_model.triggered.connect(self.load_model)
        self.action_select.triggered.connect(self.openSelect)
        self.action_about.triggered.connect(self.openAbout)
        self.action_cancel_all.triggered.connect(self.resetall)
        self.action_save_result.triggered.connect(self.save_result)

        self.btn_predict.clicked.connect(self.predict)
        self.btn_save.clicked.connect(self.save_result)
        # self.btn_predict.setIcon(style.standardIcon(QStyle.SP_DialogOpenButton))
        # ========= 样式设计 ===============
        # 推理SP_MediaPlay 打开文件夹SP_DirOpenIcon  保存SP_DialogSaveButton  SP_ComputerIcon SP_MessageBoxCritical
        self.action_load_data.setIcon(style.standardIcon(QStyle.SP_DialogOpenButton))
        self.action_load_model.setIcon(style.standardIcon(QStyle.SP_ComputerIcon))
        self.action_select.setIcon(style.standardIcon(QStyle.SP_FileDialogListView))
        self.action_about.setIcon(style.standardIcon(QStyle.SP_MessageBoxInformation))
        self.action_cancel_all.setIcon(style.standardIcon(QStyle.SP_MessageBoxCritical))
        self.action_save_result.setIcon(style.standardIcon(QStyle.SP_DialogSaveButton))
        # ============状态条设置==============
        self.statinfo = QLabel(self)
        self.statinfo.setText('当前未选择模型!')
        self.statinfo.setAlignment(Qt.AlignLeft)
        self.statusbar.addPermanentWidget(self.statinfo)

    def set_typename(self, name):
        self.type_name = name
        self.statinfo.setText("当前选择模型: " + self.type_name)
        self.printolog("当前选择模型: " + self.type_name)
        self.qd.hide()

    def resetall(self):
        self.log_data.clear()
        self.datapath = ""
        self.modelpath = ""
        self.type_name = ""
        self.printolog("重置了所有变量")
        self.statinfo.setText('当前未选择模型!')

    def openAbout(self):
        self.version = Version()
        self.version.show()

    def openSelect(self):
        self.qd.exec_()  # 直接打开窗口，阻塞式的

    def printolog(self, msg):
        t = "===" + self.timer.asctime() + "=== "
        self.log_data.append(t + msg)

    def check_before_load(self, type):
        if not self.type_name:
            self.printolog("请先选择模型类型！")
            alertmsg("请先选择模型类型！")
            return
        path = ""
        if type == "model":
            path = autopenmodel(self, self.type_name)
            self.modelpath = path if path else self.modelpath
        elif type == "data":
            path = autopendata(self, self.type_name)
            self.datapath = path if path else self.datapath
        if not path:
            self.printolog("未选择数据")
            return
        if path == -1:
            self.printolog("数据类型暂未集成")
            return
        else:
            # 数据有效
            self.printolog("请确认数据路径为：" + path)
            return 1

    def load_data(self):
        # 先看选择的类型，再读取数据
        if self.check_before_load("data"):
            print("check data ok")


    def load_model(self):
        # 读取模型类型
        if self.check_before_load("model"):
            print("check model ok")

    def read_data_callback(self):
        # 读取数据信号回调函数
        pass

    def predict(self):
        # 新线程做推理，读取，之类的
        if not self.type_name or not self.modelpath or not self.datapath:
            errormsg("未读取模型或数据，无法推理")
        else:
            self.printolog("##### 开始推理！#####")

    def save_result(self):
        if not self.inferesult:
            errormsg("未推理，请推理后保存数据")
        else:
            self.printolog("数据保存于：")
