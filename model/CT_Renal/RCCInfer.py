import argparse
import os
import shutil
import time

import cv2
import numpy as np
import pandas as pd
from nnunet.inference.predict_simple import predictstart

from model.Base.BaseInfer import BaseInfer
from model.CT_Renal.RenalScore import RenalRate, calcuateVR
from utils.NiiHelper import readnii, mask_to_onehot, niiprocess

'''
使用混合监督后的模型推理RCC

预处理,得到
nnUNet_determine_postprocessing -m 3d_fullres -t 888 -tr MYtrainer

推理模型
nnUNet_predict 
-i /media/alex/2T-DISK/XB/KITS19/infer 
-o $RESULTS_FOLDER/kits90/ 
-tr MYtrainer 
-ctr nnUNetTrainerV2CascadeFullRes 
-p nnUNetPlansv2.1 
-t Task888_RCC
-mode normal fast fastest 
'''


class RCCInfer(BaseInfer):
    def __init__(self, img_data, model_data, imps="", thick=""):
        super().__init__(img_data, model_data)
        self.imps = imps  # 像素间距 CT图像特有的
        self.thick = thick  # 层厚
        self.outputdir = ""

    def preprocess(self, ):
        pass
        # 1.预处理，找到文件夹 改名字+_0000.nii.gz
        # 2.需要设置一个输出文件夹，创建子文件夹进行推理并保存
        yuan_data = self.img_data
        basename = os.path.basename(self.img_data)
        if not basename.endswith("_0000.nii.gz"):
            basename = basename[:-7]
            t = self.img_data.rfind("\\")
            self.img_data = self.img_data[0:t]
            self.outputdir = os.path.join(self.img_data, basename + "_predict")
        else:
            basename = basename[:-12]
            self.img_data = self.img_data[:-12]
            self.outputdir = self.img_data + "_predict"
        os.makedirs(self.outputdir, exist_ok=True)
        self.img_data = os.path.join(self.outputdir, basename + "_0000.nii.gz")
        shutil.copy(yuan_data, self.img_data)

    def infer(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", '--input_folder', default=self.img_data)
        parser.add_argument('-o', "--output_folder", default=self.outputdir)
        parser.add_argument('-t', '--task_name', default="888")
        parser.add_argument('-tr', '--trainer_class_name', default="MYtrainer")
        parser.add_argument('-m', '--model', default="3d_fullres")
        parser.add_argument('-p', '--plans_identifier', default="nnUNetPlansv2.1", required=False)
        parser.add_argument('-f', '--folds', nargs='+', default=[2])
        parser.add_argument('-ctr', '--cascade_trainer_class_name', default="nnUNetTrainerV2CascadeFullRes")
        parser.add_argument('-z', '--save_npz', required=False, action='store_true')
        parser.add_argument('-l', '--lowres_segmentations', required=False, default='None')
        parser.add_argument("--part_id", type=int, required=False, default=0)
        parser.add_argument("--num_parts", type=int, required=False, default=1)
        parser.add_argument("--num_threads_preprocessing", required=False, default=6, type=int)
        parser.add_argument("--num_threads_nifti_save", required=False, default=2, type=int)
        parser.add_argument("--disable_tta", required=False, default=False, action="store_true")
        parser.add_argument("--overwrite_existing", required=False, default=False, action="store_true")
        # parser.add_argument("--mode", type=str, default="normal", required=False, help="Hands off!")
        parser.add_argument("--mode", type=str, default="fastest", required=False, help="Hands off!")
        parser.add_argument("--all_in_gpu", type=str, default="None", required=False)
        parser.add_argument("--step_size", type=float, default=0.5, required=False, help="don't touch")
        parser.add_argument('-chk', required=False, default='model_final_checkpoint')
        parser.add_argument('--disable_mixed_precision', default=False, action='store_true', required=False)
        predictstart(parser)

    def postprocess(self, infermasks):
        # 后处理，根据连通域分析去除假阳性
        return infermasks

    def getothers(self, mask):
        # 计算肿瘤体积，最大半径，T分期，Renal评分等
        renal, ps = niiprocess(self.img_data, "肾盂")
        self.imps = ps[0]
        self.thick = ps[1]
        renalmask = mask[0]
        tumormask = mask[1]
        volume, maxlenth = calcuateVR(tumormask, self.imps, self.thick)
        RR = RenalRate(r=maxlenth)
        score = RR.getscore(renal, renalmask, tumormask, self.imps, self.thick)
        TNM = RR.getTNM()
        # ret = [RR.R, RR.E, RR.N, RR.L, score, volume, maxlenth]
        ret = [volume, score, TNM]  # 体积，分数，T分期
        return ret


def saveAsCSV(startindex):
    path = "F:\\MedData\\kidney\\kits\\data"
    maskpath = "F:\\MedData\\kidney\\kits\\gt"
    patints = os.listdir(path)
    array = []
    while startindex <= len(patints):
        p = "kidney_%03d_0000.nii.gz" % startindex
        mask = "gt_%03d.nii.gz" % startindex
        ps = os.path.join(path, p)
        r = RCCInfer(ps, "F:\\MedData\\kidney\\model")
        time_start = time.time()
        vo = r.getothers(os.path.join(maskpath, mask))
        time_c = round(time.time() - time_start, 2)
        vo.insert(0, mask)
        vo.append(str(time_c))
        print(startindex)
        startindex += 1
        array.append(vo)
    output = pd.DataFrame(array)
    output.to_csv('F:/MedData/kidney/kits/testcsv.csv', encoding='gbk')


# 推理由于windows的多线程和Linux不一样,换了一个支持windows的版本的nnunet
# 单个推理都爆显存，我的6G显存跑不了，但是接口什么的都是通的，就这样吧。
if __name__ == '__main__':
    saveAsCSV(1)
#     ps = "F:\MedData\kidney\kits\data\kidney_016_0000.nii.gz"
#     mask = "F:\MedData\kidney\kits\gt\gt_016.nii.gz"
#     r = RCCInfer(ps, "F:\\MedData\\kidney\\model")
#     vo = r.getothers(mask)
#     print(vo)
