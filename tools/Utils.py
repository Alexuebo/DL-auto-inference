import os

import cv2
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from tools.DcmHelper import dcmprocess
from tools.NiiHelper import niiprocess

LOG_LINE_NUM = 0

buildintypes = ["CT肾肿瘤", "CT气胸"]


# 打开文件
def open_file(item, msg, type):
    filepath, _ = QFileDialog.getOpenFileName(item, msg, '', type + ";;All Files (*)")
    return filepath


# 打开dicom文件夹
def open_dirs(item, msg):
    path = QFileDialog.getExistingDirectory(item, msg, '', )
    return path


# 读取文件
def readfile(filepath):
    with open(filepath, 'r', encoding="utf-8") as f:
        return f.read()


def infomsg(msg):
    msg_box = QMessageBox(QMessageBox.Information, '提示信息', msg)
    msg_box.exec_()


def alertmsg(msg):
    msg_box = QMessageBox(QMessageBox.Warning, '提示信息', msg)
    msg_box.exec_()


def errormsg(msg):
    msg_box = QMessageBox(QMessageBox.Critical, '错误', msg)
    msg_box.exec_()


def autopendata(item, typename):
    # 根据type选择相应的打开方式
    # @todo 以后用设计模式修改这里，现在先这样
    path = -1
    if typename in buildintypes:
        if typename == "CT肾肿瘤":
            path = open_file(item, "请选择肾肿瘤nii.gz文件", "nii文件 (*.nii.gz)")  # 肾肿瘤nii.gz文件
        elif typename == "CT气胸":
            path = open_dirs(item, "请选择气胸的dicoms文件夹")  # 气胸的dicom文件夹
    return path


def autopenmodel(item, typename):
    # 根据type选择相应的打开方式
    # @todo 以后用设计模式修改这里，现在先这样
    path = -1
    if typename in buildintypes:
        if typename == "CT肾肿瘤":
            path = open_dirs(item, "请选择肾肿瘤训练模型pkl文件夹")
        elif typename == "CT气胸":
            path = open_file(item, "请选择气胸训练的的.pth或者.model文件", "pth文件 (*.pth);;model文件 (*.model)")
    return path


# def msgCritical(item, strInfo):
#     dlg = QMessageBox(item)
#     dlg.setIcon(QMessageBox.Critical)
#     dlg.setText(strInfo)
#     dlg.show()


# 不同类型的处理
def dataformat(path):
    result = -1
    files = os.listdir(path)
    f = files[0]  # 直接取第一个
    if f.endswith(".dcm"):
        imgps = dcmprocess(path)
        result = imgps
    elif f.endswith(".nii.gz"):
        ng = niiprocess(os.path.join(path, f))
        result = ng
    return result


def modelformat(path):
    result = -1
    path = str(path)
    if path.endswith(".pth"):
        # 先这样 后续如果要换模型再说
        print("load pth")
        result = path
    return result


def CVlist2PIL(imagelist):
    lizt = []
    # trans = np.transpose(imagelist, [2, 0, 1])
    for i in imagelist:
        image = CV2PIL(i)
        lizt.append(image)
    return lizt


# CV2转PIL
def CV2PIL(image):
    # img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    img = Image.fromarray(image)
    # image.show()
    return img


def PILlist2CV(imagelist):
    lizt = []
    for i in imagelist:
        image = PIL2CV(i)
        lizt.append(image)
    return lizt


# PIL对象转CV2 cv2格式就是ndarray
def PIL2CV(image):
    img = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    # cv2.imshow("图像", img)
    # cv2.waitKey()
    return img


def Contrast_and_Brightness(alpha, beta, img):
    """使用公式f(x)=α.g(x)+β"""
    # α调节对比度，β调节亮度
    blank = np.zeros(img.shape, img.dtype)  # 创建图片类型的零矩阵
    con = cv2.addWeighted(img, alpha, blank, 1 - alpha, beta)  # 图像混合加权
    return con


def get_window_size(window_type):
    center = 0
    width = 0
    if window_type == 'lung':
        center = -600
        width = 1000
    elif window_type == 'abdomen':
        center = 40
        width = 400
    return center, width


if __name__ == '__main__':
    dataformat("F:\\MedData\\kidney\\data")
