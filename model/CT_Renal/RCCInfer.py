from model.Base.BaseInfer import BaseInfer


class RCCInfer(BaseInfer):
    def __init__(self, img_data, model_data):
        super().__init__(img_data, model_data)

    def preprocess(self):
        pass

    def infer(self):
        pass

    def postprocess(self, infermasks):
        pass

    def getothers(self, masks):
        pass
