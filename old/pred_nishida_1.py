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

# Train data    25000 ~ 121050 (80%)
# Test data     1000 ~ 24000 (20%)


# ベースタイムの計算
def calcBaseTimeFigure(place, distance, race_course_gnd):
    csv_dir = "../data/all"
    horse_file_list = natsorted(glob.glob(csv_dir+"/*horse*"))
    race_file_list = natsorted(glob.glob(csv_dir+"/*race*"))
    file_list = np.vstack((horse_file_list, race_file_list)).T

    base_time_list = [] # ベースタイム
    ri_list = [] # 指定の競馬場　かつ　指定の距離　かつ　１，２勝クラス　かつ　芝ダ障　のrace_idをリストにする
    for file in file_list:
        race_file_name = os.path.split(file[1])[1]
        race_data = pd.read_csv(csv_dir+"/"+race_file_name,sep=",")
        col_ri = race_data.columns.get_loc('race_id')
        col_rt = race_data.columns.get_loc('race_title')
        col_rcm = race_data.columns.get_loc('race_course_m')
        col_wr = race_data.columns.get_loc('where_racecourse')
        col_rcg = race_data.columns.get_loc('race_course_gnd')
        for row in range(len(race_data)):
            ri = race_data.iat[row,col_ri]
            rt = race_data.iat[row,col_rt]
            rcm = race_data.iat[row,col_rcm]
            wr = race_data.iat[row,col_wr]
            rcg = race_data.iat[row,col_rcg]
            if rcg == race_course_gnd:
                if rt == "W1" or rt == "W2" or rt == "WX":
                    if rcm == distance:
                        if place in wr:
                            ri_list.append(ri)

    # 上記の条件のヒット数が1以下であれば、指定の競馬場　かつ　指定の距離　かつ　芝ダ障　のrace_idをリストにする
    if len(ri_list) < 2:
        print("[base_time] conditions did not hit !")
        ri_list = []
        for file in file_list:
            race_file_name = os.path.split(file[1])[1]
            race_data = pd.read_csv(csv_dir+"/"+race_file_name,sep=",")
            col_ri = race_data.columns.get_loc('race_id')
            col_rt = race_data.columns.get_loc('race_title')
            col_rcm = race_data.columns.get_loc('race_course_m')
            col_wr = race_data.columns.get_loc('where_racecourse')
            col_rcg = race_data.columns.get_loc('race_course_gnd')
            for row in range(len(race_data)):
                ri = race_data.iat[row,col_ri]
                rt = race_data.iat[row,col_rt]
                rcm = race_data.iat[row,col_rcm]
                wr = race_data.iat[row,col_wr]
                rcg = race_data.iat[row,col_rcg]
                if rcg == race_course_gnd:
                    if rcm == distance:
                        if place in wr:
                            ri_list.append(ri)

    # 指定の競馬場　かつ　指定の距離　かつ　１，２勝クラス　かつ　芝ダ障　における1〜3位タイム平均を求める
    for file in file_list:
        horse_file_name = os.path.split(file[0])[1]
        horse_data = pd.read_csv(csv_dir+"/"+horse_file_name,sep=",")
        col_ri = horse_data.columns.get_loc('race_id')
        col_gt = horse_data.columns.get_loc('goal_time')
        col_r = horse_data.columns.get_loc('rank')
        col_bw = horse_data.columns.get_loc('burden_weight')
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
            if ri in ri_list and r == 1:
                gt_r1_list.append(horse_data.iat[row,col_gt])       # 1st
                gt_r2_list.append(horse_data.iat[row + 1,col_gt])   # 2nd
                gt_r3_list.append(horse_data.iat[row + 2,col_gt])   # 3rd
                row += 3
            else:
                row += 1

        for i in range(len(gt_r1_list)):
            tmp = (gt_r1_list[i] + gt_r2_list[i] + gt_r3_list[i]) / 3
            base_time_list.append(tmp)

    base_time = statistics.mean(base_time_list)
    std_base_time = statistics.pstdev(base_time_list)
    
    return base_time, std_base_time



# 距離指数の計算
def calcDistanceFigure(base_time):
    return 100 / base_time



