import pandas as pd
import time
horse_data = pd.read_csv("../csv/horse-2019-1_my.csv",sep=",")
race_data = pd.read_csv("../csv/race-2019-1_my.csv",sep=",")

# 短距離（1000m,1200m）のrace_idを取得
num = race_data.columns.get_loc('race_course_m')
num_race_id = race_data.columns.get_loc('race_id')
sprint_race_id_list = []
for i in range(len(race_data)):
    m = race_data.iat[i,num]
    if m < 1201:
        sprint_race_id_list.append(race_data.iat[i,num_race_id])


start = time.time()

# 短距離レースのhorse_dataを抽出
sprint_horse_data = horse_data.iloc[0:0]
num = horse_data.columns.get_loc('race_id')
for i in range(len(horse_data)):
    hid = horse_data.iat[i,num]
    if hid in sprint_race_id_list:
        sprint_horse_data = sprint_horse_data.append(horse_data.loc[i])
"""

# 短距離レースのhorse_dataを抽出
sprint_horse_data = horse_data.iloc[0:0]
num = horse_data.columns.get_loc('race_id')
i = 0
idx = 0
while True:
    if i == len(horse_data) or idx == len(sprint_race_id_list):
        break

    hid = horse_data.iat[i,num]
    if hid == sprint_race_id_list[idx]:
        while True:
            if horse_data.iat[i,num] != sprint_race_id_list[idx]:
                idx += 1
                break

            sprint_horse_data = sprint_horse_data.append(horse_data.loc[i])
            i += 1
    else:
        i += 1
"""

elapsed_time = time.time() - start
print(elapsed_time)

sprint_horse_data.to_csv('sprint_horse-2019-1_my.csv',index=False)