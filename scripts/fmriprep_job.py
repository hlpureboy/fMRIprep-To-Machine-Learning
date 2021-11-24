import os
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import logging
from glob import glob
from  config import fMRI_Prep_Job

logging.basicConfig(filename='docker.log', level=logging.INFO)

def get_docker_container_num(imgage_id='d7235efbbd3c'):
    """
    get docker container num
    """
    num = os.popen('docker ps | grep {} |wc -l'.format(imgage_id)).read().split('\n')[0]
    return int(num)

def _fmriprep_cmd(args):
    """
     --fs-no-reconall usage 
    fmriprep cmd 
    """
    bids_data_path,freesurfer_license,bids_output_path,fmri_work,subject_ids,thread = args
    cmd = fMRI_Prep_Job.cmd
    cmd = cmd.format(bids_data_path=bids_data_path,freesurfer_license=freesurfer_license,bids_output_path=bids_output_path,image_id=fMRI_Prep_Job.image_id,fmri_work=fmri_work,subject_ids=" ".join(subject_ids),thread=thread)
    logging.info(cmd)
    wrap_log = os.popen(cmd)
    for log in wrap_log:pass

def run_fmri_prep():
    bids_data_path = fMRI_Prep_Job.bids_data_path
    freesurfer_license = fMRI_Prep_Job.freesurfer_license
    bids_output_path = fMRI_Prep_Job.bids_output_path
    fmri_work = fMRI_Prep_Job.fmri_work
    step = fMRI_Prep_Job.step
    thread = fMRI_Prep_Job.thread
    # 获取所有subject
    subject_ids = [i.split('/')[-1] for i in glob(os.path.join(bids_data_path,'sub-*'))]
    args = []
    count = 0
    while count <len(subject_ids):
        if count +step >len(subject_ids):
            _subject_ids = subject_ids[count:]
        else:
            _subject_ids = subject_ids[count:count+step]
        args.append((bids_data_path,freesurfer_license,bids_output_path,fmri_work,_subject_ids,thread))
        count += step
    with ThreadPoolExecutor(max_workers=fMRI_Prep_Job.max_work_nums) as executor:
        list(tqdm(executor.map(_fmriprep_cmd, args), total=len(args)))
