# fMRIprep Pipeline To Machine Learning(Demo)
> 所有配置均在`config.py`文件下定义

## 前置环境(lilab)
- 各个节点均安装docker，并有fmripre的镜像
- 可以使用conda中的base环境（相应的第三份包之后更新）

## 1. fmriprep script on single machine(docker)
在`config.py`中的`fMRI_Prep_Job`类中配置相应变量,注意在修改`cmd`时，不能修改`{}`中的关键字。在执行此步骤时，将自动在bids同级目录下建立`processed`文件夹，用来存放后处理数据。其中处理后的fmriprep数据存放在`processed/frmriprep`、`prceossed/fressurfer`中。
```python
class fMRI_Prep_Job:
    # input data path
    bids_data_path  = "/share/data2/dataset/ds002748/depression"
    # 一个容器中处理多少个被试 
    step = 8
    # fmriprep opm thread
    thread = 9
    # max work contianers
    max_work_nums = 10

    # 在bids同级目录下创建processed文件夹
    bids_output_path = os.path.join("/".join(bids_data_path.split('/')[:-1]),'processed')
    if not os.path.exists(bids_output_path):
        os.mkdir(bids_output_path)
    # fmri work path 
    fmri_work="/share/fmri_work"
    # freesurfer_license
    freesurfer_license = "/share/user_data/public/fanq_ocd/license.txt"
    # image id fmriprep
    image_id = "d7235efbbd3c"
    # fmriprep cmd 
    cmd ="docker run -it --rm -v {bids_data_path}:/data -v {freesurfer_license}:/opt/freesurfer/license.txt -v {bids_output_path}:/out -v {fmri_work}:/work {image_id} /data /out --skip_bids_validation --ignore slicetiming fieldmaps  -w /work --omp-nthreads {thread} --fs-no-reconall --resource-monitor participant --participant-label {subject_ids}"
```
## 2. fmriprep post preocess
这一步的操作主要依赖于`fmribrant`，主要作用是回归掉白质信号、脑脊液信号、全脑信号、头动信息、并进行滤波（可选），将其处理后的文件放存在`prcoessed/post-precoss/<un>fliter/clean_imgs`中，`<un>`可选表示是否进行滤波。该配置中不建议修改`dataset_path`,`store_path`
```python
class PostProcess:
    """
    fmriprep 后处理数据
    """
    # 类型的名字
    task_type = "rest"

    dataset_path = os.path.join(fMRI_Prep_Job.bids_output_path,'fmriprep')

    store_path = os.path.join(fMRI_Prep_Job.bids_output_path,'post-process')

    t_r = 2.5

    low_pass = 0.08

    high_pass = 0.01

    n_process = 40

    if t_r != None:
        store_path = os.path.join(store_path,'filter','clean_imgs')
    else:
        store_path = os.path.join(store_path,'unfilter','clean_imgs')

    os.makedirs(store_path,exist_ok=True)
```
## 3.获取ROI级别的时间序列
atlas由271个roi组成，分别是Schaefer_200(皮上),Tianye_54(皮下),Buckner_17(小脑)。由于在`fmribrant`中实现提取时间序列的功能，简单封装一下。
```python
class RoiTs:
    """
    ROI 级别时间序列
    处理271个全脑roi
    """
    n_process = 40

    # 如果在第二步fmri post process已经滤波之后，不建议再次使用滤波操作
    t_r = None
    
    low_pass = None

    high_pass = None
    
    flag_gs = False #  回归全脑均值为 True 否则为False
    # 以下内容不建议修改

    if flag_gs:
        file_name = "*with_gs.nii.gz"
        ts_file = "GS"
    else:
        file_name = "*without_gs.nii.gz"
        ts_file = "NO_GS"
    
    reg_path = os.path.join(PostProcess.store_path,"*",PostProcess.task_type,file_name)
    
    subject_id_index = -3

    save_path = os.path.join("/".join(PostProcess.store_path.split('/')[:-1]),'timeseries',ts_file)

    os.makedirs(save_path,exist_ok=True)
```
## 4. Machine Learning(Baseline)
这一步是可选的，一般先用来看看FC做性别分类、年龄回归的效果如何。只保留粗略结果，详细结果可以使用`baseline`这个包。
```python
class ML:
    # 选择的subject id 默认是全部
    sub_ids = [i.split('.')[0] for i in os.listdir(RoiTs.save_path)]
    # 量表位置
    csv = pd.read_csv('/share/data2/dataset/ds002748/depression/participants.tsv',sep='\t')
    #取交集
    csv = pd.DataFrame({"participant_id":sub_ids}).merge(csv)
    # 分类的任务
    classifies = ["gender"]
    # 回归的任务
    regressions = ["age"]
    # 分类模型
    classify_models = [SVC(),SVC(C=100),SVC(kernel='linear'),SVC(kernel='linear',C=100)]
    # 回归模型
    regress_models = [SVR(),SVR(C=100),SVR(kernel='linear'),SVR(kernel='linear',C=100)]
    kfold = 3
    # 多少个roi
    rois = 200
```
## 5. run
修改`script/run.py` ，
```python
from fmriprep_job import run_fmri_prep
from fmriprep_pprocess import  run as pp_run
from roi2ts import run as roi_ts_run
from fast_fc_ml import run as ml_run


if __name__ =='__main__':
    run_fmri_prep() # fmriprep
    pp_run() # fmriprep post process
    roi_ts_run() # get roi time series
    ml_run() # machine learning
```
然后执行
```
python run.py
```

## 6. To Do

- 质量控制