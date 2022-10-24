from PyQt5 import QtCore
from PyQt5.QtCore import QThread

from utils.DcmHelper import dcmdirprocess
from utils.NiiHelper import niiprocess
# 读取images数据的线程
from utils.tools import buildintypes


class ReadThread(QThread):  # 建立一个任务线程类,这个是读取数据的
    result = QtCore.pyqtSignal(tuple)  # 结果

    def __init__(self, datapath="", typename=""):
        super(ReadThread, self).__init__()
        self.datapath = datapath
        self.typename = typename

    def setinit(self, path, name):
        self.datapath = path
        self.typename = name

    # 读取单个太慢了，设置读取一整个文件夹,但是这样就没有进度条了
    def autoprocess(self):
        if self.typename in buildintypes:
            if self.typename == "CT肾肿瘤":
                return niiprocess(self.datapath, self.typename)
            elif self.typename == "CT气胸":
                return dcmdirprocess(self.datapath, self.typename)

    def run(self):  # 在启动线程后任务从这个函数里面开始执行
        if not self.datapath or not self.typename:
            return
        # 不同类型的自动处理
        imgs, pt = self.autoprocess()
        self.result.emit((imgs, pt))
