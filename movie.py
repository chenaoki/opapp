# -*- coding: utf-8 -*-

import os,glob,sys,cv2

def makeMovie(path = None):
    imgs= sorted(glob.glob(os.path.join(path,"*.png")))
    fourcc = cv2.VideoWriter_fourcc("m","p","4","v")
    ref = cv2.imread(imgs[0],cv2.IMREAD_COLOR)
    img_h,img_w,channels = ref.shape[:3]
    video = cv2.VideoWriter(path+".mp4",fourcc,20.0,(img_w,img_h))
    for i,img_path in enumerate(imgs):
        img = cv2.imread(img_path)
        video.write(img)
    video.release()
