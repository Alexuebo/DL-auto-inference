from abc import ABCMeta, abstractmethod

'''
后处理基类，一般只用输出就行了
'''


class BasePostprocess(metaclass=ABCMeta):

    @abstractmethod
    def printmsg(self, widget, ret):
        pass
