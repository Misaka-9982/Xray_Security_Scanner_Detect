from PyQt5.QtCore import QObject, QThread, pyqtSignal
from UI import *


class DetectCore(QObject):
    # 预留给自定义信号
    def __init__(self):
        super(DetectCore, self).__init__()
        # 绑定槽函数
        pass

