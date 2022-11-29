from model.Base.BaseInfer import BaseInfer

'''
 CT腹膜后淋巴结推理类，后续再说
'''


class RLInfer(BaseInfer):
    def __init__(self, img_data, model_data, imps="", thick=""):
        super().__init__(img_data, model_data)
        self.imps = imps  # 像素间距 CT图像特有的
        self.thick = thick  # 层厚

    def preprocess(self, ):
        pass

    def infer(self):
        pass

    def postprocess(self, infermasks):
        pass

    def getothers(self, masks):
        # 计算肿瘤体积，最大半径，T分期，Renal评分等
        pass
