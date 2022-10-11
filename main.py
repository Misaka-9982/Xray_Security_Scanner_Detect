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
        # 绑定槽函数
        ui.imgDetectButton.clicked.connect(self.imgdetect)

    def getfile(self):
        name = QFileDialog.getOpenFileName()
        if len(name[0]):
            return name[0]
        else:
            pass

    def imgdetect(self):  # 将来增加模型选择功能
        detect.run(weights='yolov5s.pt', source=self.getfile())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Mainwindow = QMainWindow()

    ui = UI.ui_1.Ui_MainWindow()
    ui.setupUi(Mainwindow)

    core = DetectCore()
    Mainwindow.show()
    sys.exit(app.exec())
