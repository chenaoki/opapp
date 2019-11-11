# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QWidget, QApplication

from PyQt5 import QtCore

from playerLayout import OpappPlayerLayout

import cupy as xp

class OpappObjectPlayerLayout(OpappPlayerLayout):
    
    def __init__(self):
        super(OpappObjectPlayerLayout, self).__init__()
        self.obj = None

    def setObject(self, obj):
        self.obj = obj
        if obj is None: return
        assert len(self.obj.data) > 0
        self.im = self.axes.imshow(
                xp.asnumpy(obj.data[self.frame, :, :]), 
                vmin=obj.vmin, vmax=obj.vmax, cmap=obj.cmap)
        self.changeFrame()
         
    def changeFrame(self):
        f_ = self.frame
        try:
            assert self.obj is not None
            self.frame = int(self.edit_frame.text())
            self.im.set_data( xp.asnumpy( self.obj.data[self.frame,:,:]))
            self.canvas.draw()
            pass
        except:
            print("error:", sys.exc_info()[0])
            self.timer.stop()
            self.frame = f_
            self.edit_frame.setText(str(f_))
            pass
        
    def play(self):
        del(self.timer)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(60) #The max FPS is limited to around 25 (interval = 40)
        self.timer.timeout.connect(self.goNext)
        self.timer.start()

                        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    class TempWidget(QWidget):        
        def __init__(self):
            super(TempWidget, self).__init__()
            self.player = OpappObjectPlayerLayout()
            self.setLayout(self.player)
            self.show()    
    a = TempWidget()
    #sys.exit(app.exec_())
    app.exec_()
