import os
import time

import cv2
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QStyle, QDialog, QGraphicsScene

# 主界面处理的逻辑
from model.Base.BaseBuilder import BaseBuilder
from model.CT_Renal.RCCInfer import RCCInfer
from threads.InferThread import InferThread
from threads.ReadThread import ReadThread
from ui.mainwindow import Ui_main
from ui.version import Version
from utils.ImageHelper import imageto3, changecolor
from utils.NiiHelper import readnii, mask_to_onehot
from utils.tools import alertmsg, autopendata, autopenmodel, errormsg, savemasks, infomsg
from view.selectGui import SelectGui


class MainGui(QMainWindow, Ui_main):

    def __init__(self, parent, type_name=""):
        super().__init__(parent)
        self.setupUi(parent)  # 初始化界面ui

        self.qd = QDialog()  # 选择框，QDialog才有exec widget没有，只有show
        self.selectui = SelectGui(self.qd)  # 要通过self实例化为类变量，不然在函数内部会被回收
        self.type_name = type_name
        self.datapath = ""
        self.modelpath = ""
        self.inferdata = []  # 推理结果
        self.imgdata = []  # 读取图像
        self.imgps = []  # 像素间距
        self.start_time = 0  # 记录开始时间
        self.imgthick = 0  # 图像层厚
        self.imgcnt = 0  # 图像张数
        self.image_scene = QGraphicsScene()  # 创建画布
        self.infer_scene = QGraphicsScene()  # 画布2
        self.readthread = ReadThread()  # 读取文件的线程
        self.inferthread = InferThread()  # 推理的线程
        self.builder = BaseBuilder()
        self.version = Version()

        self.statinfo = QLabel(self)  # 状态条

        self.initActions()

    def initActions(self):
        style = QApplication.style()
        # 先隐藏进度条
        self.progressBar.hide()
        self.view_ScrollBar.hide()
        # =============Action绑定槽函数===========
        self.selectui.opentype.connect(self.set_typename)
        self.action_load_data.triggered.connect(self.load_data)
        self.action_load_model.triggered.connect(self.load_model)
        self.action_select.triggered.connect(self.openSelect)
        self.action_about.triggered.connect(self.openAbout)
        self.action_cancel_all.triggered.connect(self.resetall)
        self.action_save_result.triggered.connect(self.save_result)
        self.actionopen_seg.triggered.connect(self.openseg)
        self.btn_predict.clicked.connect(self.predict)
        self.btn_save.clicked.connect(self.save_result)
        # ========= 样式设计 ===============
        self.action_load_data.setIcon(style.standardIcon(QStyle.SP_DialogOpenButton))
        self.action_load_model.setIcon(style.standardIcon(QStyle.SP_ComputerIcon))
        self.action_select.setIcon(style.standardIcon(QStyle.SP_FileDialogListView))
        self.action_about.setIcon(style.standardIcon(QStyle.SP_MessageBoxInformation))
        self.action_cancel_all.setIcon(style.standardIcon(QStyle.SP_MessageBoxCritical))
        self.action_save_result.setIcon(style.standardIcon(QStyle.SP_DialogSaveButton))
        self.actionopen_seg.setIcon(style.standardIcon(QStyle.SP_DialogOpenButton))
        # self.btn_predict.setIcon(style.standardIcon(QStyle.SP_DialogOpenButton))
        # ============状态条设置==============
        self.statinfo.setText('当前未选择模型!')
        self.statinfo.setAlignment(Qt.AlignLeft)
        self.statusbar.addPermanentWidget(self.statinfo)
        # ============其他设置================
        self.infer_view.show()
        self.image_view.show()  # 展示
        self.image_view.setScene(self.image_scene)  # 把画布添加到窗口
        self.infer_view.setScene(self.infer_scene)  # 把画布添加到窗口
        self.image_view.wheel.connect(self.wheelpicture)
        self.infer_view.wheel.connect(self.wheelpicture)
        self.view_ScrollBar.valueChanged.connect(self.wheelpicture)

        self.readthread.result.connect(self.read_data_callback)  # 设置任务线程发射信号触发的函数
        self.image_view.process.connect(self.image_view_process)
        self.inferthread.signal.connect(self.infer_process)  # 推理进度
        self.inferthread.mask.connect(self.infer_callback)  # 结果
        self.inferthread.other.connect(self.infer_others)  # 其他要计算的

    def set_typename(self, name):
        code = self.builder.settypename(name)
        if code == -1:
            self.printolog("暂未支持该模型: %s" % name)
            alertmsg("暂未支持该模型: %s" % name)
        else:
            self.type_name = name
            self.statinfo.setText("当前选择模型: " + self.type_name)
            self.printolog("当前选择模型: " + self.type_name)
            self.qd.hide()

    def resetall(self):
        self.log_data.clear()
        self.type_name = ""
        self.datapath = ""
        self.modelpath = ""
        self.inferdata = []  # 推理结果
        self.imgdata = []
        self.imgps = []  # 像素间距
        self.start_time = 0  # 记录开始时间
        self.imgthick = 0  # 图像层厚
        self.imgcnt = 0  # 图像张数
        self.image_scene.clear()
        self.infer_scene.clear()
        self.printolog("重置了所有变量")
        self.statinfo.setText('当前未选择模型!')

    def openAbout(self):
        self.version.show()

    def openSelect(self):
        self.qd.exec_()  # 直接打开窗口，阻塞式的

    def openseg(self):
        if len(self.datapath) > 0:
            masks_path = autopendata(self, self.type_name)
            if masks_path:
                masks = readnii(masks_path)
                onehotmasks = mask_to_onehot(masks, [[0], [1], [2]])  # 三分类，0背景 1kidney 2tumor
                renalmask = onehotmasks[1].astype("uint8")  # 预测出来是float 需要转int
                tumormask = onehotmasks[2].astype("uint8")  # 肿瘤mask
                self.infer_callback(tumormask)
                r = RCCInfer(self.datapath, self.modelpath)
                vo = r.getothers([renalmask, tumormask])
                self.infer_others(vo)
        else:
            self.printolog("未选择数据")

    def printolog(self, msg):
        t = "--" + time.asctime() + "--"
        self.log_data.append(t + msg)

    def check_before_load(self, type):
        if not self.type_name:
            self.printolog("请先选择模型类型！")
            alertmsg("请先选择模型类型！")
            return
        path = ""
        if type == "model":
            path = autopenmodel(self, self.type_name)
            if path:
                self.modelpath = path
                self.printolog("请确认模型路径为：" + self.modelpath)
                return 1
        elif type == "data":
            path = autopendata(self, self.type_name)
            if path:
                self.datapath = path
                self.printolog("请确认数据路径为：" + self.datapath)
                if os.path.isfile(self.datapath):
                    cnt = 1
                else:
                    cnt = len(os.listdir(self.datapath))
                self.printolog("共扫描到{}条数据，读取中...".format(cnt))
                return 1
        if not path:
            self.printolog("未选择数据")
        if path == -1:
            self.printolog("数据类型暂未集成")

    def maskadd(self, mask):
        yuan = self.imgdata
        rets = []
        if len(yuan) == len(mask):
            for idx in range(len(yuan)):
                d = imageto3(yuan[idx])
                _, th3 = cv2.threshold(mask[idx], 0, 255, cv2.THRESH_BINARY)
                p = changecolor(th3)  # 修改mask为红色
                img = cv2.bitwise_or(d, p)
                rets.append(img)
        if rets:
            self.inferdata = rets

    def show_images(self, scene, view, num):
        scene.clear()  # 先清空上次的残留
        pix1 = QPixmap.fromImage(view.images[num])  # 展示第num张图片
        scene.addPixmap(pix1)

    # 让两个画布同时滚动
    def wheelpicture(self, pos):
        self.view_ScrollBar.setValue(pos)
        self.image_view.now = pos
        if len(self.imgdata) and len(self.inferdata):
            self.infer_view.now = pos
            self.show_images(self.image_scene, self.image_view, pos)
            self.show_images(self.infer_scene, self.infer_view, pos)
        elif len(self.imgdata):
            self.show_images(self.image_scene, self.image_view, pos)

    def read_data_callback(self, ret):
        # 显示到grahic
        self.imgdata = ret[0]
        self.imgps = ret[1][0]
        self.imgthick = ret[1][1]
        self.imgcnt = len(self.imgdata)
        self.printolog("读取并自动调整窗位完成，共{}张图像".format(self.imgcnt))
        self.image_view.setImages(self.imgdata)  # 设置到缓存
        self.show_images(self.image_scene, self.image_view, 0)  # 展示第一张
        # 显示滚动条
        self.view_ScrollBar.setRange(0, self.imgcnt - 1)  # 从0开始要减1
        self.view_ScrollBar.show()

    def infer_callback(self, ret):
        timecnt = time.perf_counter() - self.start_time
        self.printolog("推理完成，用时 " + str(round(timecnt)) + "s")
        # mask与原图相加
        self.maskadd(ret)
        self.infer_view.setImages(self.inferdata)
        self.show_images(self.infer_scene, self.infer_view, 0)  # 展示第一张

    def image_view_process(self, index: int):  # 传回来填入的index
        QtWidgets.QApplication.processEvents()
        precent = (index + 1) * (100 / self.imgcnt)  # 转化为百分比
        if precent < 100:
            self.progressBar.setValue(precent)
            self.progressBar.show()
        else:
            self.progressBar.hide()

    def infer_process(self, step):  # 推理进度条
        QtWidgets.QApplication.processEvents()
        if step != 5:
            self.progressBar.setFormat("第%s步处理中..." % step)
            self.progressBar.show()
        else:
            self.progressBar.hide()

    def infer_others(self, ret):
        # 展示其他结果,list形式
        # 后处理类，根据typename选择
        self.builder.buildpost().printmsg(self, ret)

    def load_data(self):
        # 先看选择的类型，再读取数据
        if self.check_before_load("data"):
            self.readthread.setinit(self.datapath, self.type_name)
            self.readthread.start()

    def load_model(self):
        if self.check_before_load("model") and self.check_before_load("data"):
            # 模型检查是否存在文件
            infomsg("检查数据和模型完毕，可以开始推理！")

    def predict(self):
        if not self.type_name or not self.modelpath or len(self.imgdata) == 0:
            errormsg("未读取模型或数据，无法推理")
        else:
            self.printolog("***************开始推理!***************")
            self.start_time = time.perf_counter()
            # 新线程做推理
            self.inferthread.setdata(self.builder, self.imgdata, self.modelpath, self.imgps, self.imgthick)
            self.inferthread.start()

    def save_result(self):
        if not self.inferdata:
            errormsg("未推理，请推理后保存数据")
        else:
            path = savemasks(self)
            if path:
                self.printolog("开始保存数据，路径为：" + path)
                for i, item in enumerate(self.inferdata):
                    name = "%03d" % i + ".png"
                    cv2.imwrite(os.path.join(path, name), item)
            else:
                self.printolog("未选择保存位置")
