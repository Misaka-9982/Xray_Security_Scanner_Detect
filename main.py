import sys
import threading
import queue

import cv2
from PIL import Image, ImageQt
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import *
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
        vidstop = self.uiupdate.ui3update([None])  # 参数无意义，只是为了返回vidstop函数
        self.ui3.stopvidButton.clicked.connect(vidstop)

    def initui4(self):
        self.ui4 = UI.ui_4.Ui_MainWindow()
        self.ui4.setupUi(Mainwindow)
        Mainwindow.show()
        self.ui4.selectCameraButton.clicked.connect(core.camdetect)


class DetectCore(QWidget):  # 为了messagebox继承自QWidget
    # 预留给自定义信号

    def __init__(self):
        super(DetectCore, self).__init__()
        self.runcore = detect.RunCore()
        # 信号在RunCore中定义  绑定信号要用RunCore的实例对象来绑定，不能绑定到类上
        # uiupdate在uiinit类的构造函数中初始化
        self.runcore.imgresultsignal.connect(uiinit.uiupdate.ui2update)
        self.runcore.vidresultsignal.connect(uiinit.uiupdate.ui3update)
        # self.runcore.camresultsignal.connect(uiinit.uiupdate.ui4update)

        self.name = [None] * 2   # 文件名

        # 检测线程  # 为了后续对线程的控制，必须定义在这里作为实例变量
        self.runthread = threading.Thread(target=self.runcore.run, daemon=True, kwargs={'weights': 'yolov5s.pt', 'source': self.name[0], 'nosave': True})

    def imgdetect(self):  # 将来增加模型选择功能  # 是否保存识别后图片文件功能
        if not self.runcore.runstatus and not uiinit.uiupdate.timer.isActive():
            self.name = QFileDialog.getOpenFileName(caption='选择要识别的图片', filter='Images (*.bmp *.dng, *.jpeg *.jpg *.mpo *.png '
                                                                          '*.tif *.tiff *.webp')
            if len(self.name[0]):    # 记得改权重为训练后的新权重
                uiinit.ui2.detectResultListImg.clear()  # 开始图片检测前清空原有记录
                self.runthread = threading.Thread(target=self.runcore.run, daemon=True, kwargs={'weights': 'yolov5s.pt', 'source': self.name[0], 'nosave': True})
                self.runcore.needstop = False
                uiinit.ui2.imageLabel.setText('正在检测...请稍后')
                self.runthread.start()
            else:
                pass
        else:
            QMessageBox.warning(self, '警告', '当前有图片正在识别，请结束后再选择新图片！', QMessageBox.Ok)

    def viddetect(self):  # 后台识别线程已停止且视频播放结束
        if not self.runcore.runstatus and not uiinit.uiupdate.timer.isActive():
            self.name = QFileDialog.getOpenFileName(caption='选择要识别的视频', filter='Videos (*.asf *.avi *.gif *.m4v *.mkv *.mov '
                                                                          '*.mp4 *.mpeg *.mpg *.ts *.wmv')
            if len(self.name[0]):
                uiinit.ui3.detectResultListVid.clear()
                self.runthread = threading.Thread(target=self.runcore.run, daemon=True, kwargs={'weights': 'yolov5s.pt', 'source': self.name[0], 'nosave': True})
                self.runcore.needstop = False
                uiinit.ui3.videoLabel.setText('正在检测...请稍后')
                self.runthread.start()
            else:
                pass
        else:
            QMessageBox.warning(self, '警告', '当前有视频正在识别，请关闭后再选择新视频！', QMessageBox.Ok)

    def camdetect(self):
        pass


