import pandas as pd
import os
import glob
from natsort import natsorted
import pathlib

# 変換後データの格納ディレクトリ作成
if not os.path.isdir("cnv"):
    os.makedirs("cnv")

csv_dir = "org"
file_list = natsorted(glob.glob(csv_dir+"/race*"))

for j in range(len(file_list)):
    file_name = os.path.split(file_list[j])[1]
    race_data = pd.read_csv("org/"+file_name,sep=",")

    # race_title
    num = race_data.columns.get_loc('race_title')
    for i in range(len(race_data)):
        t = race_data.iat[i,num]
        if "未勝利" in t or "新馬" in t:
            title = "F"
        elif "500万下" in t or "400万下" in t:
            title = "W1"
        elif "1000万下" in t or "900万下" in t:
            title = "W2"
        elif "オープン" in t or "OP" in t:
            title = "OP"
        elif "L" in t:
            title = "L"
        elif "G1" in t:
            title = "G1"
        elif "G2" in t:
            title = "G2"
        elif "G3" in t:
            title = "G3"
        else:
            title = "WX"
        race_data.iat[i,num] = title

    # race_course
    num = race_data.columns.get_loc('race_course')
    race_data.insert(num+1, "race_course_gnd", "")    # 芝、ダート、障害
    race_data.insert(num+1, "race_course_lr", "")     # 右、左回り
    race_data.insert(num+1, "race_course_m", 0)       # 距離
    num_gnd = race_data.columns.get_loc('race_course_gnd')
    num_lr = race_data.columns.get_loc('race_course_lr')
    num_m = race_data.columns.get_loc('race_course_m')
    for i in range(len(race_data)):
        c = race_data.iat[i,num]
        c_gnd = ""
        if "芝" in c:
            c_gnd = "T"
        elif "ダ" in c:
            c_gnd = "D"
        if "障" in c:
            c_gnd = "O"
        c_lr = ""
        if "右" in c:
            c_lr = "R"
        elif "左" in c:
            c_lr = "L"
        else:
            c_lr = ""
        c_m = int(c[-5:-1])
        race_data.iat[i,num_gnd] = c_gnd
        race_data.iat[i,num_lr] = c_lr
        race_data.iat[i,num_m] = c_m
    

    # weather
    num = race_data.columns.get_loc('weather')
    for i in range(len(race_data)):
        w = race_data.iat[i,num]
        if "晴" in w:
            weather = "S"
        elif "曇" in w:
            weather = "C"
        elif "小雨" in w:
            weather = "R0"
        elif "雨" in w:
            weather = "R1"
        else:
            weather = ""
        race_data.iat[i,num] = weather

    # ground_status
    num = race_data.columns.get_loc('ground_status')
    for i in range(len(race_data)):
        gs = race_data.iat[i,num]
        if "不良" in gs:
            ground_status = "B"
        elif "稍重" in gs:
            ground_status = "H0"
        elif "重" in gs:
            ground_status = "H1"
        elif "良" in gs:
            ground_status = "G"
        else:
            ground_status = ""
        race_data.iat[i,num] = ground_status


    #print(race_data[["race_title","race_course_gnd","race_course_lr","race_course_m","weather","ground_status"]])

    race_data = race_data.drop(columns='race_course')
    print(race_data)

    race_data.to_csv("cnv/"+"cnv_"+file_name,index=False)