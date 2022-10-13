import sys
import threading
import queue

import cv2
from PIL import Image, ImageQt
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPixmap, QImageReader, QImage

import UI.ui_1
import UI.ui_2
import UI.ui_3
import UI.ui_4
import detect


class UI_init(QObject):
    # 预留给自定义信号

    def __init__(self):
        super(UI_init, self).__init__()
        # 实例化UI刷新类
        self.uiupdate = UiUpdate()
        # 绑定槽函数
        self.initui1()

    # 把UI 的返回键去掉，不做返回功能了
    def initui1(self):
        ui1.imgDetectButton.clicked.connect(self.initui2)
        ui1.videoDetectButton.clicked.connect(self.initui3)
        ui1.cameraDetectButton.clicked.connect(self.initui4)

    def initui2(self):
        self.ui2 = UI.ui_2.Ui_MainWindow()
        self.ui2.setupUi(Mainwindow)
        Mainwindow.show()
        self.ui2.selectImageButton.clicked.connect(core.imgdetect)

    def initui3(self):
        self.ui3 = UI.ui_3.Ui_MainWindow()
        self.ui3.setupUi(Mainwindow)
        Mainwindow.show()
        self.ui3.selectVideoButton.clicked.connect(core.viddetect)

    def initui4(self):
        self.ui4 = UI.ui_4.Ui_MainWindow()
        self.ui4.setupUi(Mainwindow)
        Mainwindow.show()
        self.ui4.selectCameraButton.clicked.connect(core.camdetect)


class DetectCore(QObject):
    # 预留给自定义信号

    def __init__(self):
        super(DetectCore, self).__init__()
        self.runcore = detect.RunCore()
        # 信号在RunCore中定义  绑定信号要用RunCore的实例对象来绑定，不能绑定到类上
        # uiupdate在uiinit类的构造函数中初始化
        self.runcore.imgresultsignal.connect(uiinit.uiupdate.ui2update)
        self.runcore.vidresultsignal.connect(uiinit.uiupdate.ui3update)
        # self.runcore.camresultsignal.connect(uiinit.uiupdate.ui4update)

    def imgdetect(self):  # 将来增加模型选择功能  # 是否保存识别后图片文件功能
        name = QFileDialog.getOpenFileName(caption='选择要识别的图片', filter='Images (*.bmp *.dng, *.jpeg *.jpg *.mpo *.png '
                                                                      '*.tif *.tiff *.webp')
        if len(name[0]):    # 记得改权重为训练后的新权重
            uiinit.ui2.detectResultListImg.clear()  # 开始图片检测前清空原有记录
            runthread = threading.Thread(target=self.runcore.run, daemon=True, kwargs={'weights': 'yolov5s.pt', 'source': name[0]})
            runthread.start()
        else:
            pass

    def viddetect(self):
        name = QFileDialog.getOpenFileName(caption='选择要识别的视频', filter='Videos (*.asf *.avi *.gif *.m4v *.mkv *.mov '
                                                                      '*.mp4 *.mpeg *.mpg *.ts *.wmv')
        if len(name[0]):
            uiinit.ui3.detectResultListVid.clear()
            runthread = threading.Thread(target=self.runcore.run, daemon=True, kwargs={'weights': 'yolov5s.pt', 'source': name[0], 'nosave': True})
            runthread.start()
        else:
            pass

    def camdetect(self):
        pass


class UiUpdate(QObject):
    def __init__(self):
        super(UiUpdate, self).__init__()
        self.fps = 0
        self.w = 0
        self.h = 0
        self.timer = QTimer()   # 定义计时器
        self.framebuffer = queue.Queue()

    def ui2update(self, signal):
        # 后面根据可能概率换为QTabelWidget来显示颜色等级
        if isinstance(signal[0], str):  # 标签名
            uiinit.ui2.detectResultListImg.addItem(QListWidgetItem(signal[0]))
        elif isinstance(signal[0], np.ndarray):  # 图片和路径
            uiinit.ui2.imageLabel.setPixmap(QPixmap(signal[1]))  # 图片文件路径
        else:
            raise Exception('未知错误')

    def ui3update(self, signal):
        def vidstart():
            if not self.timer.isActive():
                self.timer.timeout.connect(self.vidframeupdate)
                self.timer.start(100)   # 100ms  不能小于帧生成时间
            else:
                pass

        # 视频结束或按下停止时调用  注意按下停止时还要停止后台检测线程
        def vidstop():
            self.timer.stop()

        if isinstance(signal[0], str) and signal[0] == 'start':
            vidstart()
        elif isinstance(signal[0], np.ndarray):
            self.framebuffer.put(signal[0], block=False)
        elif isinstance(signal[0], str) and signal[0] == 'finished':
            self.framebuffer.put('finished')
        else:   # 仅为了调用vidstop函数传任意参数时
            return vidstop  # 停止时间需要以播放速度为准，返回出stop函数用于外部调用

    def vidframeupdate(self):
        try:   # 如果播放速率大于识别速率会报队列空exception
            t_frame = self.framebuffer.get(block=False)
            if not isinstance(t_frame, str):   # t_frame不是结束字符串即为一帧
                frame = cv2.cvtColor(t_frame, cv2.COLOR_BGR2RGB)
                height, width, bytesPerComponent = frame.shape
                bytesPerLine = bytesPerComponent * width
                qimage = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
                uiinit.ui3.videoLabel.setPixmap(QPixmap.fromImage(qimage))
            else:   # 队列空 且已经识别完毕，不是等待识别状态
                vidstopfunc = self.ui3update([None])  # 参数无意义，只是为了返回stop函数
                vidstopfunc()
        except queue.Empty:
            pass




def ui4update(self, signal):
        pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    Mainwindow = QMainWindow()

    ui1 = UI.ui_1.Ui_MainWindow()
    ui1.setupUi(Mainwindow)

    uiinit = UI_init()   # 此处实例化UI_init必须要将实例赋值给一个变量，否则构造函数初始化的信号连接将会被回收/中断
    core = DetectCore()

    Mainwindow.show()
    sys.exit(app.exec())