class UiUpdate(QWidget):
    def __init__(self):
        super(UiUpdate, self).__init__()
        self.fps = 0
        self.w = 0
        self.h = 0
        self.timer = QTimer()   # 定义计时器
        self.timer.timeout.connect(self.vidframeupdate)  # 不能在vidstart函数中绑定，否则会绑定多次，使一次timeout触发多次帧刷新导致帧速率异常
        self.framebuffer = queue.Queue()  # 识别结果缓冲区
        self.allresult = []        # 标签和置信度
        self.isslowwarn = False    # 识别速度过慢提示标签

    def ui2update(self, signal):
        # 后面根据可能概率换为QTabelWidget来显示颜色等级
        if isinstance(signal[0], list):  # 结果列表
            uiinit.ui2.detectResultListImg.clear()
            signal[0].sort(reverse=True, key=lambda x: x[1])  # 按置信度降序
            for result, conf in signal[0]:
                uiinit.ui2.detectResultListImg.addItem(QListWidgetItem(result+' - '+f'{conf:.2f}'))
        elif isinstance(signal[0], np.ndarray):  # 图片
            # 如下是从内存加载ndarray图片到Qpixmap显示在qlabel的流程  测试稳定
            frame = cv2.cvtColor(signal[0], cv2.COLOR_BGR2RGB)
            height, width, bytesPerComponent = frame.shape
            bytesPerLine = bytesPerComponent * width
            qimage = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            uiinit.ui2.imageLabel.setPixmap(QPixmap.fromImage(qimage))
        else:
            raise Exception('未知错误')

    def ui3update(self, signal):
        def vidstart():
            if not self.timer.isActive():
                self.timer.start(100)   # 100ms / 10fps  启动帧刷新计时器
                uiinit.ui3.detectResultListVid.clear()
                uiinit.ui3.videolistlabel.setText('实时结果：')
                self.allresult = []   # 清除上一次检测结果
            else:
                pass

        # 视频结束或按下停止时调用  注意按下停止时还要停止后台检测线程  清空缓冲区
        def vidstop():
            # print(self.timer.isActive() or core.runcore.runstatus or core.runthread.is_alive())
            if self.timer.isActive() or core.runcore.runstatus or core.runthread.is_alive():
                self.timer.stop()
                core.runcore.needstop = True  # 终止检测线程信号
                # 如果信号用qt信号发出，会导致异常在主线程被触发
                self.framebuffer = queue.Queue()      # 清空缓冲区
                core.runcore.runstatus = False
                uiinit.ui3.videoLabel.setText('视频播放结束')
                uiinit.ui3.detectResultListVid.clear()
                # 显示所有出现过的物品
                uiinit.ui3.videolistlabel.setText('最终结果(每类最高置信度)：')
                # 找出每类物品中最高置信度的算法
                self.allresult.sort(key=lambda x: x[0])  # 将同类标签放到一起
                t_max = 0
                t_lable = None
                endresult = []
                for result in self.allresult:
                    if t_lable == result[0] and t_max < result[1]:
                        t_max = result[1]
                    elif t_lable != result[0]:  # 不能用else，会把同类不大于的放进来
                        if t_lable is not None:
                            endresult.append([t_lable, t_max])
                        t_lable = result[0]
                        t_max = result[1]
                endresult.append([t_lable, t_max])  # endresult中t_table无重复的
                endresult.sort(reverse=True, key=lambda x: x[1])  # 出现过概率大的往前排
                try:
                    for result, conf in endresult:
                        uiinit.ui3.detectResultListVid.addItem(QListWidgetItem(result+' - '+f'{conf:.2f}'))
                except TypeError:  # 第一帧还未识别完成时就终止，result为None会导致主线程崩溃
                    pass

        # 开始信号
        if isinstance(signal[0], str) and signal[0] == 'start':
            vidstart()
        # 帧和识别结果
        elif isinstance(signal[0], np.ndarray):  # signal[0]是图片，signal[1]是所有目标标签
            self.framebuffer.put([signal[0], signal[1]], block=False)
        # 结束信号
        elif isinstance(signal[0], str) and signal[0] == 'finished':
            self.framebuffer.put('finished')
        # 仅为了调用vidstop函数传任意参数时
        else:
            return vidstop  # 停止时间需要以播放速度为准，返回出stop函数用于外部调用

    def vidframeupdate(self):   # 收到计时器timeout信号时触发
        def slowwarn():                               # 缓冲区过大问题
            QMessageBox.warning(self, '警告', '检测到您的电脑识别速度低于10fps，可能导致视频较卡顿，'
                                            '请安装显卡加速环境或使用较快的低精度模型', QMessageBox.Ok)
            self.isslowwarn = True

        try:   # 如果播放速率大于识别速率会报队列空exception
            resultdata = self.framebuffer.get(block=False)  # 从缓冲区队列读
            t_frame = resultdata[0]
            resultlist = resultdata[1]
            if not isinstance(t_frame, str):   # t_frame不是结束字符串即为一帧
                frame = cv2.cvtColor(t_frame, cv2.COLOR_BGR2RGB)
                height, width, bytesPerComponent = frame.shape
                bytesPerLine = bytesPerComponent * width
                qimage = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
                uiinit.ui3.videoLabel.setPixmap(QPixmap.fromImage(qimage))
                # 更新标签列表
                uiinit.ui3.detectResultListVid.clear()
                for result, conf in resultlist:
                    uiinit.ui3.detectResultListVid.addItem(QListWidgetItem(result+' - '+f'{conf:.2f}'))
                    # 统计最终标签列表  费时部分在stop函数执行
                    self.allresult.append([result, conf])
            else:   # 队列空 且已经识别完毕，不是等待识别状态
                vidstopfunc = self.ui3update([None])  # 参数无意义，只是为了返回stop函数
                vidstopfunc()
        except queue.Empty:
            if not self.isslowwarn and not core.runcore.needstop:
                slowwarn()







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
