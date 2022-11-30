import cv2
import numpy as np

R = ["<4cm", "4~7cm", ">7cm"]  # 最大径 Radius (maximal diameter in cm)
E = [">50%", "<50%", "1"]  # 内生性 Exophytic/endophytic properties
N = [">7mm", "4~7mm", "<4mm"]  # 距离肾门位置 Nearness of the tumor to the collecting system or sinus (mm)
L = ["outer",  # 完全在上下极线之外
     "through",  # 肿瘤穿过肾极线
     "inner"]  # 与肾上下极的位置关系 Location relative to the polar lines
'''
只有前四项给分，分别是1~3分，最小4分 最大12分
4~6为低度复杂性 7~9中度 10~12高度
'''
A = ["A", "P", "X"]  # 位于腹/背侧 Anterior/Posterior 不给分，只附加后缀A, P, X
H = ["H"]  # 如果肿瘤触及主肾动脉或静脉，则指定后缀“H”


# 肾肿瘤评分的处理类
class RenalRate:
    def __init__(self, r=0, e=0, n=0, ll="", a="", h=""):
        # 给出评分如  9ah 4p 12xh
        self.R = r
        self.E = e
        self.N = n
        self.L = ll
        self.A = a
        self.H = h

    def getTNM(self):
        T = ""
        if self.R != 0:
            if self.R <= 7:
                T = "T1"
                if self.R <= 4:
                    T += "a"
                else:
                    T += "b"
            elif self.R <= 15:
                T = "T2"
                if self.R <= 10:
                    T += "a"
                else:
                    T += "b"
            elif self.R < 20:
                T = "T3"
            else:
                T = "T4"
        return T

    def getscore(self, renal, renalmask, tumormask, imps, thick):
        # 1.最大径R ok
        if self.R == 0:
            _, self.R = calcuateVR(tumormask, imps, thick)
        # 2.肾和肿瘤交比 E ok
        self.E = calcuateE(renalmask, tumormask)
        # 3.肿瘤和肾盂最近距离 N
        self.N, RPmask = calcuateN(renal, renalmask, tumormask, imps)
        # 4.与上下极线的关系 L
        self.L = calcuateL(RPmask, renalmask, tumormask)
        return self.cntRENAL()

    def cntRENAL(self):
        '''
        计算评分，输出值
        :param input:
        :return:
        '''
        score = 0
        if self.R != 0:
            if self.R <= 4:
                r = 1
            elif self.R <= 7:
                r = 2
            else:
                r = 3
            score += r
            self.R = r
        if self.E != 0:
            if self.E < 0.5:
                e = 1
            elif self.E < 1:
                e = 2
            else:
                e = 3
            score += e
            self.E = e
        if self.N >= 0:
            if self.N >= 7:
                n = 1
            elif self.N > 4:
                n = 2
            else:
                n = 3
            score += n
            self.N = n
        if self.L != 0:
            score += self.L
        if score < 6:
            comp = " 低度复杂性"
        elif score <= 9:
            comp = " 中度复杂性"
        else:
            comp = " 高度复杂性"
        if self.A.upper() in A:
            score = str(score)
            score += self.A.lower()
        if self.H.upper() in H:
            score = str(score)
            score += self.H.lower()
        return str(score) + comp


def calcuateVR(tumormask, imps, thick):
    '''
    计算体积 V 和 最大径 R
    :param thick:
    :param imps:
    :param tumormask:
    :return:
    '''
    volume = 0
    maxlenth = 0
    for m in tumormask:
        _, th3 = cv2.threshold(m, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        notzero = cv2.countNonZero(th3)  # 统计肿瘤点数
        volume += (notzero * imps[0] * imps[1] * thick)  # 求和
        # 找外轮廓，计算轴向最大径
        contours, _ = cv2.findContours(th3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours):
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)  # 外接正矩形，用最小外接矩形计算太麻烦了
                maxlenth = max(maxlenth, w, h)
    volume = round(volume / 1000, 2)  # 体积转化为ml
    maxlenth = round(maxlenth * imps[0] / 10, 2)  # 单位*像素间距=mm 化成cm

    return volume, maxlenth


