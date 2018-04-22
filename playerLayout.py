# -*- coding: utf-8 -*-

import sys, glob, os
import cv2

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtWidgets import QLineEdit, QLabel
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QErrorMessage, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class OpappPlayerLayout(QVBoxLayout):
    
    def __init__(self, ext='png', figsize = (2,5)):
        
        super(OpappPlayerLayout, self).__init__()
        
        self.ext = ext
        self.frame = 0
        self.step = 1
        
        self.edit_frame = QLineEdit()
        self.edit_frame.setText(str(self.frame))
        self.edit_frame.textChanged.connect(self.changeFrame)
        
        self.edit_step = QLineEdit()
        self.edit_step.setText(str(self.step))
        self.edit_step.textChanged.connect(self.changeStep)
        
        self.btn_back = QPushButton(u'<')
        self.btn_next = QPushButton(u'>')
        self.btn_play = QPushButton(u'play')
        self.btn_pause = QPushButton(u'pause')
        self.btn_stop = QPushButton(u'stop')
        self.btn_back.clicked.connect(self.goBack)
        self.btn_next.clicked.connect(self.goNext)
        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)
        
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(60)
        
        layout = QHBoxLayout()
        layout.addWidget(self.edit_frame)
        layout.addWidget(self.btn_back)
        layout.addWidget(self.edit_step)
        layout.addWidget(self.btn_next)
        self.addLayout(layout)
                
        self.figure = plt.figure(figsize=figsize)
        self.axes = plt.axes()
        self.canvas = FigureCanvas(self.figure)
        self.addWidget(self.canvas)
        
        layout = QHBoxLayout()
        layout.addWidget(self.btn_play)
        layout.addWidget(self.btn_pause)
        layout.addWidget(self.btn_stop)
        self.addLayout(layout)
        
        try:
            self.loadPath()
        except:
            pass
        
    def setPath(self, path):
        self.path = path
        self.files = sorted( glob.glob(os.path.join(self.path, '*.'+self.ext)) )
        if len(self.files) > 0:
            img = cv2.imread(self.files[0])
            self.im = self.axes.imshow(img)
            self.changeFrame()
         
    def changeFrame(self):
        f_ = self.frame
        try:
            self.frame = int(self.edit_frame.text())
            img = cv2.imread(self.files[self.frame])
            self.im.set_data(img)
            self.canvas.draw()
            pass
        except:
            print("error:", sys.exc_info()[0])
            self.timer.stop()
            self.frame = f_
            self.edit_frame.setText(str(f_))
            pass
        
    def changeStep(self):
        s_ = self.step
        try:
            self.step = int(self.edit_step.text())
        except:
            print("error:", sys.exc_info()[0])
            self.step = s_
            self.edit_step.setText(str(s_))
            
    def goNext(self):
        self.edit_frame.setText(str(self.frame + self.step))
        self.changeFrame()
        
    def goBack(self):
        self.edit_frame.setText(str(self.frame - self.step))
        self.changeFrame()
        
    def play(self):
        del(self.timer)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(60)
        self.timer.timeout.connect(self.goNext)
        self.timer.start( max(len(self.files) - self.frame, 0))
        
    def pause(self):
        self.timer.stop()
        
    def stop(self):
        self.timer.stop()
        self.edit_frame.setText(u'0')
        self.changeFrame()
                
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    class TempWidget(QWidget):        
        def __init__(self):
            super(TempWidget, self).__init__()
            self.player = OpappPlayerLayout()
            self.setLayout(self.player)
            self.player.setPath('./sample')
            self.show()    
    a = TempWidget()
    #sys.exit(app.exec_())
    app.exec_()
