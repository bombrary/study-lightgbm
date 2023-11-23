import lightgbm as lgb
from matplotlib import pyplot as plt

model = lgb.Booster(model_file=f'model/model_2018-2022.txt')

# fig, ax = plt.subplots()
# lgb.plot_tree(model, ax=ax)

# plt.show()
