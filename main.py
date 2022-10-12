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

    def imgdetect(self):  # 将来增加模型选择功能  # 是否保存识别后图片文件功能
        name = QFileDialog.getOpenFileName(caption='选择要识别的图片', filter='Images (*.bmp *.dng, *.jpeg *.jpg *.mpo *.png '
                                                                      '*.tif *.tiff *.webp')
        if len(name[0]):    # 记得改权重为训练后的新权重
            detect.RunCore.run(weights='yolov5s.pt', source=name[0])
        else:
            pass

    def viddetect(self):
        name = QFileDialog.getOpenFileName(caption='选择要识别的视频', filter='Videos (*.asf *.avi *.gif *.m4v *.mkv *.mov '
                                                                      '*.mp4 *.mpeg *.mpg *.ts *.wmv')
        if len(name[0]):
            detect.RunCore.run(weights='yolov5s.pt', source=name[0])
        else:
            pass

    def camdetect(self):
        pass


class UI_init(QObject):
    # 预留给自定义信号

    def __init__(self):
        super(UI_init, self).__init__()
        # 绑定槽函数
        self.initui1()

    # 把UI 的返回键去掉，不做返回功能了
    def initui1(self):
        ui1.imgDetectButton.clicked.connect(self.initui2)
        ui1.videoDetectButton.clicked.connect(self.initui3)
        ui1.cameraDetectButton.clicked.connect(self.initui4)

    def initui2(self):
        ui2 = UI.ui_2.Ui_MainWindow()
        ui2.setupUi(Mainwindow)
        Mainwindow.show()
        ui2.selectImageButton.clicked.connect(core.imgdetect)

    def initui3(self):
        ui3 = UI.ui_3.Ui_MainWindow()
        ui3.setupUi(Mainwindow)
        Mainwindow.show()
        ui3.selectVideoButton.clicked.connect(core.viddetect)

    def initui4(self):
        ui4 = UI.ui_4.Ui_MainWindow()
        ui4.setupUi(Mainwindow)
        Mainwindow.show()
        ui4.selectCameraButton.clicked.connect(core.camdetect)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    Mainwindow = QMainWindow()

    ui1 = UI.ui_1.Ui_MainWindow()
    ui1.setupUi(Mainwindow)

    ui = UI_init()   # 此处实例化UI_init必须要将实例赋值给一个变量，否则构造函数初始化的信号连接将会被回收/中断
    core = DetectCore()
    Mainwindow.show()
    sys.exit(app.exec())
