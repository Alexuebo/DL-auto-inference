import time

from PyQt5 import QtCore
from PyQt5.QtCore import QThread

# 读取images数据的线程
from model.CT_PNE.PneInfer import PneInfer


class InferThread(QThread):  # 建立一个任务线程类,这个是读取数据的
    signal = QtCore.pyqtSignal(int)  # 设置触发信号传递的参数数据类型,这里是字符串
    mask = QtCore.pyqtSignal(list)
    other = QtCore.pyqtSignal(list)

    def __init__(self):
        super(InferThread, self).__init__()
        self.result = []

    def setdata(self, imgdata, modelpath, imgps, thick):
        self.pi = PneInfer(imgdata, modelpath)
        self.imgps = imgps
        self.thick = thick

    def run(self):  # 在启动线程后任务从这个函数里面开始执行
        self.signal.emit(1)  # 第一步，推理
        infermask = self.pi.infer()

        self.signal.emit(2)  # 第二部，后处理
        self.result = self.pi.postprocess(infermask)

        self.signal.emit(3)  # 第三步，计算体积
        v = self.pi.getvolume(self.result, self.imgps, self.thick)

        self.signal.emit(4)  # 最后一步，提交
        self.mask.emit(self.result)
        retother = [v]
        self.other.emit(retother)
