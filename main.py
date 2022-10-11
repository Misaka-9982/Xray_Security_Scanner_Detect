import sys

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow, QApplication

import UI.ui_1
import UI.ui_2
import UI.ui_3
import UI.ui_4
import detect


class DetectCore(QObject):
    # 预留给自定义信号

    def __init__(self):
        super(DetectCore, self).__init__()

    def getfile(self):
        name = QFileDialog.getOpenFileName()
        if len(name[0]):
            return name[0]
        else:
            pass

    def imgdetect(self):  # 将来增加模型选择功能
        detect.run(weights='yolov5s.pt', source=self.getfile())


class UI_init(QObject):
    # 预留给自定义信号

    def __init__(self):
        super(UI_init, self).__init__()
        # 绑定槽函数
        ui1.imgDetectButton.clicked.connect(self.initui2)

    def initui2(self):
        Mainwindow2 = QMainWindow()
        ui2 = UI.ui_2.Ui_MainWindow()
        ui2.setupUi(Mainwindow2)
        Mainwindow2.show()





if __name__ == '__main__':
    app = QApplication(sys.argv)
    Mainwindow1 = QMainWindow()

    ui1 = UI.ui_1.Ui_MainWindow()
    ui1.setupUi(Mainwindow1)

    UI_init()
    Mainwindow1.show()
    sys.exit(app.exec())
