'''
使用气胸进行推理的推理类
'''
import cv2
import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import transforms

from model.BaseInfer import BaseInfer
from model.CT_PNE.AttU_Net import AttU_Net
from model.CT_PNE.PNEDataset import PNEDataset

batchsize = 4

x_transforms = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])

y_transforms = transforms.ToTensor()


class PneInfer(BaseInfer):
    def __init__(self, img_data, model_data):
        super().__init__(img_data, model_data)

    def infer(self):
        mod = AttU_Net(3, 1)
        imlists = self.img_data  # 数据
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

    def postprocess(self, mask):
        # 后处理逻辑太慢了，比推理还慢
        # for mask in infermasks:
        # image = cv2.cvtColor(np.asarray(mask), cv2.COLOR_RGB2GRAY)
        # mask 二值化
        mask[mask < 100] = 0
        mask[mask >= 100] = 255
        # np.set_printoptions(suppress=True)
        im_floodfill = mask.copy()
        # Mask 用于 floodFill，官方要求长宽+2
        h, w = mask.shape[:2]
        # image = np.zeros((h + 2, w + 2), np.uint8)
        image = np.zeros((h + 2, w + 2), np.uint8)
        # 得到im_floodfill 255填充非孔洞值
        cv2.floodFill(im_floodfill, image, (0, 0), 255)
        # 得到im_floodfill的逆im_floodfill_inv
        im_floodfill_inv = cv2.bitwise_not(im_floodfill)
        # 把im_in、im_floodfill_inv这两幅图像结合起来得到前景
        im_out = mask.astype(int) | im_floodfill_inv.astype(int)
        # 把mask变成红色 255是白色
        rgbpic = self.changecolor(im_out)
        # retmask.append(rgbpic)
        return rgbpic

    def getvolume(self, masks, imps, thick):
        volume = 0
        x, y = imps[0], imps[1]
        for m in masks:
            image = cv2.cvtColor(np.asarray(m), cv2.COLOR_RGB2GRAY)
            _, th3 = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            notzero = cv2.countNonZero(th3)  # 直接统计非零点的个数
            volume += (notzero * x * y * thick)  # 求和
        return volume

    def changecolor(self, imgarray):
        height = imgarray.shape[0]
        width = imgarray.shape[1]
        img = Image.fromarray(imgarray)
        img = img.convert('RGB')
        imary = np.asarray(img)
        dst = np.zeros((height, width, 3))
        for h in range(0, height):
            for w in range(0, width):
                (b, g, r) = imary[h, w]
                if (b, g, r) == (255, 255, 255):  # 白色mask
                    dst[h, w] = (255, 10, 10)  # RGB R大即为红色mask
        img2 = Image.fromarray(np.uint8(dst))
        return img2
