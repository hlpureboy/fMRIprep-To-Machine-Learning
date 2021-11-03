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


def fileformat(file_name):
    """
    """
    file_name = file_name.split('.')[0]
    file_names = file_name.split('_')
    d = {}
    for type_name in file_names:
        if type_name.startswith('ses'):
            d['ses']=type_name
        if type_name.startswith('task'):
            d['task'] = type_name.split('-')[-1]
        if type_name.startswith('sub'):
            d['sub_id'] = type_name
    if d.get('ses') == None:
        d['ses'] = "ses-0"
    

def pipeline(args):
    subject_path = args
    subject_img = image.load_img(subject_path)
    ts1 = img2atlas_ts(subject_img,schaefer_atlas,t_r=RoiTs.t_r,high_pass=RoiTs.high_pass,low_pass=RoiTs.low_pass)
    ts2 = img2atlas_ts(subject_img,tianye_atlas,t_r=RoiTs.t_r,high_pass=RoiTs.high_pass,low_pass=RoiTs.low_pass)
    ts3 = img2atlas_ts(subject_img,buckner_atlas,t_r=RoiTs.t_r,high_pass=RoiTs.high_pass,low_pass=RoiTs.low_pass)
    ts = np.hstack([ts1,ts2,ts3])
    name_format = fileformat( subject_path.split('/')[-1])
    save_path = os.path.join(RoiTs.save_path,name_format['sub_id'],name_format['task'])
    os.makedirs(save_path,exist_ok=True)
    np.save(os.path.join(save_path,"{}.npy".format(name_format['ses'])),ts)


def run():
    imgs = glob(RoiTs.reg_path)
    with Pool(RoiTs.n_process) as p:
        list(tqdm(p.imap(pipeline,imgs),total=len(imgs),desc='get roi time series'))
