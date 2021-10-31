# -*- coding:utf-8 -*-
## qt5
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QImage, QPalette, QPixmap
# 追加したimport
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
from PyQt5.QtCore import Qt

import sys 
import time
from time import sleep

class Window(QMainWindow): 
  
    def __init__(self): 
        super().__init__() 

        #app = QApplication([])
        # ファイルを読み込み
        #self.image = QImage(1000, 1000, QImage.Format_ARGB32)     #500*500ピクセルの画像を作成
        #self.image = QImage("/Users/seigo/Downloads/20211031.png")
        self.image = QImage("/Users/seigo/Downloads/20211031_3.png") # 事前に1440*900などのサイズにリサイズしておくと後処理が楽

        self.window = QWidget()
        self.window.setWindowTitle('Image View')
        self.window.setFixedSize(self.image.width(), self.image.height())
        self.setFixedSize(self.image.width(), self.image.height())

        self.painter = QPainter()
        self.imageLabel = QLabel()
        self.layout = QVBoxLayout()

        # creating a timer object 
        self.TimerUpdate_mSec = 200
        self.TimerUpdate_cnt = 0
        timer = QTimer(self) 
        timer.timeout.connect(self.callback_draw)
        timer.start(self.TimerUpdate_mSec)

    # timer callback function 
    def callback_draw(self):

        # -----
        # 加工したいイメージを渡して編集開始
        self.painter.begin(self.image)
        # 塗りつぶし範囲指定
        img_width  = self.image.width()
        img_height = self.image.height()
        x_size = img_width/10  #100
        y_size = img_height/10 #100
        x_pos  = int(self.TimerUpdate_cnt * x_size % img_width)
        y_pos  = int(self.TimerUpdate_cnt * x_size / img_width) * y_size
        print(str(x_pos) + " " + str(y_pos))
        self.painter.fillRect(x_pos, y_pos, x_size, y_size, Qt.black)
        self.painter.end()
        # -----

        # ラベルに読み込んだ画像を反映
        self.imageLabel.setPixmap(QPixmap.fromImage(self.image))
        # スケールは1.0
        #self.imageLabel.scaleFactor = 1.0

        self.layout.addWidget(self.imageLabel)

        self.window.setFixedSize(self.image.width(), self.image.height())
        self.window.resize(self.image.width(), self.image.height())
        self.window.setLayout(self.layout)
        #self.resize(self.image.width(), self.image.height())
        #self.setFixedSize(self.image.width(), self.image.height())
        #print(window.frameSize())
        #self.window.show()
        self.window.showFullScreen()
        #self.window.showMaximized()
        #self.window.showNormal()
        #app.exec_()

        self.TimerUpdate_cnt += 1
        if self.TimerUpdate_cnt > (img_width/100)*(img_height/100):
            time.sleep(self.TimerUpdate_mSec*0.001)
            sys.exit(0)

if __name__ == '__main__':
    # create pyqt5 app 
    app = QApplication(sys.argv)   
    # create the instance of our Window 
    window = Window() 
    # start the app 
    sys.exit(app.exec()) 
