import pandas as pd
import os
import glob
from natsort import natsorted
import pathlib

# 変換後データの格納ディレクトリ作成
if not os.path.isdir("cnv"):
    os.makedirs("cnv")

csv_dir = "org"
file_list = natsorted(glob.glob(csv_dir+"/horse*"))

for j in range(len(file_list)):
    file_name = os.path.split(file_list[j])[1]
    horse_data = pd.read_csv("org/"+file_name,sep=",")

    # rank
    num = horse_data.columns.get_loc('rank')
    for i in range(len(horse_data)):
        try:
            r = int(horse_data.iat[i,num])
            rank = r
        except:
            rank = None
        horse_data.iat[i,num] = rank

    # sex_and_age
    num = horse_data.columns.get_loc('sex_and_age')
    horse_data.insert(num+1, "sex", "")
    horse_data.insert(num+1, "age", "")
    num_s = horse_data.columns.get_loc('sex')
    num_a = horse_data.columns.get_loc('age')
    for i in range(len(horse_data)):
        c = horse_data.iat[i,num]
        c_s = ""
        tmp = ""
        if "牡" in c:
            c_s = "M"
            tmp = "牡"
        elif "セ" in c:
            c_s = "S"
            tmp = "セ"
        elif "牝" in c:
            c_s = "F"
            tmp = "牝"
        c_a = int(c.split(tmp)[-1])
        horse_data.iat[i,num_s] = c_s
        horse_data.iat[i,num_a] = c_a

    # goal_time
    num = horse_data.columns.get_loc('goal_time')
    for i in range(len(horse_data)):
        if type(horse_data.iat[i,num]) == float:
            continue
        else:
            gt = horse_data.iat[i,num].split(":")
            if len(gt) == 1:
                time = float(gt[0])
            elif len(gt) == 2:
                time = float(gt[1]) + float(gt[0])*60
            else:
                time = None
            horse_data.iat[i,num] = time

    # horse_weight
    num = horse_data.columns.get_loc('horse_weight')
    horse_data.insert(num+1, "weight_change", "")
    num_wc = horse_data.columns.get_loc('weight_change')
    for i in range(len(horse_data)):
        if type(horse_data.iat[i,num]) == float:
            continue
        else:
            hw = horse_data.iat[i,num].split("(")
            if len(hw) == 1:
                weight = None
                change = None
            else:
                weight = float(hw[0])
                wc = hw[1][0:-1]
                change = 0
                print(wc)
                if "+" in wc:
                    change = float(wc[1:])
                elif "-" in wc:
                    change = float(wc[1:]) * -1
                else:
                    change = float(wc)
            horse_data.iat[i,num] = weight
            horse_data.iat[i,num_wc] = change


    #print(horse_data[["rank","sex_and_age","goal_time","horse_weight"]])
    
    horse_data = horse_data.drop(columns='sex_and_age')
    horse_data = horse_data.drop(columns='time_value')
    horse_data = horse_data.drop(columns='tame_time')
    print(horse_data)
    
    horse_data.to_csv("cnv/"+"cnv_"+file_name,index=False)