# 馬場指数の計算 TODO
def calcGndFigure(base_time, std_base_time, place, distance, race_course_gnd, weather, ground_status):
    csv_dir = "../data/all"
    horse_file_list = natsorted(glob.glob(csv_dir+"/*horse*"))
    race_file_list = natsorted(glob.glob(csv_dir+"/*race*"))
    file_list = np.vstack((horse_file_list, race_file_list)).T

    ave_time_list = [] # 1〜3位平均タイム
    ri_list = [] # 指定の競馬場　かつ　指定の距離　かつ　芝ダ障天候馬場　のrace_idをリストにする
    for file in file_list:
        race_file_name = os.path.split(file[1])[1]
        race_data = pd.read_csv(csv_dir+"/"+race_file_name,sep=",")
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
            if rcm == distance and place in wr and race_course_gnd in rcg and w == weather and gs == ground_status:
                ri_list.append(ri)

    # 上記の条件のヒット数が1以下であれば、天候の条件を無視
    if len(ri_list) < 2:
        print("[ri_list] conditions conditions did not hit !")
        ri_list = []
        for file in file_list:
            race_file_name = os.path.split(file[1])[1]
            race_data = pd.read_csv(csv_dir+"/"+race_file_name,sep=",")
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
                if rcm == distance and place in wr and race_course_gnd in rcg and gs == ground_status:
                    ri_list.append(ri)

    # 上記の条件のヒット数が1以下であれば、None
    if len(ri_list) < 2:

        return None

    # 指定の競馬場　かつ　指定の距離　かつ　芝ダ障天候馬場　における1〜3位タイム平均を求める
    for file in file_list:
        horse_file_name = os.path.split(file[0])[1]
        horse_data = pd.read_csv(csv_dir+"/"+horse_file_name,sep=",")
        col_ri = horse_data.columns.get_loc('race_id')
        col_gt = horse_data.columns.get_loc('goal_time')
        col_r = horse_data.columns.get_loc('rank')
        col_bw = horse_data.columns.get_loc('burden_weight')
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
            if ri in ri_list and r == 1:
                gt_r1_list.append(horse_data.iat[row,col_gt])       # 1st
                gt_r2_list.append(horse_data.iat[row + 1,col_gt])   # 2nd
                gt_r3_list.append(horse_data.iat[row + 2,col_gt])   # 3rd
                row += 3
            else:
                row += 1
        for k in range(len(gt_r1_list)):
            tmp = (gt_r1_list[k] + gt_r2_list[k] + gt_r3_list[k]) / 3
            ave_time_list.append(tmp)

    if len(ave_time_list) == 0:
        diff_time = 0
    else:
        ave_time = statistics.mean(ave_time_list)
        std_time = statistics.pstdev(ave_time_list)
        stand_base_time = (ave_time - base_time) / std_base_time    # ベースタイムからの標準正規分布におけるave_timeの記録
        stand_time = (base_time - ave_time) / std_time              # ave_timeからの標準正規分布におけるベースタイムの記録
        diff_time = stand_base_time - stand_time                    # ベースタイムより良いタイムが出る馬場だと、数値が低くなる。https://regist.netkeiba.com/?pid=faq_detail&id=1295

    return diff_time * 10   # 指数として出力するため10かけている



def calcSpeedFigure(place, distance, race_course_gnd, weather, ground_status, goal_time, burden_weight):
    # ゴールタイム表記変換
    gt = goal_time.split(":")
    if len(gt) == 1:
        time = float(gt[0])
    elif len(gt) == 2:
        time = float(gt[1]) + float(gt[0])*60
    else:
        time = None
    goal_time = time
    print("goal_time = {}".format(goal_time))
    # ベースタイム算出
    base_time, std_base_time = calcBaseTimeFigure(place, distance, race_course_gnd)
    print("base_time = {}".format(base_time))
    # 距離指数算出
    df = calcDistanceFigure(base_time)
    if df == None:

        return None

    print("df = {}".format(df))
    # 馬場指数算出
    gf = calcGndFigure(base_time, std_base_time, place, distance, race_course_gnd, weather, ground_status)
    print("gf = {}".format(gf))
    # スピード指数算出
    speed_figure = (base_time*10 - goal_time*10) * df + gf + (burden_weight - 55) * 2 + 80
    print("speed_figure = {}".format(speed_figure))

    return speed_figure



# csvデータの読み込み
def read_csv_data(csv_dir):
    horse_file_list = natsorted(glob.glob(csv_dir+"/*horse*"))
    race_file_list = natsorted(glob.glob(csv_dir+"/*race*"))

    # レースデータのファイル読み込み
    race_data_list = []
    with Pool() as p:
        race_data_list = p.map(pd.read_csv, race_file_list)
    # 馬データのファイル読み込み
    horse_data_list = []
    with Pool() as p:
        horse_data_list = p.map(pd.read_csv, horse_file_list)

    return race_data_list, horse_data_list



