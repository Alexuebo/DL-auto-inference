from PyQt5 import QtCore
from PyQt5.QtCore import QThread


# 推理线程
class InferThread(QThread):
    signal = QtCore.pyqtSignal(int)
    mask = QtCore.pyqtSignal(list)
    other = QtCore.pyqtSignal(list)

    def __init__(self):
        super(InferThread, self).__init__()
        self.result = []

    def setdata(self, builder, imgdata, modelpath, imgps, thick):
        self.pi = builder.buildinfer(imgdata, modelpath)
        self.pi.imps = imgps
        self.pi.thick = thick

    def run(self):  # 在启动线程后任务从这个函数里面开始执行
        self.signal.emit(1)  # 第一步，预处理
        self.pi.preprocess()

        self.signal.emit(2)  # 第二步，推理
        infermask = self.pi.infer()

        self.signal.emit(3)  # 第三部，后处理
        self.result = self.pi.postprocess(infermask)

        self.signal.emit(4)  # 第四步，计算其他的东西
        others = self.pi.getothers(self.result)

        self.signal.emit(5)  # 提交,一般是这5步骤
        self.mask.emit(self.result)
        self.other.emit(list(others))
