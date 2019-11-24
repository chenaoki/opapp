import sys, os, json
import numpy as np
import cupy as xp
import cv2

sys.path.append("./opmap")
from opmap.rawCam import RawCam
from opmap.vmemMap import VmemMap
from opmap.phaseMapHilbert import PhaseMapHilbert
from opmap.phaseVarianceMap import PhaseVarianceMap
from opmap.apdMap import APDMap
from movie import makeMovie

def run_opapp(json_path='./param.json', raw_path=None, result_path=None):
    
    rawcam = None
    vmem = None
    pmap = None
    pvmap = None
    
    with open(json_path, "r") as f : params = json.load(f)
    param_cam     = params.get("camera",{})
    param_menu   = params.get("menu",{})
    param_vmem    = params.get("vmem",{})
    param_pvmap   = params.get("pvmap",{})
    param_roi     = params.get("roi_rect",{})
    save_int      = param_menu.get("save_int",1)
    diff_min      = param_vmem.get("diff_min",0)
    intensity_min = param_vmem.get("intensity_min",0)
    smooth_xy     = param_vmem.get("smooth_xy_size",1)
    smooth_t      = param_vmem.get("smooth_t_size",1)
    pv_win        = param_pvmap.get("pv_win",9)


    if raw_path is not None: param_cam["path"] = raw_path
    if result_path is not None:
        saveDir = result_path
    else:
        saveDir = os.path.join(param_cam["path"], "result/opapp")
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    if param_menu["cam"] != 0 :
        print("RawCam...")
        rawcam = RawCam(**param_cam)
        print(rawcam.data.shape)
        roi_rect = {
            "top" : param_roi["top"],
            "bottom" : rawcam.data.shape[1] - 1 - param_roi["bottom"],
            "left" : param_roi["left"],
            "right" : rawcam.data.shape[2] - 1 - param_roi["right"]
        }
        rawcam.setRectROI(**roi_rect)
        if intensity_min > 0 : rawcam.setIntROI(val_min=intensity_min)
        rawcam.morphROI(closing=10)
        rawcam.morphROI(erosion=10)
        #rawcam.saveImage(saveDir+'/cam', skip=len(rawcam.data))
        #if param_menu["cam"] in [2,3] : rawcam.saveImage(saveDir+'/cam', skip=save_int)
        #if param_menu["cam"] == 3 : makeMovie(saveDir+'/cam')
        #if param_menu["cam"] == 4 : np.save(saveDir+'/cam', rawcam.data)
        print("done")
    else:
        print("Skip RawCam")

    if param_menu["vmem"] != 0 :
        print("VmemMap...")
        vmem = VmemMap(rawcam)
        if diff_min > 0 : vmem.setDiffRange(diff_min=diff_min)
        vmem.morphROI(closing=10)
        vmem.morphROI(erosion=10)
        if smooth_t > 1 : vmem.smooth_t(size=smooth_t)
        if smooth_xy > 1 : vmem.smooth_xy(size=smooth_xy)
        #if param_menu["vmem"] in [2,3] : vmem.saveImage(saveDir+'/vmem', skip=save_int)
        #if param_menu["vmem"] == 3 : makeMovie(saveDir+'/vmem')
        #if param_menu["vmem"] == 4 : np.save(saveDir+'/vmem', vmem.data)
        print("done")
    else:
        print("Skip VmemMap")

    if param_menu["pmap"] != 0 :
        print("PhaseMap...")
        pmap = PhaseMapHilbert(vmem)
        #if param_menu["pmap"] in [2,3] : pmap.saveImage(saveDir+'/pmap', skip=save_int)
        #if param_menu["pmap"] == 3 : makeMovie(saveDir+'/pmap')
        #if param_menu["pmap"] == 4 : np.save(saveDir+'/pmap', pmap.data)
        print("done")
    else:
        print("Skip PhaseMap")

    if param_menu["pvmap"] != 0 :
        print("PhaseVarianceMap...")
        #pmap.smooth(9)
        pvmap = PhaseVarianceMap(pmap, size=pv_win)
        #if param_menu["pvmap"] in [2,3] : pvmap.saveImage(saveDir+'/pvmap', skip=save_int)
        #if param_menu["pvmap"] == 3 : makeMovie(saveDir+'/pvmap')
        #if param_menu["pvmap"] == 4 : np.save(saveDir+'/pvmap', pvmap.data)
        im = xp.asnumpy(rawcam.data[0,:])
        im = (255*im/im.max()).astype(np.uint8) 
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        im_cpv = np.sum(xp.asnumpy(pvmap.data), axis = 0)
        im_cpv = (255*im_cpv/im_cpv.max()).astype(np.uint8) 
        im_cpv = cv2.cvtColor(im_cpv, cv2.COLOR_GRAY2BGR)
        im_cpv[:,:,0]=0
        im_cpv[:,:,1]=0
        im_cpv = cv2.addWeighted(im, 1.0, im_cpv, 0.2, 0)
        print("done")
    else:
        print("Skip PhaseVarianceMap")

    
    return rawcam, vmem, pmap, pvmap, im_cpv

if __name__ == '__main__':

  if len(sys.argv) < 2:
    print('Usage : '),
    print('python {0} [target directory]'.format(sys.argv[0]))
    exit()

  src = sys.argv[1]
  dst= sys.argv[2]
  run_opapp(raw_path=src, result_path=dst)

  import matplotlib.pyplot as plt