def scrapHorseRaceData(horse_name):
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    URL = "https://db.netkeiba.com/?pid=horse_search_detail"
    driver.get(URL)
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    # 馬名を入力
    driver.find_element_by_class_name('field').send_keys(horse_name)

    # フォームを送信
    frm = driver.find_element_by_css_selector("#db_search_detail_form > form")
    frm.submit()
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    if "検索結果" in driver.title:
        all_rows = driver.find_element_by_class_name('nk_tb_common').find_elements_by_tag_name("tr")
        horse_url = all_rows[1].find_element_by_tag_name("a").get_attribute("href")
        print("go to " + horse_url)
        driver.get(horse_url)
        time.sleep(1)
        wait.until(EC.presence_of_all_elements_located)

    # 馬のレース成績をリストに保存
    horse_race_data_list = []
    wait.until(EC.presence_of_all_elements_located)
    all_rows = driver.find_element_by_class_name('db_h_race_results').find_elements_by_tag_name("tr")
    for row in range(1, len(all_rows)):
        place = all_rows[row].find_elements_by_tag_name("td")[1].find_element_by_tag_name("a").text[1:3]
        w = all_rows[row].find_elements_by_tag_name("td")[2].text
        weather = ""
        if "晴" in w:
            weather = "S"
        elif "曇" in w:
            weather = "C"
        elif "小雨" in w:
            weather = "R0"
        elif "雨" in w:
            weather = "R1"
        burden_weight = int(all_rows[row].find_elements_by_tag_name("td")[13].text)
        c_gnd = all_rows[row].find_elements_by_tag_name("td")[14].text[0]
        race_course_gnd = ""
        if "芝" in c_gnd:
            race_course_gnd = "T"
        elif "ダ" in c_gnd:
            race_course_gnd = "D"
        if "障" in c_gnd:
            race_course_gnd = "O"
        distance = int(all_rows[row].find_elements_by_tag_name("td")[14].text[1:])
        gs = all_rows[row].find_elements_by_tag_name("td")[15].text
        ground_status = ""
        if "不良" in gs:
            ground_status = "B"
        elif "稍" in gs:
            ground_status = "H0"
        elif "重" in gs:
            ground_status = "H1"
        elif "良" in gs:
            ground_status = "G"
        goal_time = all_rows[row].find_elements_by_tag_name("td")[17].text
        horse_race_data_list.append([place, weather, burden_weight, race_course_gnd, distance, ground_status, goal_time])

    return horse_race_data_list




def get_unique_list(seq):
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]



if __name__ == '__main__':

    start = time.time()

    
    # 馬のスピード指数を算出
    horse_name_list = ["ワールドプレミア", "ディープボンド", "カレンブーケドール", "アリストテレス", "ウインマリリン", "ディアスティマ", "ユーキャンスマイル", "マカヒキ", "ナムラドノヴァン", "オーソリティ", "メロディーレーン", "ゴースト", "オセアグレイト", "メイショウテンゲン", "ディバインフォース", "シロニイ", "ジャコマル"]
    start = time.time()
    for i in range(len(horse_name_list)):
        print(horse_name_list[i])

        # 馬の過去の戦績をスクレイピング
        horse_race_data_list = scrapHorseRaceData(horse_name_list[i])
        print("scraping is end.")
        print(horse_race_data_list)
        #tmp = horse_race_data_list[0]
        #horse_race_data_list[0] = horse_race_data_list[4]
        #horse_race_data_list[4] = tmp

        # 馬のスピード指数の平均と標準偏差を算出
        speed_figure_list = []
        for j in range(len(horse_race_data_list)):
            place = horse_race_data_list[j][0]
            print(place)
            if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
                weather = horse_race_data_list[j][1]
                burden_weight = horse_race_data_list[j][2]
                race_course_gnd = horse_race_data_list[j][3]
                distance = horse_race_data_list[j][4]
                ground_status = horse_race_data_list[j][5]
                goal_time = horse_race_data_list[j][6]
                speed_figure = calcSpeedFigure(place, distance, race_course_gnd, weather, ground_status, goal_time, burden_weight)
                if speed_figure == None:

                    continue
                    
                speed_figure_list.append(speed_figure)

        ave_speed_figure = statistics.mean(speed_figure_list)
        std_speed_figure = statistics.pstdev(speed_figure_list)

        print(ave_speed_figure)
        print(std_speed_figure)
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}[sec]".format(elapsed_time))

    
    """

    nakken@nakken-desktop:~/programming/hobby/keiba/v2/old$ python pred_nishida.py
    ワールドプレミア
    go to https://db.netkeiba.com/horse/2016104854/
    scraping is end.
    [['阪神', 'S', 58, 'T', 3200, 'G', '3:14.7'], ['中山', 'S', 57, 'T', 2500, 'G', '2:33.4'], ['中山', 'S', 57, 'T', 2500, 'G', '2:35.6'], ['東京', 'C', 57, 'T', 2400, 'G', '2:23.8'], ['中山', 'C', 55, 'T', 2500, 'G', '2:31.4'], ['京都', 'S', 57, 'T', 3000, 'G', '3:06.0'], ['阪神', 'R0', 56, 'T', 2400, 'G', '2:27.5'], ['阪神', 'S', 56, 'T', 2000, 'H0', '2:02.6'], ['京都', 'S', 56, 'T', 1800, 'G', '1:47.3'], ['京都', 'S', 55, 'T', 2000, 'G', '2:02.2'], ['京都', 'S', 55, 'T', 1800, 'G', '1:48.0']]
    阪神
    goal_time = 194.7
    [base_time] conditions did not hit !
    Traceback (most recent call last):
    File "pred_nishida.py", line 382, in <module>
        speed_figure = calcSpeedFigure(place, distance, race_course_gnd, weather, ground_status, goal_time, burden_weight)
    File "pred_nishida.py", line 235, in calcSpeedFigure
        base_time, std_base_time = calcBaseTimeFigure(place, distance, race_course_gnd)
    File "pred_nishida.py", line 111, in calcBaseTimeFigure
        base_time = statistics.mean(base_time_list)
    File "/usr/lib/python3.6/statistics.py", line 311, in mean
        raise StatisticsError('mean requires at least one data point')
    statistics.StatisticsError: mean requires at least one data point

    """