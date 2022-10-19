import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow  # QtWidgets是Qt中最基础的类

from view.MainGui import MainGui

if __name__ == "__main__":
    app = QApplication(sys.argv)  # 1.创建整体的app
    icon = QIcon("resouces/icons/app.ico")
    # app.setWindowIcon(icon)  # 设置一个icon
    mainwindow = QMainWindow()
    mainwindow.setWindowIcon(icon)
    m = MainGui(mainwindow)
    mainwindow.show()  # 5.show出来
    sys.exit(app.exec_())  # 6.退出按钮会使app整个退出
