# author Nakkkkk (https://github.com/Nakkkkk)
# このプログラムによって発生した損害に対し、いかなる責任をも負わないとする。
# I assume no responsibility for any damages caused by this program.


import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import os
from natsort import natsorted
import glob
import seaborn as sns
import matplotlib.pyplot as plt
import statistics
import time

from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from multiprocessing.dummy import Pool




# 分布の計算
def calcGoalTimeDistribution(place, distance, race_course_gnd, weather, ground_status):
    csv_dir = "../data/all"
    horse_file_list = natsorted(glob.glob(csv_dir+"/*horse*"))
    race_file_list = natsorted(glob.glob(csv_dir+"/*race*"))
    file_list = np.vstack((horse_file_list, race_file_list)).T


    for idx_p in range(len(place)):
        for idx_d in range(len(distance)):
            for idx_rcg in range(len(race_course_gnd)):

                plt.clf()
                plt.figure(figsize=(15, 20), dpi=100)

                ave_time_mtx = np.ones((len(weather), len(ground_status))) # 1〜3位平均タイムのmatrix
                ave_time_mtx = [] # 1〜3位平均タイムのmatrix 競馬場、距離、芝ダ障は固定とする
                for i in range(len(weather)):
                    ave_time_mtx.append([])
                    for j in range(len(ground_status)):
                        ave_time_mtx[i].append([])
                for file in file_list:
                    horse_file_name = os.path.split(file[0])[1]
                    horse_data = pd.read_csv(csv_dir+"/"+horse_file_name,sep=",")
                    race_file_name = os.path.split(file[1])[1]
                    race_data = pd.read_csv(csv_dir+"/"+race_file_name,sep=",")
                    print(horse_file_name)

                    # 指定の競馬場　かつ　指定の距離　かつ　芝ダ障天候馬場　のrace_idをリストにする
                    ri_mtx = [] # 競馬場、距離、芝ダ障は固定とする
                    for i in range(len(weather)):
                        ri_mtx.append([])
                        for j in range(len(ground_status)):
                            ri_mtx[i].append([])
                    col_ri = race_data.columns.get_loc('race_id')
                    col_rcg = race_data.columns.get_loc('race_course_gnd')
                    col_w = race_data.columns.get_loc('weather')
                    col_gs = race_data.columns.get_loc('ground_status')
                    col_rcm = race_data.columns.get_loc('race_course_m')
                    col_wr = race_data.columns.get_loc('where_racecourse')
                    for row in range(len(race_data)):
                        ri = race_data.iat[row,col_ri]
                        rcg = race_data.iat[row,col_rcg]
                        w = race_data.iat[row,col_w]
                        gs = race_data.iat[row,col_gs]
                        rcm = race_data.iat[row,col_rcm]
                        wr = race_data.iat[row,col_wr]
                        # 20210504 競馬場、距離、芝ダ障は固定とする
                        if rcm == distance[idx_d] and place[idx_p] in wr and race_course_gnd[idx_rcg] in rcg:
                            for i in range(len(weather)):
                                for j in range(len(ground_status)):
                                    if w == weather[i] and gs == ground_status[j]:
                                        ri_mtx[i][j].append(ri)

                    # 指定の競馬場　かつ　指定の距離　かつ　芝ダ障天候馬場　における1〜3位タイム平均を求める
                    col_ri = horse_data.columns.get_loc('race_id')
                    col_gt = horse_data.columns.get_loc('goal_time')
                    col_r = horse_data.columns.get_loc('rank')
                    col_bw = horse_data.columns.get_loc('burden_weight')
                    for i in range(len(weather)):
                        for j in range(len(ground_status)):
                            print(weather[i] + "-" + ground_status[j])
                            gt_r1_list = [] # 1位のgoal_timeのリスト
                            gt_r2_list = [] # 2位のgoal_timeのリスト
                            gt_r3_list = [] # 3位のgoal_timeのリスト
                            row = 0
                            while True:
                                if len(horse_data) == row:
                                    break

                                ri = horse_data.iat[row,col_ri]
                                r = horse_data.iat[row,col_r]
                                bw = horse_data.iat[row,col_bw]
                                if ri in ri_mtx[i][j] and r == 1:
                                    gt_r1_list.append(horse_data.iat[row,col_gt])       # 1st
                                    gt_r2_list.append(horse_data.iat[row + 1,col_gt])   # 2nd
                                    gt_r3_list.append(horse_data.iat[row + 2,col_gt])   # 3rd
                                    row += 3
                                else:
                                    row += 1
                            for k in range(len(gt_r1_list)):
                                tmp = (gt_r1_list[k] + gt_r2_list[k] + gt_r3_list[k]) / 3
                                ave_time_mtx[i][j].append(tmp)

                # 描画
                fig, axes = plt.subplots(nrows=len(weather), ncols=len(ground_status), sharex=False)
                for i in range(len(weather)):
                    for j in range(len(ground_status)):
                        ave_ = 0.0
                        if len(ave_time_mtx[i][j]) != 0:
                            ave_ = sum(ave_time_mtx[i][j])/len(ave_time_mtx[i][j])
                        axes[i,j].set_title("{}-{}-{:.3f}({})".format(weather[i], ground_status[j], ave_, len(ave_time_mtx[i][j])))
                        axes[i,j].hist(ave_time_mtx[i][j])
                        axes[i,j].tick_params(axis='x', labelrotation=45)

                #plt.show()
                plt.tight_layout()
                plt.savefig("{}-{}-{}.png".format(place[idx_p], distance[idx_d], race_course_gnd[idx_rcg]))
                plt.close()


    return 




if __name__ == '__main__':

    calcGoalTimeDistribution(["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"], [1200,1800,2200,3000], ["T","D"], ["S","C","R0","R1"], ["G","H0","H1","B"])



