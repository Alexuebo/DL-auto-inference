import cv2
import numpy as np


# 图像处理-高斯滤波,
# 这实现太慢了，不如直接用cv2库函数
def gaussion_filter(img, k_size=5, sigma=0.5):
    if len(img.shape) == 3:
        H, W, C = img.shape
    else:
        img = np.expand_dims(img, axis=-1)
        H, W, C = img.shape
    pad = k_size // 2
    out = np.zeros((H + pad * 2, W + pad * 2, C), dtype=np.float)
    out[pad: pad + H, pad:pad + W] = img.copy().astype(np.float)
    k = np.zeros((k_size, k_size), dtype=np.float)
    for x in range(-pad, -pad + k_size):
        for y in range(-pad, -pad + k_size):
            k[y + pad, x + pad] = np.exp(-(x ** 2 + y ** 2) / (2 * (sigma ** 2)))
    k /= (2 * np.pi * sigma * sigma)
    k /= k.sum()
    tmp = out.copy()
    for y in range(H):
        for x in range(W):
            for c in range(C):
                out[pad + y, pad + x, c] = np.sum(k * tmp[y:y + k_size, x:x + k_size, c])
    out = np.clip(out, 0, 255)
    out = out[pad:pad + H, pad:pad + W].astype(np.uint8)
    return out


# 阈值处理-二值化
def thres_filter(img, thresh, maxValue):
    th, dst = cv2.threshold(img, thresh, maxValue, cv2.THRESH_BINARY)
    return dst


# 图像mask提取
def mask_extract(image):
    mask = 255 - image
    # 构造Marker图像
    marker = np.zeros_like(image)
    marker[0, :] = 255
    marker[-1, :] = 255
    marker[:, 0] = 255
    marker[:, -1] = 255

    # 形态学重建
    SE = cv2.getStructuringElement(shape=cv2.MORPH_CROSS, ksize=(7, 7))
    while 1:
        marker_pre = marker
        dilation = cv2.dilate(marker, kernel=SE)
        marker = np.min((dilation, mask), axis=0)
        if (marker_pre == marker).all():
            break
    dst = 255 - marker
    filling = dst - image
    return filling


def imageto3(array):
    image = np.expand_dims(array, axis=2)
    image = np.concatenate((image, image, image), axis=-1)
    return image


def imlistto3(array):
    image = np.expand_dims(array, axis=3)
    image = np.concatenate((image, image, image), axis=-1)
    return image


def changecolor(imgarray):
    img = np.uint8(imgarray)  # 推理出来是浮点型，转整形
    image = imageto3(img)
    image[:, :, 0] = 0  # CV2是B,G,R格式
    image[:, :, 1] = 0  # 只留下R即为红色
    return image


def findVOI(array):
    '''
    从三个方向分别切片，找到VOI
    :param array: 三维ndarray
    :return: 6个下标
    '''
    maxi = maxj = maxk = 0
    mini = minj = mink = 0
    # N方向
    li = 0
    ri = array.shape[0] - 1
    while li < ri:
        scliesli = array[li, ::]
        scliesri = array[ri, ::]
        if np.max(scliesli) > 0 and mini == 0:
            mini = li
        if np.max(scliesri) > 0 and maxi == 0:
            maxi = ri
        if not mini:
            li += 1
        if not maxi:
            ri -= 1
        if mini != 0 and maxi != 0:
            break
    # H方向
    lj = 0
    rj = array.shape[1] - 1
    while lj < rj:
        sclieslj = array[:, lj:, :]
        scliesrj = array[:, rj:, :]
        if minj == 0 and np.max(sclieslj) > 0:
            minj = lj
        if np.max(scliesrj) > 0 and maxj == 0:
            maxj = rj
        if not minj:
            lj += 1
        if not maxj:
            rj -= 1
        if minj != 0 and maxj != 0:
            break
    # W方向
    lk = 0
    rk = array.shape[2] - 1
    while lk < rk:
        sclieslk = array[::, lk]
        scliesrk = array[::, rk]
        if mink == 0 and np.max(sclieslk) > 0:
            mink = lk
        if maxk == 0 and np.max(scliesrk) > 0:
            maxk = rk
        if not mink:
            lk += 1
        if not maxk:
            rk -= 1
        if mink != 0 and maxk != 0:
            break

    return [(maxi, mini), (maxj, minj), (maxk, mink)]
