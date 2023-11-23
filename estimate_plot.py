from matplotlib import pyplot as plt
import pandas as pd

fig, ax = plt.subplots()

# df = pd.read_csv("search_result_param.csv")
# ax.scatter(df['num_leaves'], df['time'])
# ax.scatter(df['num_leaves'], df['accuracy_TP'] + df['accuracy_TN'])
# ax.set_ylabel('accuracy (%)')
# ax.set_xlabel('num_leaves')
# 
# for x, y, label in zip(df['num_leaves'],
#                        df['accuracy_TP'] + df['accuracy_TN'],
#                        df['min_data_in_leaf']):
#     ax.text(x, y, label)
# 
# plt.show()


df = pd.read_csv("search_result.csv")
ax.scatter(df['drop_feature_num'], df['accuracy_TP'] + df['accuracy_TN'])
ax.set_xlabel('drop feature num')
ax.set_ylabel('accuracy (%)')
plt.show()
