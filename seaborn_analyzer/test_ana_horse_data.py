#参考としてtitanicデータを読み込んでいます
import seaborn as sns
titanic = sns.load_dataset("titanic")

import pandas as pd
horse_data = pd.read_csv("../csv/cnv/cnv_horse-1975_1-2021_4_27000.csv",sep=",")
horse_data = horse_data[["rank","age","horse_number","burden_weight","last_time","odds","popular","horse_weight"]]
print(horse_data)

#ここから実行部分
from custom_pair_plot import CustomPairPlot
gp = CustomPairPlot()
gp.pairanalyzer(horse_data)