from re import sub
import sys,os
sys.path.append('/share/data/scripts/')
from baseline.workflow import fast_run
import pandas as pd 
from config import ML,RoiTs,Result
import numpy as np
from sklearn.preprocessing import LabelEncoder

def run():
    # 生成fcs
    fcs = []
    check_ids = []
    for sub_id in ML.sub_ids:
        ts = np.load(os.path.join(RoiTs.save_path,sub_id+'.npy')).T[:ML.rois]
        
        fc = np.corrcoef(ts)
        if fc.shape[0] !=ML.rois:
            raise ValueError("FC is not {0}x{1}".format(ML.rois,ML.rois))
        fcs.append(fc[np.triu_indices(ML.rois,k=1)].flatten())
        check_ids.append(ML.sub_ids)
    fcs = np.vstack(fcs)
    results = []
    for task in ML.classifies:
        index = list(ML.csv[ML.csv[task].isna()==False].index)
        x = fcs[index]
        y = LabelEncoder().fit_transform(ML.csv[task].values[index])
        res = fast_run(x,y,'classification',models=ML.classify_models,fold=ML.kfold)
        res_df = res.result
        res_df['task'] = [task for i in range(len(ML.classify_models))]
        results.append(res_df)
    pd.concat(results).to_csv(os.path.join(Result.path,'classification.csv'),index=False)

    results = []
    for task in ML.regressions:
        index = list(ML.csv[ML.csv[task].isna()==False].index)
        x = fcs[index]
        y = ML.csv[task].values[index]
        res = fast_run(x,y,'regression',models=ML.regress_models,fold=ML.kfold)
        res_df = res.result
        res_df['task'] = [task for i in range(len(ML.classify_models))]
        results.append(res_df)
    pd.concat(results).to_csv(os.path.join(Result.path,'regression.csv'),index=False)
