from model.Base.BasePostprocess import BasePostprocess


class RCCPostprocess(BasePostprocess):

    def printmsg(self, widget, ret):
        retvol = ret[0]
        retper = ret[1]
        widget.printolog("肾肿瘤计算为：" + str(round(retvol / 1000, 4)) + "ml")
        # 需要计算肾肿瘤
