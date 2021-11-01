import sys
sys.path.append('/share/data/scripts/')
from fmribrant.process import process_img,muti_process_img
from fmribrant.config import ProcessConfig
from fmribrant.dataset import fMriprep
from config import PostProcess

def run():
    dataset = fMriprep(PostProcess.dataset_path)
    tasks = dataset.get_tasks(PostProcess.task_type)
    config = ProcessConfig()
    config.store_path = PostProcess.store_path
    config.dataset_type = 'fmri_perp'
    config.low_pass = PostProcess.low_pass
    config.high_pass = PostProcess.high_pass
    config.t_r = PostProcess.t_r
    muti_process_img(subjects=tasks, process_num=PostProcess.n_process, config=config)
    