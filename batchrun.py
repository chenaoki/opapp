# -*- coding: utf-8 -*-
import os,sys,shutil,glob
from opapp import run_opapp

if __name__ == "__main__":
    path = sys.argv[1]
    result = sys.argv[2]
    paths = sorted(glob.glob(os.path.join(path,"*")))
    print(paths)
    for i,src_path in enumerate(paths):
        files = sorted(glob.glob(src_path+"/*.raww"))
        splt_src = (src_path.split("\\"))
        out_path = os.path.join(result,"{0}/{1}".format(splt_src[-2],splt_src[-1]))
        if (len(files)>0):
            print(out_path)
            run_opapp('./param.json',raw_path=src_path,result_path=out_path)
            shutil.copy("./param.json",out_path)