def calcuateE(renalmask, tumormask):
    if renalmask.shape[0] != tumormask.shape[0]:
        return
    else:
        E = 0.0
        cnt = 0
        for i in range(renalmask.shape[0]):
            K = renalmask[i]
            T = tumormask[i]
            _, thK = cv2.threshold(K, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            _, thT = cv2.threshold(T, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thK, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 提取肾脏轮廓
            if len(contours):
                for c in contours:  # 有两个肾轮廓，依次遍历
                    hull = cv2.convexHull(c)  # 找凸包
                    NK = np.zeros(K.shape)  # 生成一个空图
                    convexK = cv2.fillConvexPoly(NK, hull, (255, 255, 0)).astype("uint8")  # 在空图中绘制凸包mask
                    N = cv2.bitwise_and(convexK, thT)  # 求T与K交集
                    tumorarea = np.sum(np.float32(np.greater(thT, 0)))
                    and_area = np.sum(np.float32(np.greater(N, 0)))
                    if np.greater(tumorarea, 0):
                        iou = and_area / tumorarea
                        if iou:
                            cnt += 1
                            E += iou
        return E / cnt


def calcuateN(renal, renalmask, tumormask, imps):
    '''
    计算肿瘤与肾盂最小距离N
    :param renal:
    :param renalmask:
    :param tumormask:
    :param imps:
    :return:
    '''
    RP = []
    minN = 99999999
    for i in range(renal.shape[0]):
        # 1.ROI裁剪
        _, renth = cv2.threshold(renalmask[i], 0, 255, cv2.THRESH_BINARY)
        image = cv2.bitwise_and(renal[i], renth)
        gaussion_image = cv2.GaussianBlur(image, (5, 5), 0.5)
        # 2.分割得到肾盂mask
        _, thresh_image = cv2.threshold(gaussion_image, 50, 255, cv2.THRESH_BINARY_INV)
        rp = cv2.bitwise_and(thresh_image, image)
        rp = cv2.dilate(rp, kernel=np.ones((4, 4), np.uint8), iterations=1)
        _, thrp = cv2.threshold(rp, 0, 255, cv2.THRESH_BINARY)
        RP.append(thrp)  # 肾盂mask，需要返回的
        # 3.计算RP与tumormask 的最近欧式距离n
        tumorcnt, _ = cv2.findContours(tumormask[i], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        rpcnt, _ = cv2.findContours(thrp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if tumorcnt and rpcnt:
            for t in tumorcnt:
                for r in rpcnt:
                    t = np.squeeze(t)
                    r = np.squeeze(r)
                    dis = minDistance(t, r)
                    # 4.换算成mm
                    dis = dis * imps[0]
                    minN = min(minN, dis)
    RPmask = np.array(RP)
    return minN, RPmask


def minDistance(contour, contourOther):
    distanceMin = 99999999
    # 如果只有一个点，那就跳过
    if len(contour.shape) == 1 or len(contourOther.shape) == 1:
        return distanceMin
    for (xA, yA) in contour:
        for (xB, yB) in contourOther:
            distance = ((xB - xA) ** 2 + (yB - yA) ** 2) ** (1 / 2)  # 欧式距离
            if distance < distanceMin:
                distanceMin = distance
    return distanceMin


def calcuateL(RPmask, renalmask, tumormask):
    '''
    计算与肾极线的位置关系
    :param RPmask:
    :param renalmask:
    :param tumormask:
    :return:
    有个问题，左右肾有两个
    '''
    rmid = findMidOfMask(renalmask)  # 肾中线平面
    RPmin, RPmax = findLimitOfMask(RPmask)  # 肾盂
    tumormin, tumormax = findLimitOfMask(tumormask)  # 肾肿瘤
    tumormid = (tumormin + tumormax) // 2
    rmin = (RPmin + rmid) // 2  # 上极线平面
    rmax = (RPmax + rmid) // 2  # 下极线平面
    if tumormax < rmin or tumormin > rmax:
        return 1
    elif tumormin < rmid < tumormax or rmin < tumormid < rmax:
        return 3
    else:
        return 2


def findMidOfMask(array):
    a, b = findLimitOfMask(array)
    return (a + b) // 2


def findLimitOfMask(array):
    mini = maxi = 0
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
    return mini, maxi


def calcuateRENAL():
    '''
    这些计算很像，可以写在一个方法里面提升计算速度，但是可读性会降低
    :return:
    '''
    pass
