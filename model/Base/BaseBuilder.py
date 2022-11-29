'''
建造者模式的Builder，用于构造各种具体的推理逻辑类
'''
from model.CT_PNE.PneInfer import PneInfer
from model.CT_PNE.PnePostprocess import PnePostprocess
from model.CT_Renal.RCCInfer import RCCInfer
from model.CT_Renal.RCCPostprocess import RCCPostprocess

classtype = {"CT气胸": "PneInfer",
             "CT肾肿瘤": "RCCInfer"}


class BaseBuilder:

    def __init__(self, typename=""):
        self.typename = typename

    def settypename(self, typename):
        if typename in classtype:
            self.typename = typename
        else:
            return -1

    # todo 有没有设计模式能根据用户输入自动创建对象的。。是不是到最后还是要写if判断？
    def buildinfer(self, img_data, model_data):
        clazz = classtype.get(self.typename)
        if clazz == "PneInfer":
            return PneInfer(img_data, model_data)
        elif clazz == "RCCInfer":
            return RCCInfer(img_data, model_data)

    def buildpost(self):
        clazz = classtype.get(self.typename)
        if clazz == "PneInfer":
            return PnePostprocess()
        elif clazz == "RCCInfer":
            return RCCPostprocess()
