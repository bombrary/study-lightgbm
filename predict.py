import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder, StandardScaler
import sys

assert(len(sys.argv) >= 3)
yearStart = int(sys.argv[1])
yearEnd = int(sys.argv[2])

# 予測を行う新しいデータの読み込み
# file_name = 'race_data_hanshin_11R_20230625'
file_name = 'tmp'
old_data = pd.read_csv('race_data/' + file_name + '.csv')
new_data = pd.read_csv('race_data/' + file_name + '.csv')

#人気、オッズを退避
pop = new_data['人気']
odds = new_data['オッズ']
# 着順列を除外 (この列が存在する場合)

drop_features = ['着順',
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
new_data = new_data.drop(drop_features, axis=1)


#日付
# 日付時刻型への変換を試み、無効な形式であればNaNにする
new_data['日付'] = pd.to_datetime(new_data['日付'], errors='coerce')
new_data['日付1'] = pd.to_datetime(new_data['日付1'], errors='coerce')
new_data['日付2'] = pd.to_datetime(new_data['日付2'], errors='coerce')
new_data['日付3'] = pd.to_datetime(new_data['日付3'], errors='coerce')
new_data['日付4'] = pd.to_datetime(new_data['日付4'], errors='coerce')
new_data['日付5'] = pd.to_datetime(new_data['日付5'], errors='coerce')
# 日付カラムから年、月、日を抽出
new_data['year'] = new_data['日付'].dt.year
new_data['month'] = new_data['日付'].dt.month
new_data['day'] = new_data['日付'].dt.day
# (年-yearStart)*365 + 月*30 + 日 を計算し新たな '日付'カラムを作成
new_data['日付'] = (new_data['year'] - yearStart) * 365 + new_data['month'] * 30 + new_data['day']

new_data['year'] = new_data['日付1'].dt.year
new_data['month'] = new_data['日付1'].dt.month
new_data['day'] = new_data['日付1'].dt.day
# (年-yearStart)*365 + 月*30 + 日 を計算し新たな '日付'カラムを作成
new_data['日付1'] = (new_data['year'] - yearStart) * 365 + new_data['month'] * 30 + new_data['day']

new_data['year'] = new_data['日付2'].dt.year
new_data['month'] = new_data['日付2'].dt.month
new_data['day'] = new_data['日付2'].dt.day
# (年-yearStart)*365 + 月*30 + 日 を計算し新たな '日付'カラムを作成
new_data['日付2'] = (new_data['year'] - yearStart) * 365 + new_data['month'] * 30 + new_data['day']

new_data['year'] = new_data['日付3'].dt.year
new_data['month'] = new_data['日付3'].dt.month
new_data['day'] = new_data['日付3'].dt.day
# (年-yearStart)*365 + 月*30 + 日 を計算し新たな '日付'カラムを作成
new_data['日付3'] = (new_data['year'] - yearStart) * 365 + new_data['month'] * 30 + new_data['day']

new_data['year'] = new_data['日付4'].dt.year
new_data['month'] = new_data['日付4'].dt.month
new_data['day'] = new_data['日付4'].dt.day
# (年-yearStart)*365 + 月*30 + 日 を計算し新たな '日付'カラムを作成
new_data['日付4'] = (new_data['year'] - yearStart) * 365 + new_data['month'] * 30 + new_data['day']

new_data['year'] = new_data['日付5'].dt.year
new_data['month'] = new_data['日付5'].dt.month
new_data['day'] = new_data['日付5'].dt.day
# (年-yearStart)*365 + 月*30 + 日 を計算し新たな '日付'カラムを作成
new_data['日付5'] = (new_data['year'] - yearStart) * 365 + new_data['month'] * 30 + new_data['day']
# 不要となった 'year', 'month', 'day' カラムを削除
new_data.drop(['year', 'month', 'day'], axis=1, inplace=True)

# カテゴリカル変数のエンコーディング
categorical_features = ['馬', '騎手', 'レース名','場名','開催', '騎手1', '騎手2', '騎手3', '騎手4', '騎手5']  # カテゴリカル変数の列名を指定してください

# ラベルエンコーディング
for i, feature in enumerate(categorical_features):
    print(f"\rProcessing feature {i+1}/{len(categorical_features)}", end="")
    le = LabelEncoder()
    new_data[feature] = le.fit_transform(new_data[feature])


# モデルの読み込み
model = lgb.Booster(model_file=f'model/model_{yearStart}-{yearEnd}.txt')
# Make prediction
y_new_pred = model.predict(new_data)

# 予測結果を0と1に変換
# y_new_pred = (y_new_pred >= 0.5).astype(int)

# 予測結果の表示
print(y_new_pred)

# '予測結果'という新しい列を2列目に追加
new_data.insert(1, '予測結果', y_new_pred)
new_data.insert(3, '人気', pop)
new_data.insert(4, 'オッズ', odds)
new_data.insert(5, '馬名', old_data['馬'])

# Save prediction
new_data.to_csv('predict_result/' + file_name + '.csv', index=False)

result = new_data.sort_values('予測結果', ascending=False)[['予測結果', '馬番', '馬名']]
print(result)
