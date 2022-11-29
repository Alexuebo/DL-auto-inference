from model.Base.BasePostprocess import BasePostprocess


class RCCPostprocess(BasePostprocess):

    # 需要计算肾肿瘤体积,肿瘤评分
    def printmsg(self, widget, ret):
        vol = ret[0]
        soc = ret[1]
        T = ret[2]
        widget.printolog("肾肿瘤体积计算为：" + str(vol) + "ml")
        widget.printolog("RENAL评分为：" + str(soc))
        widget.printolog("T分期为：" + str(T))
