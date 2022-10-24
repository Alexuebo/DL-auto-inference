from model.Base.BasePostprocess import BasePostprocess


class PnePostprocess(BasePostprocess):

    def printmsg(self, widget, ret):
        retvol = ret[0]
        retper = ret[1]
        widget.printolog("气胸体积计算为：" + str(round(retvol / 1000, 4)) + "ml")
        widget.printolog("肺压缩比为：" + str(round(retper, 2)) + "%")
