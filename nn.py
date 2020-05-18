import numpy as np
import sklearn
import pandas as pd
from sklearn.multioutput import ClassifierChain
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import label_ranking_average_precision_score
from sklearn.svm import SVC
from sklearn.preprocessing import MultiLabelBinarizer
import pickle
from sklearn.multiclass import OneVsRestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import SVC, LinearSVC
from sklearn.metrics import label_ranking_average_precision_score
from sklearn.neural_network import MLPClassifier

import time

train_path = "/scratch/ab8690/ml/data/train.csv"
val_path = "/scratch/ab8690/ml/data/dev.csv"

train = pd.read_csv(train_path, index_col=0)
val = pd.read_csv(val_path, index_col=0)

val = val[~val.labels.str.contains(":")]
train = train[~train.labels.str.contains(":")]
labels_list = [label.split(" ") for label in train['labels']]
labels_list = [label[0].split(",") for label in labels_list]
labels_list_val = [label.split(" ") for label in val['labels']]
labels_list_val = [label[0].split(",") for label in labels_list_val]
labels_list = [[int(s) for s in sublist] for sublist in labels_list] 
labels_list_val = [[int(s) for s in sublist] for sublist in labels_list_val] 


mlb = MultiLabelBinarizer(classes = range(3993))
encoded_labels = mlb.fit_transform(labels_list)
encoded_labels_df = pd.DataFrame(encoded_labels, columns=mlb.classes_)
mlb = MultiLabelBinarizer(classes = range(3993))
encoded_labels_val = mlb.fit_transform(labels_list_val)
encoded_labels_df_val = pd.DataFrame(encoded_labels_val, columns=mlb.classes_)

def make_dict(entry):
    # entry is a list with form ['id:value', 'id:value']
    col_dict = {}
    for word in entry:
        key, value = word.split(":")
        key = int(key)
        value = float(value)
        col_dict[key] = value
    return col_dict
    
    
train_df = train['features']
val_df = val['features']

features = [item.split(" ") for item in train_df]
col_dicts = [make_dict(entry) for entry in features]

features_val = [item.split(" ") for item in val_df]
col_dicts_val = [make_dict(entry) for entry in features_val]

features_df = pd.DataFrame(col_dicts)
features_df_val = pd.DataFrame(col_dicts_val)

features_df = features_df.fillna(0)
features_df_val = features_df_val.fillna(0)
print('done cleanning')

###### downsample
#features_df = features_df.iloc[0:5000,:]
#features_df_val = features_df_val[0:1000,]
#encoded_labels_df = encoded_labels_df.iloc[0:5000,:]

print("feat shape:", features_df.shape)
print("labels shape:", encoded_labels_df.shape)

X_train = np.array(features_df)
Y_train = np.array(encoded_labels_df)
x_val = np.array(features_df_val)
y_val = np.array(encoded_labels_df_val)

###### DEFINE MODEL ######

layers=[(100, 100),(100, 100, 100),(500, 500),(500, 500, 500),(1000,),(1000, 1000)]
lr =[0.001,0.0001]


results=[]
for i in layers:
    for j in lr:
        mlp = MLPClassifier()
        mlp.fit(X_train,Y_train)
        y_score = mlp.predict_proba(x_val)
        precision =label_ranking_average_precision_score(y_val, y_score)
        print(precision,i,j)
        results.append(precision)

        

