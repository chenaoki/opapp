# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtWidgets import QLineEdit, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class OpappPlotLayout(QVBoxLayout):
    
    def __init__(self):
        
        super(OpappPlotLayout, self).__init__()
        
        self.start = 0
        self.end = 1
        self.filter = 1
        self.pos_x = 0
        self.pos_y = 0
        self.vmin = -1
        self.vmax = 1
        self.obj = None
        
        self.edit_start = QLineEdit()
        self.edit_start.setText(str(self.start))
        self.edit_start.textChanged.connect(self.draw)
        
        self.edit_end = QLineEdit()
        self.edit_end.setText(str(self.end))
        self.edit_end.textChanged.connect(self.draw)
        
        self.edit_filter = QLineEdit()
        self.edit_filter.setText(str(self.filter))
        self.edit_filter.textChanged.connect(self.draw)

        self.edit_pos_x = QLineEdit()
        self.edit_pos_x.setText(str(self.pos_x))
        self.edit_pos_x.textChanged.connect(self.draw)

        self.edit_pos_y = QLineEdit()
        self.edit_pos_y.setText(str(self.pos_y))
        self.edit_pos_y.textChanged.connect(self.draw)
        
        layout = QHBoxLayout()
        layout.addWidget(QLabel(u'start'))
        layout.addWidget(self.edit_start)
        layout.addWidget(QLabel(u'end'))
        layout.addWidget(self.edit_end)
        layout.addWidget(QLabel(u'filter'))
        layout.addWidget(self.edit_filter)
        layout.addWidget(QLabel(u'pos_x'))
        layout.addWidget(self.edit_pos_x)
        layout.addWidget(QLabel(u'pos_y'))
        layout.addWidget(self.edit_pos_y)
        self.addLayout(layout)
                
        self.figure = plt.figure()
        self.axes = plt.axes()
        self.canvas = FigureCanvas(self.figure)
        
        self.addWidget(self.canvas)
                
        try:
            self.loadPath()
        except:
            pass
        
    def setObject(self, obj):
        self.obj = obj
        self.vmax = obj.vmax
        self.vmin = obj.vmin
        if obj is None: return
        if len(self.obj.data) > 0:
            L, H, W = obj.data.shape
            self.edit_pos_y.setText(str(H//2))
            self.edit_pos_x.setText(str(H//2))
            self.edit_start.setText(str(0))
            self.edit_end.setText(str(L))
            #self.plot.set_data(t, ts)
            #self.plot, = self.axes.plot([], [])
            self.draw()
         
    def calc_APD70(self, ts):
        apd_start = 0; apd_end = 0
        threshold = 0.7*ts.min()+0.3*ts.max()
        flg = 0
        for i, v in enumerate(ts):
            if i == 0 : continue
            if v > threshold and flg == 0:
                flg = 1
                apd_start = i
            if v <= threshold and flg == 1:
                flg = 2
                apd_end = i
        return threshold, apd_start, apd_end
    
    def draw(self):
        self.axes.clear()
        self.start = int(self.edit_start.text())
        self.end = int(self.edit_end.text())
        self.filter = int(self.edit_filter.text())
        self.pos_x = int(self.edit_pos_x.text())
        self.pos_y = int(self.edit_pos_y.text())
        #try:
        ts = self.obj.data[self.start:self.end, self.pos_y, self.pos_x]
        t = np.arange(self.start, self.end)
        if self.filter>1:
            ts = gaussian_filter1d(ts, sigma = self.filter, )
        
        self.axes.set_xlim(self.start, self.end)
        #self.axes.set_ylim(self.vmin, self.vmax)
        self.axes.set_ylim(ts.min(), ts.max())
        #self.plot.set_data(t, ts)
        self.plot = self.axes.plot(t, ts)

        threshold, apd_start, apd_end = self.calc_APD70(ts)
        self.axes.hlines(threshold, self.start+apd_start, self.start+apd_end, "blue", linestyles="dashed")
        self.axes.text(self.start+(0.7*apd_start+0.3*apd_end), threshold+(ts.max()-ts.min())*0.1, "APD70: %s (ms)" % (apd_end - apd_start), fontsize=20)
        
        self.canvas.draw()
        
        pass
        #except:
        #    print("error:", sys.exc_info()[0])
        #    pass
        
        
if __name__ == '__main__':
    
    class SampleData(object):
        def __init__(self):
            self.data = np.zeros((100, 10, 10))
            for i in range(10):
                for j in range(10):
                    offset = (j-i)*np.pi/10
                    self.data[:,i,j] = np.sin(np.arange(-np.pi, np.pi, 2*np.pi/100)+offset)
    
    app = QApplication(sys.argv)
    class TempWidget(QWidget):        
        def __init__(self):
            super(TempWidget, self).__init__()
            self.player = OpappPlotLayout()
            self.setLayout(self.player)
            self.player.setObject(SampleData())
            self.show()    
    a = TempWidget()
    #sys.exit(app.exec_())
    app.exec_()
