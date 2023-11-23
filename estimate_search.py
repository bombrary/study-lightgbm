import lightgbm as lgb
import pandas as pd
from sklearn.metrics import roc_curve,roc_auc_score
import matplotlib.pyplot  as plt
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import time
import sys

def split_date(df, test_size):
    sorted_id_list = df.sort_values('日付').index.unique()
    train_id_list = sorted_id_list[:round(len(sorted_id_list) * (1-test_size))]
    test_id_list = sorted_id_list[round(len(sorted_id_list) * (1-test_size)):]
    train = df.loc[train_id_list]
    test = df.loc[test_id_list]
    return train, test


assert(len(sys.argv) >= 3)
yearStart = int(sys.argv[1])
yearEnd = int(sys.argv[2])

# データの読み込み
data = pd.read_csv(f'encoded/encoded_{yearStart}-{yearEnd}.csv')
#着順を変換
data['着順'] = data['着順'].map(lambda x: 1 if x<4 else 0)

# 特徴量とターゲットの分割
train, test = split_date(data, 0.3)



def fit(num_leaves, min_data_in_leaf):
    X_train = train.drop(['着順','オッズ','人気','上がり','走破時間','通過順'], axis=1)
    y_train = train['着順']
    X_test = test.drop(['着順','オッズ','人気','上がり','走破時間','通過順'], axis=1)
    y_test = test['着順']

    # LightGBMデータセットの作成
    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_test, label=y_test)

    print(f"estimate: {num_leaves}, {min_data_in_leaf}")
    params={
        'num_leaves':num_leaves,
        'min_data_in_leaf': min_data_in_leaf,
        'class_weight':'balanced',
        'random_state':100
    }

    lgb_clf = lgb.LGBMClassifier(**params)

    start = time.perf_counter()
    lgb_clf.fit(X_train, y_train)
    end = time.perf_counter() - start

    y_pred_train = lgb_clf.predict_proba(X_train)[:,1]
    y_pred = lgb_clf.predict_proba(X_test)[:,1]

    score_train = roc_auc_score(y_train,y_pred_train)
    score_test = roc_auc_score(y_test,y_pred)

    #モデルの評価
    print(f"roc_auc_score(train): {score_train}")
    print(f"roc_auc_score(test): {score_test}")

    total_cases = len(y_test)  # テストデータの総数
    TP = (y_test == 1) & (y_pred >= 0.5)  # True positives
    FP = (y_test == 0) & (y_pred >= 0.5)  # False positives
    TN = (y_test == 0) & (y_pred < 0.5)  # True negatives
    FN = (y_test == 1) & (y_pred < 0.5)  # False negatives

    TP_count = sum(TP)
    FP_count = sum(FP)
    TN_count = sum(TN)
    FN_count = sum(FN)

    accuracy_TP = TP_count / total_cases * 100
    accuracy_TN = TN_count / total_cases * 100

    return score_train, score_test, accuracy_TP, accuracy_TN, end



# data = []
# for num_leaves in [31, 63, 127, 256]:
#     for min_data_in_leaf in [190, 190//2, 190//4, 190//8]:
#         score_train, score_test, accuracy_TP, accuracy_TN, est_time = fit(num_leaves, min_data_in_leaf)
#         data.append([num_leaves, min_data_in_leaf, score_train, score_test, accuracy_TP, accuracy_TN, est_time])
# 
# df = pd.DataFrame(data, columns=['num_leaves',
#                                  'min_data_in_leaf',
#                                  'score_train',
#                                  'score_test',
#                                  'accuracy_TP',
#                                  'accuracy_TN',
#                                  'time'])
# 
# df.to_csv(f'search_result.csv', index=False)


drop_features_all = ['着順',
                 'オッズ',
                 '人気',
                 '上がり',
                 '走破時間',
                 '通過順',
                 '天気',
                 '距離4',
                 '距離3',
                 '距離5',
                 '距離2',
                 '芝・ダート',
                 '芝・ダート1',
                 '芝・ダート2',
                 '芝・ダート3',
                 '芝・ダート4',
                 '芝・ダート5',]
drop_features_all = reversed(drop_features_all)

data = []
num_leaves = 127
min_data_in_leaf = 47
drop_features = []
for i, f in enumerate(drop_features_all):
    drop_features.append(f)
    print(drop_features)
    score_train, score_test, accuracy_TP, accuracy_TN, est_time = fit(num_leaves, min_data_in_leaf)
    data.append([i, score_train, score_test, accuracy_TP, accuracy_TN, est_time])

df = pd.DataFrame(data, columns=['drop_feature_num',
                                 'score_train',
                                 'score_test',
                                 'accuracy_TP',
                                 'accuracy_TN',
                                 'time'])

df.to_csv(f'search_result.csv', index=False)
