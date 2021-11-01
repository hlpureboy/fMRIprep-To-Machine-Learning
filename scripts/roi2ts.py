import os,sys
from platform import win32_edition
from nilearn import image,masking,plotting
from nilearn.input_data import NiftiLabelsMasker
from config import RoiTs
sys.path.append('/share/data/scripts/')
from fmribrant.atlas.mni import Atlases_Nfiti
from fmribrant.signals.timeseries import img2atlas_ts

from tqdm import tqdm 
from multiprocessing import Pool
import numpy as np
from glob import glob 



schaefer_atlas = Atlases_Nfiti('Schaefer','Cortex').fetch_atlas(display=False,n_rois=200).load_img()
tianye_atlas = Atlases_Nfiti('Tianye','Subcortex').fetch_atlas(display=False,n_levels=4).load_img()
buckner_atlas = Atlases_Nfiti('Buckner','Cerebellum').fetch_atlas(display=False,yeo_networks=17).load_img()


def pipeline(args):
    subject_path = args
    subject_img = image.load_img(subject_path)
    ts1 = img2atlas_ts(subject_img,schaefer_atlas,t_r=RoiTs.t_r,high_pass=RoiTs.high_pass,low_pass=RoiTs.low_pass)
    ts2 = img2atlas_ts(subject_img,tianye_atlas,t_r=RoiTs.t_r,high_pass=RoiTs.high_pass,low_pass=RoiTs.low_pass)
    ts3 = img2atlas_ts(subject_img,buckner_atlas,t_r=RoiTs.t_r,high_pass=RoiTs.high_pass,low_pass=RoiTs.low_pass)
    ts = np.hstack([ts1,ts2,ts3])
    sub_id = subject_path.split('/')[RoiTs.subject_id_index]
    np.save(os.path.join(RoiTs.save_path,"{}.npy".format(sub_id)),ts)


def run():
    imgs = glob(RoiTs.reg_path)
    with Pool(RoiTs.n_process) as p:
        list(tqdm(p.imap(pipeline,imgs),total=len(imgs),desc='get roi time series'))
