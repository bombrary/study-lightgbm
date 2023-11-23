import pandas as pd

df = pd.read_csv('predict_result/tmp.csv')

result = df.sort_values('予測結果', ascending=False)[['予測結果', '馬番', '馬名']]
print(result)
