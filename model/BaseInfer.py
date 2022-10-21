'''
推理逻辑的基类
'''


class BaseInfer():
    def __init__(self, img_data, model_data, imps="", thick=""):
        self.img_data = img_data
        self.model_data = model_data
        # self.infermask = self.infer()  # 推理得到初始mask
        # self.mask = self.postprocess(self.infermask)  # 后处理得到真正mask
        # self.getvolume(self.mask, imps, thick)  # 计算体积,或者评分

    def infer(self):
        '''
        推理
        :param img_data: 图像数据
        :param model_data: 模型数据
        :return:
        '''
        pass

    def postprocess(self, infermasks):
        '''
        后处理
        :param infermasks: 推理出的mask
        :return:
        '''
        pass

    def getvolume(self, masks, imps, thick):
        '''
        统计体积，需要像素间距和层厚
        :param masks: 分割好的图像
        :param imps: 原图像的像素间距
        :param thick: 原图像层厚
        :return:
        '''
        pass
