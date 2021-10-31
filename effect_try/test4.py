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
        #super().__init__() 
        super(QMainWindow, self).__init__()
        
        #app = QApplication([])
        # ファイルを読み込み
        #self.image = QImage(1000, 1000, QImage.Format_ARGB32)     #500*500ピクセルの画像を作成
        #self.image = QImage("/Users/seigo/Downloads/20211031.png")
        #self.image = QImage("/home/ubuntu/Downloads/20211031.png") # 事前に任意のサイズにリサイズしておくと後処理が楽
        self.image = QImage("./test.png")
        # 事前に任意のサイズにリサイズしておくと後処理が楽
        # gnome-screenshot -f test.png などでキャプチャ
        
        self.window = QWidget()
        self.window.setWindowTitle('Image View')
        self.window.setFixedSize(self.image.width(), self.image.height())
        self.setFixedSize(self.image.width(), self.image.height())

        self.painter = QPainter()
        self.imageLabel = QLabel()
        self.layout = QVBoxLayout()

        # creating a timer object 
        self.TimerUpdate_mSec = 15
        self.TimerUpdate_cnt = 0
        self.TimerUpdate_cnt_step = 0        
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
        block_ratio = 13 #10
        x_size = img_width/block_ratio  #100
        y_size = img_height/block_ratio  #100

        ## 0
        current_position=int(self.TimerUpdate_cnt_step%4) #0,1,2,3
        loop_cnt=int(self.TimerUpdate_cnt_step/4)
        #print(str(current_position)+" "+str(loop_cnt))

        if current_position == 0:
            x_pos  = int((self.TimerUpdate_cnt+loop_cnt) * x_size % img_width)
            y_pos  = int(loop_cnt * y_size % img_height)
            #y_pos  = int(self.TimerUpdate_cnt * x_size / img_width) * y_size
            if self.TimerUpdate_cnt >= block_ratio-1-loop_cnt:
                self.TimerUpdate_cnt = 0
                self.TimerUpdate_cnt_step += 1
            self.TimerUpdate_cnt += 1

        ## 1
        elif current_position == 1:
            x_pos  = int((block_ratio-1-loop_cnt) * x_size % img_width)
            y_pos  = int((self.TimerUpdate_cnt+loop_cnt) * y_size % img_height)
            if self.TimerUpdate_cnt >= block_ratio-1-loop_cnt+1:
                self.TimerUpdate_cnt = 0
                self.TimerUpdate_cnt_step += 1
            self.TimerUpdate_cnt += 1

        ## 2
        elif current_position == 2:
            x_pos  = int((block_ratio-1-self.TimerUpdate_cnt-loop_cnt) * x_size % img_width)
            y_pos  = int((block_ratio-1-loop_cnt) * y_size % img_height)
            if (block_ratio-1-self.TimerUpdate_cnt <= loop_cnt):
                self.TimerUpdate_cnt = 0
                self.TimerUpdate_cnt_step += 1
            self.TimerUpdate_cnt += 1

        ## 3
        elif current_position == 3:
            x_pos  = int(loop_cnt * x_size % img_width)
            y_pos  = int((block_ratio-1-self.TimerUpdate_cnt-loop_cnt) * y_size % img_height)
            if (block_ratio-1-self.TimerUpdate_cnt <= loop_cnt+1):
                self.TimerUpdate_cnt = 0
                self.TimerUpdate_cnt_step += 1
            else:
                self.TimerUpdate_cnt += 1

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

        #self.TimerUpdate_cnt += 1
        if self.TimerUpdate_cnt_step >= 25:
            print("end")
            time.sleep(self.TimerUpdate_mSec*0.001/4)
            sys.exit(0)

if __name__ == '__main__':
    # create pyqt5 app 
    app = QApplication(sys.argv)   
    # create the instance of our Window 
    window = Window() 
    # start the app 
    sys.exit(app.exec()) 
