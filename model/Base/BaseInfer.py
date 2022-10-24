'''
推理逻辑的基类
'''
from abc import ABCMeta, abstractmethod


class BaseInfer(metaclass=ABCMeta):
    def __init__(self, img_data, model_data):
        self.img_data = img_data  # 数据
        self.model_data = model_data  # 模型

    @abstractmethod
    def preprocess(self):
        '''
        推理前预处理
        :return:
        '''
        pass

    @abstractmethod
    def infer(self):
        '''
        推理过程
        :return:
        '''
        pass

    @abstractmethod
    def postprocess(self, infermasks):
        '''
        后处理，空洞填充之类的
        :param infermasks: 推理出的mask
        :return:
        '''
        pass

    @abstractmethod
    def getothers(self, masks):
        '''
        计算其他后续的运算，如体积,压缩比等，体积需要像素间距和层厚
        :param masks: 分割好的图像
        :return:
        '''
        pass
