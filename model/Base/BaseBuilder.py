'''
建造者模式的Builder
'''
from model.CT_PNE.PneInfer import PneInfer
from model.CT_PNE.PnePostprocess import PnePostprocess
from model.CT_Renal.RCCInfer import RCCInfer
from model.CT_Renal.RCCPostprocess import RCCPostprocess
from utils.tools import alertmsg

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
