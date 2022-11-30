import cv2
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsView

from utils.ImageHelper import imageto3

'''
重写的QGraphicsView方法
步骤：
1.使用opencv 打开图片
2.cv2转为QImage
3.QImage转为QPixmap
4.把QPixmap加入到QGraphicsScene
5.把QGraphicsScene加入到graphicsView
6.graphicsView show

使用方法：
self.scene = QGraphicsScene()  # 创建画布
self.ui.graphicsView.setScene(self.scene)  # 把画布添加到窗口
self.ui.graphicsView.show()

2 采集数据的线程为非UI线程,则在QGraphicsView中显示时不仅需要添加Item对象,并且更新显示线程需在UI线程中,
否则QGraphicsView不会主动更新显示,使用信号将image放到UI线程中更新即可
3 保证在UI更新时,所需更新的image还未被销毁,由于处于不同的线程,所以image可存储于更新前不会被销毁的对象中
'''


class ImageView(QGraphicsView):
    wheel = QtCore.pyqtSignal(int)  # 鼠标滚动
    process = QtCore.pyqtSignal(int)  # 进度在这

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.images = []
        self.now = 0
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.left_click = False
        self.ctrl = False
        self.end_pos = 0
        self.start_pos = 0

    def setImages(self, imgs):
        # imgs是整个病人，一张张转化为RGB
        for i, img in enumerate(imgs):
            self.process.emit(i)
            if len(img.shape) <= 2:
                img = imageto3(img)
            cvimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 把opencv对象 默认BGR转为RGB
            y, x = cvimg.shape[:-1]
            frame = QImage(cvimg, x, y, QImage.Format_RGB888)
            self.images.append(frame)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self.ctrl = False

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self.ctrl = True

    # 鼠标滚轮事件
    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        if self.images:
            if self.ctrl:
                #  放大缩小
                self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                if event.angleDelta().y() > 0:
                    self.scale(1.1, 1.1)
                    self.__setDragEnabled(self.__isEnableDrag())
                else:
                    self.scale(1 / 1.1, 1 / 1.1)
                    self.__setDragEnabled(self.__isEnableDrag())
            else:
                # 滚动上下图片
                if event.angleDelta().y() > 0:  # 上滚
                    if self.now == 0:
                        return
                    else:
                        self.now -= 1
                        self.wheel.emit(self.now)
                else:  # 下滚
                    if self.now == len(self.images) - 1:
                        return
                    else:
                        self.now += 1
                        self.wheel.emit(self.now)

    # 图片的拖动

    def __isEnableDrag(self):
        """ 根据图片的尺寸决定是否启动拖拽功能 """
        v = self.verticalScrollBar().maximum() > 0
        h = self.horizontalScrollBar().maximum() > 0
        return v or h

    def __setDragEnabled(self, isEnabled: bool):
        """ 设置拖拽是否启动 """
        self.setDragMode(
            self.ScrollHandDrag if isEnabled else self.NoDrag)
