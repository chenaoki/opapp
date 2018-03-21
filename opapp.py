import sys, os, json
#import cv2
import numpy as np

from opmap.rawCam import RawCam
from opmap.vmemMap import VmemMap
from opmap.phaseMap import PhaseMap
from opmap.phaseVarianceMap import PhaseVarianceMap
#from opmap.coreMap import CoreMap
from opmap.util import makeMovie
#from opmap.util import phase_add
#from opmap.cmap import bipolar

def run_opapp(json_path='./param.json', raw_path=None, result_path=None):
    with open(json_path, "r") as f : params = json.load(f)
    param_cam     = params.get("camera",{})
    param_menu   = params.get("menu",{})
    param_vmem    = params.get("vmem",{})
    param_pvmap   = params.get("pvmap",{})
#    param_core    = params.get("core",{})
#    param_integ   = params.get("integ",{})
    param_roi     = params.get("roi_rect",{})
    save_int      = param_menu.get("save_int",1)
#    flg_corelog   = param_menu.get("core_log",1)
    diff_min      = param_vmem.get("diff_min",0)
    intensity_min = param_vmem.get("intensity_min",0)
    smooth_size   = param_vmem.get("smooth_size",9)
#    threshold     = param_core.get("pv_thre",0.6)
    pv_win        = param_pvmap.get("pv_win",9)
#    phase_wf      = param_integ.get("phase_wf",-0.6*np.pi)
#    phase_wt      = param_integ.get("phase_wt", 0.6*np.pi)
#    phase_dwf     = param_integ.get("phase_dwf", 0.1 *np.pi)
#    phase_dwt     = param_integ.get("phase_dwt", 0.1 *np.pi)

    roi_rect = {
        "top" : param_roi["top"],
        "bottom" : param_cam["image_height"] - 1 - param_roi["bottom"],
        "left" : param_roi["left"],
        "right" : param_cam["image_width"] - 1 - param_roi["right"]
    }

    if raw_path is not None: param_cam["path"] = raw_path
    if result_path is not None:
        saveDir = result_path
    else:
        saveDir = os.path.join(param_cam["path"], "result/opapp")
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
#    print(saveDir)

    if param_menu["cam"] == 0 : return
#    print "RawCam..."
    rawcam = RawCam(**param_cam)
    if roi_rect is not None : rawcam.setRectROI(**roi_rect)
    if intensity_min > 0 : rawcam.setIntROI(val_min=intensity_min)
    rawcam.morphROI(closing=10)
    rawcam.morphROI(erosion=10)
    if param_menu["cam"] in [2,3] : rawcam.saveImage(saveDir+'/cam', skip=save_int)
    if param_menu["cam"] == 3 : makeMovie(saveDir+'/cam')
    if param_menu["cam"] == 4 : np.save(saveDir+'/cam', rawcam.data)
#    print "done",

    if param_menu["vmem"] == 0 : return
#    print "VmemMap..."
    vmem = VmemMap(rawcam)
    if diff_min > 0 : vmem.setDiffRange(diff_min=diff_min)
    vmem.morphROI(closing=10)
    vmem.morphROI(erosion=10)
    if smooth_size > 0 : vmem.smooth(size=smooth_size)
    if param_menu["vmem"] in [2,3] : vmem.saveImage(saveDir+'/vmem', skip=save_int)
    if param_menu["vmem"] == 3 : makeMovie(saveDir+'/vmem')
    if param_menu["vmem"] == 4 : np.save(saveDir+'/vmem', vmem.data)
#    print "done",

    if param_menu["pmap"] == 0 : return
#    print "PhaseMap..."
    pmap = PhaseMap(vmem)
    if param_menu["pmap"] in [2,3] : pmap.saveImage(saveDir+'/pmap', skip=save_int)
    if param_menu["pmap"] == 3 : makeMovie(saveDir+'/pmap')
    if param_menu["pmap"] == 4 : np.save(saveDir+'/pmap', pmap.data)
#    print "done",

    if param_menu["pvmap"] == 0 : return
#    print "PhaseVarianceMap..."
    pvmap = PhaseVarianceMap(pmap, size=pv_win)
    if param_menu["pvmap"] in [2,3] : pvmap.saveImage(saveDir+'/pvmap', skip=save_int)
    if param_menu["pvmap"] == 3 : makeMovie(saveDir+'/pvmap')
    if param_menu["pvmap"] == 4 : np.save(saveDir+'/pvmap', pvmap.data) 
#    print "done",

    if param_menu["core"] == 0 : return
#    print "CoreMap..."
#    coremap = CoreMap(pvmap, threshold=threshold)
#    if param_menu["core"] in [2,3] : coremap.saveImage(saveDir+'/core', skip=save_int)
#    if param_menu["core"] == 3 : makeMovie(saveDir+'/core')
#    if param_menu["core"] == 4 : np.save(saveDir+'/core', coremap.data)
#    if flg_corelog == 1 : np.savetxt(saveDir+'/core.log', coremap.getCoreLog())
#    print "done",

    if param_menu["integrate"] in [0,1] : return
#    print "Integrate..."
#    if param_menu["integrate"] in [2,3] :
#
#        if not os.path.exists(saveDir+'/all'):
#            os.makedirs(saveDir+'/all')
#
#        s = coremap.data.shape
#        if save_int > 0 :
#            frames = list(range(0, s[0], save_int))
#        else:
#            frames = list(range(s[0]))
#
#        cam = cv2.resize( rawcam.data[0,:,:], (s[1],s[2]) )
#        cam = 255.0 * ( cam.astype(np.float) / float(np.max(cam)) )
#        cmap_vm = bipolar()
#
#        for n, f in enumerate(frames):
#
#            im_out = np.zeros([s[1],s[2],3], dtype=np.uint8)
#
#            # Blending
#            vm = cv2.resize( 0.5*(1.0+vmem.data[f,:,:]), (s[1],s[2]) )
#            wf = ( np.absolute( phase_add( pmap.data[f,:,:] , -phase_wf ) ) < phase_dwf )*1
#            wt = ( np.absolute( phase_add( pmap.data[f,:,:] , -phase_wt ) ) < phase_dwt )*1
#            wf = wf.astype(np.uint8)
#            wt = wt.astype(np.uint8)
##            core = ((coremap.data[f,:,:]>0)*1).astype(np.uint8)
#
#            im_out = ( cmap_vm(vm)[:,:,:3] * 255 ).astype(np.uint8)
#            im_out = im_out[:,:,::-1]
#            im_out[:,:,1]  = wf*255 
#            im_out[:,:,0]  = wt*255 
#            for i, c in enumerate('rgb'):
##                im_out[:,:,i] = core*255 + (1-core)*im_out[:,:,i]
#                im_out[:,:,i] = cam*0.3 + im_out[:,:,i]*(1-0.3)
#                im_out[:,:,i] *= pmap.roi.astype(np.uint8)
#
#            im_draw = np.array(im_out)
#            cv2.putText(im_draw, "{0:0>4}".format(f), (5,15), cv2.FONT_HERSHEY_PLAIN,.8,(255,255,255))
#            cv2.imwrite(saveDir+'/all/{0:0>6}.png'.format(n), im_draw)      
#  
#    if param_menu["integrate"] == 3 :
#        makeMovie(saveDir+'/all', img_type='png')
  
#    print "done"

if __name__ == '__main__':

  if len(sys.argv) < 2:
    print('Usage : '),
    print('python {0} [target directory]'.format(sys.argv[0]))
    exit()

  src = sys.argv[1]
  dst= sys.argv[2]
  run_opapp(raw_path=src, result_path=dst)
