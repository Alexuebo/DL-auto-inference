from abc import ABCMeta, abstractmethod


class BasePostprocess(metaclass=ABCMeta):

    @abstractmethod
    def printmsg(self, widget, ret):
        pass
