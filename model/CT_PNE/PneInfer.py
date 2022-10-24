'''
使用气胸进行推理的推理类
'''
import cv2
import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import transforms

from model.Base.BaseInfer import BaseInfer
from model.CT_PNE.AttU_Net import AttU_Net
from model.CT_PNE.PNEDataset import PNEDataset
from threads.ReadThread import ReadThread
from utils.ImageHelper import gaussion_filter, thres_filter, mask_extract, imageto3
from utils.tools import PILlist2CV

batchsize = 4

x_transforms = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])

y_transforms = transforms.ToTensor()


class PneInfer(BaseInfer):
    def __init__(self, img_data, model_data, imps="", thick=""):
        super().__init__(img_data, model_data)
        self.feiye = []
        self.feiyevol = 0
        self.imps = imps  # 像素间距 CT图像特有的
        self.thick = thick  # 层厚

    def preprocess(self):
        '''
        预处理得到肺野,计算肺体积并保存
        :return:
        '''
        retimg = []
        for i in self.img_data:
            # gaussion_image = gaussion_filter(i, 5, 0.5)  # 高斯平滑
            gaussion_image = cv2.GaussianBlur(i, (5, 5), 0.5)
            thresh_image = thres_filter(gaussion_image, thresh=230, maxValue=255)  # 阈值分割
            mask = mask_extract(thresh_image)
            # 将image的相素值和mask像素值相加得到结果
            masked = cv2.add(gaussion_image, np.zeros(np.shape(i), dtype=np.uint8), mask=mask)
            retimg.append(masked)
            # 统计下肺野体积，好计算压缩比
            notzero = cv2.countNonZero(mask)
            self.feiyevol += (notzero * self.imps[0] * self.imps[1] * self.thick)  # 求和
        self.feiye = retimg

    def infer(self):
        mod = AttU_Net(3, 1)
        imlists = self.feiye  # 输入预处理过后的模型
        ckpt = self.model_data  # 模型
        # 是否使用cuda
        if torch.cuda.is_available():
            # torch.cuda.empty_cache()
            device = torch.device("cuda")
            mod = mod.cuda()
        else:
            device = torch.device("cpu")

        if device == "cpu":
            mod.load_state_dict(torch.load(ckpt))
        else:
            mod = torch.nn.DataParallel(AttU_Net(3, 1))  # .cuda() 双卡推理代码
            # mod.load_state_dict({k.replace('module.', ''): v for k, v in torch.load(ckpt).items()})
            mod.load_state_dict(torch.load(ckpt, map_location=device))

        inferdata = PNEDataset(imlists, transform=x_transforms, target_transform=y_transforms)
        dataloaders = DataLoader(inferdata, batch_size=batchsize)
        mod.eval()
        retimg = []
        with torch.no_grad():
            for x in dataloaders:
                x = x.to(device)
                pre_y = mod(x).sigmoid()
                pre_y = pre_y.cpu()
                img_y = torch.squeeze(pre_y).numpy()
                # 0~1的灰度（double）扩展到0~255的RGB
                if img_y.ndim == 2:  # 2维数组，是最后一个的情况
                    pic = img_y * 255
                    retimg.append(pic)
                else:
                    for n in range(img_y.shape[0]):
                        pic = img_y[n] * 255
                        retimg.append(pic)
        return retimg

    def postprocess(self, infermasks):
        retarray = []
        for mask in infermasks:
            # mask 二值化
            mask[mask < 100] = 0
            mask[mask >= 100] = 255
            # Mask 用于 floodFill，官方要求长宽+2
            im_floodfill = mask.copy()  # 要赋值一份
            h, w = mask.shape[:2]
            # image = np.zeros((h + 2, w + 2), np.uint8)
            image = np.zeros((h + 2, w + 2), np.uint8)
            # 得到im_floodfill 255填充非孔洞值
            cv2.floodFill(im_floodfill, image, (0, 0), 255)
            # 得到im_floodfill的逆im_floodfill_inv
            im_floodfill_inv = cv2.bitwise_not(im_floodfill)
            # 把im_in、im_floodfill_inv这两幅图像结合起来得到前景
            im_out = mask.astype(int) | im_floodfill_inv.astype(int)
            rgbarray = self.changecolor(im_out)
            retarray.append(rgbarray)
        return retarray

    def changecolor(self, imgarray):
        img = np.uint8(imgarray)  # 推理出来是浮点型，转整形
        image = imageto3(img)
        image[:, :, 0] = 0  # CV2是B,G,R格式
        image[:, :, 1] = 0  # 只留下R即为红色
        return image

    def getothers(self, masks):
        '''
        气胸的需要计算体积和肺压缩比。
        :param masks:
        :param imps:
        :param thick:
        :return:
        '''
        volume = 0
        for m in masks:
            image = cv2.cvtColor(m, cv2.COLOR_RGB2GRAY)
            _, th3 = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            notzero = cv2.countNonZero(th3)  # 直接统计非零点的个数
            volume += (notzero * self.imps[0] * self.imps[1] * self.thick)  # 求和
            # 把mask变成红色 255是白色
        return volume, (volume / self.feiyevol) * 100

