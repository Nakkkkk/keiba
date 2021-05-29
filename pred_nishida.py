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
import sqlite3

# Train data    25000 ~ 121050 (80%)
# Test data     1000 ~ 24000 (20%)



# 距離指数の計算
def calcDistanceFigure(base_time):
    return 100 / base_time



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



# ベースタイムと馬場指数の計算 TODO
def calcBaseTimeFigureAndGndFigure(race_data_list, horse_data_list, place, distance, race_course_gnd, weather, ground_status):
    ave_time_list = [] # 1〜3位平均タイム
    base_time_list = [] # ベースタイム
    bt_ri_list = [] # ベースタイム用のrace_idリスト
    gf_ri_list = [] # 馬場指数用のrace_idリスト


    # ベースタイム　と　馬場指数　のデータベースと照合
    # データベースにデータがあれば、それをリターン
    db_list = readDatabeseBaseTimeFigureAndGndFigure()
    horse_race_data_list_shr_trim = []
    for i in range(len(db_list)):
        if db_list[i][1] == place and \
           db_list[i][2] == distance and \
           db_list[i][3] == race_course_gnd and \
           db_list[i][4] == weather and \
           db_list[i][5] == ground_status:

            print("REUSE")
            
            return db_list[i][6], db_list[i][7]


    # ベースタイムと馬場指数の計算に使うrace_idの検索
    for race_data in race_data_list:
        col_ri = race_data.columns.get_loc('race_id')
        col_rt = race_data.columns.get_loc('race_title')
        col_rcg = race_data.columns.get_loc('race_course_gnd')
        col_w = race_data.columns.get_loc('weather')
        col_gs = race_data.columns.get_loc('ground_status')
        col_rcm = race_data.columns.get_loc('race_course_m')
        col_wr = race_data.columns.get_loc('where_racecourse')
        for row in range(len(race_data)):
            ri = race_data.iat[row,col_ri]
            rt = race_data.iat[row,col_rt]
            rcg = race_data.iat[row,col_rcg]
            w = race_data.iat[row,col_w]
            gs = race_data.iat[row,col_gs]
            rcm = race_data.iat[row,col_rcm]
            wr = race_data.iat[row,col_wr]
            # 馬場指数
            if rcm == distance and place in wr and race_course_gnd in rcg and w == weather and gs == ground_status:
                gf_ri_list.append(ri)
            # ベースタイム
            if rcg == race_course_gnd:
                if rt == "W1" or rt == "W2" or rt == "WX":
                    if rcm == distance:
                        if place in wr:
                            bt_ri_list.append(ri)

    # [馬場指数] 上記の条件のヒット数が1以下であれば、指定の競馬場　かつ　指定の距離　かつ　芝ダ障　のrace_idをリストにする
    if len(gf_ri_list) < 2:
        print("[gf_ri_list] conditions did not hit !")
        gf_ri_list = []
        for race_data in race_data_list:
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
                    gf_ri_list.append(ri)

    # [ベースタイム] 上記の条件のヒット数が1以下であれば、天候の条件を無視
    if len(bt_ri_list) < 2:
        print("[base_time] conditions did not hit !")
        bt_ri_list = []
        for race_data in race_data_list:
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
                            bt_ri_list.append(ri)


    gf_ri_list_sort = natsorted(gf_ri_list, reverse=True)
    bt_ri_list_sort = natsorted(bt_ri_list, reverse=True)
    gf_ri_list_idx = 0
    bt_ri_list_idx = 0
    # 指定の競馬場　かつ　指定の距離　かつ　芝ダ障天候馬場　における1〜3位タイム平均を求める
    for horse_data in horse_data_list:
        col_ri = horse_data.columns.get_loc('race_id')
        col_gt = horse_data.columns.get_loc('goal_time')
        col_r = horse_data.columns.get_loc('rank')
        col_bw = horse_data.columns.get_loc('burden_weight')
        row = 0
        while True:
            if len(horse_data) == row:
                break

            ri = horse_data.iat[row,col_ri]
            r = horse_data.iat[row,col_r]
            bw = horse_data.iat[row,col_bw]
            gf_ri_bool = False
            if len(gf_ri_list) != gf_ri_list_idx:
                gf_ri_bool = (ri == gf_ri_list_sort[gf_ri_list_idx] and r == 1)
            bt_ri_bool = False
            if len(bt_ri_list) != bt_ri_list_idx:
                bt_ri_bool = (ri == bt_ri_list_sort[bt_ri_list_idx] and r == 1)
            if gf_ri_bool or bt_ri_bool:
                ave_gt = (horse_data.iat[row,col_gt] + horse_data.iat[row + 1,col_gt] + horse_data.iat[row + 2,col_gt]) / 3
                if gf_ri_bool and len(gf_ri_list) != gf_ri_list_idx:
                    ave_time_list.append(ave_gt)
                    gf_ri_list_idx += 1
                if bt_ri_bool and len(bt_ri_list) != bt_ri_list_idx:
                    base_time_list.append(ave_gt)
                    bt_ri_list_idx += 1
                row += 3
            else:
                row += 1


    if len(gf_ri_list) != len(ave_time_list) or len(bt_ri_list) != len(base_time_list):
        
        print("")
        print("")
        print("#######    len(gf_ri_list) != len(ave_time_list) or len(bt_ri_list) != len(base_time_list)")
        print("")
        print("")

        return

    # ベースタイム
    base_time = statistics.mean(base_time_list)
    std_base_time = statistics.pstdev(base_time_list)

    # 馬場指数
    if len(ave_time_list) < 2:
        gnd_figure = "NULL"
    else:
        ave_time = statistics.mean(ave_time_list)
        std_time = statistics.pstdev(ave_time_list)
        stand_base_time = (ave_time - base_time) / std_base_time    # ベースタイムからの標準正規分布におけるave_timeの記録
        stand_time = (base_time - ave_time) / std_time              # ave_timeからの標準正規分布におけるベースタイムの記録
        diff_time = stand_base_time - stand_time                    # ベースタイムより良いタイムが出る馬場だと、数値が低くなる。https://regist.netkeiba.com/?pid=faq_detail&id=1295
        gnd_figure = diff_time * 10


    # データベースに計算結果を保存
    updateDatabeseBaseTimeFigureAndGndFigure(place, distance, race_course_gnd, weather, ground_status, base_time, gnd_figure)


    return base_time, gnd_figure   # 指数として出力するため10かけている



def scrHorseRaceData(race_url):
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    driver.get(race_url) # 速度ボトルネック
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)
    all_race_rows = driver.find_element_by_class_name('Shutuba_Table').find_elements_by_tag_name("tr")
    horse_name_list = []
    horse_url_list = []
    jockey_name_list = []
    jockey_url_list = []
    for r_row in range(2,len(all_race_rows)):
        horse_name_list.append(all_race_rows[r_row].find_element_by_class_name('HorseInfo').find_element_by_tag_name("a").get_attribute("title"))
        horse_url_list.append(all_race_rows[r_row].find_element_by_class_name('HorseInfo').find_element_by_tag_name("a").get_attribute("href"))
        jockey_name_list.append(all_race_rows[r_row].find_element_by_class_name('Jockey').find_element_by_tag_name("a").get_attribute("title"))
        jockey_url_list.append(all_race_rows[r_row].find_element_by_class_name('Jockey').find_element_by_tag_name("a").get_attribute("href"))

    # 馬のレース成績をリストに保存
    horse_race_data_list = []
    for r_row in range(len(horse_name_list)):
        print(horse_name_list[r_row])
        driver.get(horse_url_list[r_row])
        time.sleep(1)
        wait.until(EC.presence_of_all_elements_located)
        all_horse_rows = driver.find_element_by_class_name('db_h_race_results').find_elements_by_tag_name("tr")

        tmp_horse_race_data_list = []
        for h_row in range(1, len(all_horse_rows)):
            place = all_horse_rows[h_row].find_elements_by_tag_name("td")[1].find_element_by_tag_name("a").text[1:3]
            w = all_horse_rows[h_row].find_elements_by_tag_name("td")[2].text
            weather = ""
            if "晴" in w:
                weather = "S"
            elif "曇" in w:
                weather = "C"
            elif "小雨" in w:
                weather = "R0"
            elif "雨" in w:
                weather = "R1"
            burden_weight = float(all_horse_rows[h_row].find_elements_by_tag_name("td")[13].text)
            c_gnd = all_horse_rows[h_row].find_elements_by_tag_name("td")[14].text[0]
            race_course_gnd = ""
            if "芝" in c_gnd:
                race_course_gnd = "T"
            elif "ダ" in c_gnd:
                race_course_gnd = "D"
            if "障" in c_gnd:
                race_course_gnd = "O"
            distance = float(all_horse_rows[h_row].find_elements_by_tag_name("td")[14].text[1:])
            gs = all_horse_rows[h_row].find_elements_by_tag_name("td")[15].text
            ground_status = ""
            if "不良" in gs:
                ground_status = "B"
            elif "稍" in gs:
                ground_status = "H0"
            elif "重" in gs:
                ground_status = "H1"
            elif "良" in gs:
                ground_status = "G"
            goal_time = all_horse_rows[h_row].find_elements_by_tag_name("td")[17].text
            tmp_horse_race_data_list.append([place, weather, burden_weight, race_course_gnd, distance, ground_status, goal_time])
        horse_race_data_list.append(tmp_horse_race_data_list)


    # ジョッキーのレース成績をリストに保存（直近200試合を参照）
    jockey_race_data_list = []
    for r_row in range(len(jockey_name_list)):
        print(jockey_name_list[r_row])
        driver.get(jockey_url_list[r_row])

        cnt = 0
        while True:
            time.sleep(1)
            wait.until(EC.presence_of_all_elements_located)
            all_jockey_rows = driver.find_element_by_class_name('race_table_01').find_elements_by_tag_name("tr")

            tmp_jockey_race_data_list = []
            for j_row in range(1, len(all_jockey_rows)):
                place = all_jockey_rows[j_row].find_elements_by_tag_name("td")[1].find_element_by_tag_name("a").text[1:3]
                w = all_jockey_rows[j_row].find_elements_by_tag_name("td")[2].text
                weather = ""
                if "晴" in w:
                    weather = "S"
                elif "曇" in w:
                    weather = "C"
                elif "小雨" in w:
                    weather = "R0"
                elif "雨" in w:
                    weather = "R1"
                burden_weight = float(all_jockey_rows[j_row].find_elements_by_tag_name("td")[13].text)
                c_gnd = all_jockey_rows[j_row].find_elements_by_tag_name("td")[14].text[0]
                race_course_gnd = ""
                if "芝" in c_gnd:
                    race_course_gnd = "T"
                elif "ダ" in c_gnd:
                    race_course_gnd = "D"
                if "障" in c_gnd:
                    race_course_gnd = "O"
                distance = float(all_jockey_rows[j_row].find_elements_by_tag_name("td")[14].text[1:])
                gs = all_jockey_rows[j_row].find_elements_by_tag_name("td")[15].text
                ground_status = ""
                if "不良" in gs:
                    ground_status = "B"
                elif "稍" in gs:
                    ground_status = "H0"
                elif "重" in gs:
                    ground_status = "H1"
                elif "良" in gs:
                    ground_status = "G"
                goal_time = all_jockey_rows[j_row].find_elements_by_tag_name("td")[16].text
                tmp_jockey_race_data_list.append([place, weather, burden_weight, race_course_gnd, distance, ground_status, goal_time])
            jockey_race_data_list.append(tmp_jockey_race_data_list)

            cnt += 1
            if cnt > 11:
                break

            try:
                target = driver.find_elements_by_link_text("次")[0]
                #print(driver.find_elements_by_link_text("次"))
                driver.execute_script("arguments[0].click();", target) #javascriptでクリック処理
            except IndexError:
                break

    return horse_race_data_list, horse_name_list, jockey_race_data_list, jockey_name_list




def makeDatabeseBaseTimeFigureAndGndFigure():
    # DBを作成する
    # すでに存在していれば、それにアスセスする。
    dbname = 'BaseTimeAndGndFigure.db'
    conn = sqlite3.connect(dbname)
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

    # DBにアスセス
    conn = sqlite3.connect(dbname)
    # sqliteを操作するカーソルオブジェクトを作成
    cur = conn.cursor()

    # btgfというtableを作成
    try:
        cur.execute('CREATE TABLE btgf( \
        id INTEGER PRIMARY KEY AUTOINCREMENT, \
        place STRING, \
        distance INTEGER, \
        race_course_gnd STRING, \
        weather STRING, \
        ground_status STRING, \
        basetime REAL, \
        gndfigure REAL \
        )')
    except(sqlite3.OperationalError):
        pass
    # データベースへコミット。これで変更が反映される。
    conn.commit()
    conn.close()



def updateDatabeseBaseTimeFigureAndGndFigure(place, distance, race_course_gnd, weather, ground_status, basetime, gndfigure):
    dbname = 'BaseTimeAndGndFigure.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    # データを入力 OR 更新
    cur.execute('SELECT * FROM btgf WHERE place = "{}" AND distance = {} AND race_course_gnd = "{}" AND weather = "{}" AND ground_status = "{}"'.format(place, distance, race_course_gnd, weather, ground_status))
    row_fetched = cur.fetchall()
    if len(row_fetched) == 0:
        print("INSERT")
        cur.execute('INSERT INTO btgf(place, distance, race_course_gnd, weather, ground_status, basetime, gndfigure) \
        values("{}",{},"{}","{}","{}",{},{})'.format(place, distance, race_course_gnd, weather, ground_status, basetime, gndfigure))
    else:
        print("UPDATE")
        cur.execute('UPDATE btgf SET basetime = {}, gndfigure = {} WHERE id = {}'.format(basetime, gndfigure, row_fetched[0][0]))

    conn.commit()

    cur.close()
    conn.close()



def readDatabeseBaseTimeFigureAndGndFigure():
    dbname = 'BaseTimeAndGndFigure.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    cur.execute('SELECT * FROM btgf')
    row_fetched = cur.fetchall()

    cur.close()
    conn.close()

    return row_fetched



def get_unique_list(seq):
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]



if __name__ == '__main__':

    start = time.time()


    # ベースタイム　と　馬場指数　のデータベースを作成
    makeDatabeseBaseTimeFigureAndGndFigure()
    
    # csvデータの読み込み
    csv_dir = "../data/all"
    race_data_list, horse_data_list = read_csv_data(csv_dir)
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))


    # 出走馬、ジョッキーの過去の戦績
    race_url = "https://race.netkeiba.com/race/shutuba.html?race_id=202105020811&rf=race_submenu"
    horse_race_data_list, horse_name_list, jockey_race_data_list, jockey_name_list = scrHorseRaceData(race_url)

    # 出走馬の過去の戦績（重複なし）
    horse_race_data_list_shr = []
    for i in range(len(horse_race_data_list)):
        for j in range(len(horse_race_data_list[i])):
            place = horse_race_data_list[i][j][0]
            if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
                weather = horse_race_data_list[i][j][1]
                burden_weight = horse_race_data_list[i][j][2]
                race_course_gnd = horse_race_data_list[i][j][3]
                distance = horse_race_data_list[i][j][4]
                ground_status = horse_race_data_list[i][j][5]
                goal_time = horse_race_data_list[i][j][6]
                horse_race_data_list_shr.append([place, distance, race_course_gnd, weather, ground_status])
    horse_race_data_list_shr = get_unique_list(horse_race_data_list_shr)
    print("len horse_race_data_list_shr:{}".format(len(horse_race_data_list_shr)))
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))


    # 出走馬の過去の戦績（重複なし）に対する　ベースタイム　と　馬場指数
    horse_base_time_and_gnd_figure_list = []
    for i in range(len(horse_race_data_list_shr)):
        base_time, gf = calcBaseTimeFigureAndGndFigure(race_data_list, horse_data_list, horse_race_data_list_shr[i][0], horse_race_data_list_shr[i][1], horse_race_data_list_shr[i][2], horse_race_data_list_shr[i][3], horse_race_data_list_shr[i][4])
        #print("base_time = {}".format(base_time))
        #print("gf = {}".format(gf))
        horse_base_time_and_gnd_figure_list.append([base_time, gf])
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))


    # スピード指数の計算
    horse_result = []
    for i in range(len(horse_name_list)):
        try:
            print(horse_name_list[i])
            print("")
            # 出走馬の過去の戦績
            horse_race_data = horse_race_data_list[i]
            speed_figure_list = []
            for j in range(len(horse_race_data)):
                place = horse_race_data[j][0]
                if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
                    weather = horse_race_data[j][1]
                    burden_weight = horse_race_data[j][2]
                    race_course_gnd = horse_race_data[j][3]
                    distance = horse_race_data[j][4]
                    ground_status = horse_race_data[j][5]
                    goal_time = horse_race_data[j][6]
                    try:
                        idx = horse_race_data_list_shr.index([place, distance, race_course_gnd, weather, ground_status])
                        tmp = horse_base_time_and_gnd_figure_list[idx]
                        base_time = tmp[0]
                        gf = tmp[1]

                        # ゴールタイム表記変換
                        gt = goal_time.split(":")
                        if len(gt) == 1:
                            goal_time = float(gt[0])
                        elif len(gt) == 2:
                            goal_time = float(gt[1]) + float(gt[0])*60
                        else:
                            goal_time = None
                        print("goal_time = {}".format(goal_time))
                        # ベースタイム算出
                        print("base_time = {}".format(base_time))
                        # 距離指数算出
                        df = calcDistanceFigure(base_time)
                        print("df = {}".format(df))
                        # 馬場指数算出
                        if gf == None:

                            continue

                        print("gf = {}".format(gf))
                        # スピード指数算出
                        speed_figure = (base_time*10 - goal_time*10) * df + gf + (burden_weight - 55) * 2 + 80
                        print("speed_figure = {}".format(speed_figure))

                        speed_figure_list.append(speed_figure)

                    except:
                        print("can not find")
                        print([place, distance, race_course_gnd, weather, ground_status])

            ave_speed_figure = statistics.mean(speed_figure_list)
            std_speed_figure = statistics.pstdev(speed_figure_list)
            print("[ave] speed_figure = {}".format(ave_speed_figure))
            print("[std] speed_figure = {}".format(std_speed_figure))

            horse_result.append([horse_name_list[i], ave_speed_figure])

        except Exception as e:
            print('=== エラー内容 ===')
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('e自身:' + str(e))
            print(horse_result)


    print("## org ##")
    print(horse_result)
    print("## sorted ##")
    print(sorted(horse_result, reverse=True, key=lambda x: x[1]))
    elapsed_time = time.time() - start
    print("elapsed_time:{0}[sec]".format(elapsed_time))
    

    # ジョッキーの過去の戦績（重複なし）
    jockey_race_data_list_shr = []
    for i in range(len(jockey_race_data_list)):
        for j in range(len(jockey_race_data_list[i])):
            place = jockey_race_data_list[i][j][0]
            if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
                weather = jockey_race_data_list[i][j][1]
                burden_weight = jockey_race_data_list[i][j][2]
                race_course_gnd = jockey_race_data_list[i][j][3]
                distance = jockey_race_data_list[i][j][4]
                ground_status = jockey_race_data_list[i][j][5]
                goal_time = jockey_race_data_list[i][j][6]
                jockey_race_data_list_shr.append([place, distance, race_course_gnd, weather, ground_status])
    jockey_race_data_list_shr = get_unique_list(jockey_race_data_list_shr)
    print("len jockey_race_data_list_shr:{}".format(len(jockey_race_data_list_shr)))
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))


    # ジョッキーの過去の戦績（重複なし）に対する　ベースタイム　と　馬場指数
    jockey_base_time_and_gnd_figure_list = []
    for i in range(len(jockey_race_data_list_shr)):
        base_time, gf = calcBaseTimeFigureAndGndFigure(race_data_list, horse_data_list, jockey_race_data_list_shr[i][0], jockey_race_data_list_shr[i][1], jockey_race_data_list_shr[i][2], jockey_race_data_list_shr[i][3], jockey_race_data_list_shr[i][4])
        jockey_base_time_and_gnd_figure_list.append([base_time, gf])
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))

    # スピード指数の計算
    jockey_result = []
    for i in range(len(jockey_name_list)):
        try:
            print(jockey_name_list[i])
            print("")
            # 出走馬の過去の戦績
            jockey_race_data = jockey_race_data_list[i]
            speed_figure_list = []
            for j in range(len(jockey_race_data)):
                place = jockey_race_data[j][0]
                if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
                    weather = jockey_race_data[j][1]
                    burden_weight = jockey_race_data[j][2]
                    race_course_gnd = jockey_race_data[j][3]
                    distance = jockey_race_data[j][4]
                    ground_status = jockey_race_data[j][5]
                    goal_time = jockey_race_data[j][6]
                    try:
                        idx = jockey_race_data_list_shr.index([place, distance, race_course_gnd, weather, ground_status])
                        tmp = jockey_base_time_and_gnd_figure_list[idx]
                        base_time = tmp[0]
                        gf = tmp[1]

                        # ゴールタイム表記変換
                        gt = goal_time.split(":")
                        if len(gt) == 1:
                            goal_time = float(gt[0])
                        elif len(gt) == 2:
                            goal_time = float(gt[1]) + float(gt[0])*60
                        else:
                            goal_time = None
                        print("goal_time = {}".format(goal_time))
                        # ベースタイム算出
                        print("base_time = {}".format(base_time))
                        # 距離指数算出
                        df = calcDistanceFigure(base_time)
                        print("df = {}".format(df))
                        # 馬場指数算出
                        if gf == None:

                            continue

                        print("gf = {}".format(gf))
                        # スピード指数算出
                        speed_figure = (base_time*10 - goal_time*10) * df + gf + (burden_weight - 55) * 2 + 80
                        print("speed_figure = {}".format(speed_figure))

                        speed_figure_list.append(speed_figure)

                    except:
                        print("can not find")
                        print([place, distance, race_course_gnd, weather, ground_status])

            ave_speed_figure = statistics.mean(speed_figure_list)
            std_speed_figure = statistics.pstdev(speed_figure_list)
            print("[ave] speed_figure = {}".format(ave_speed_figure))
            print("[std] speed_figure = {}".format(std_speed_figure))

            jockey_result.append([jockey_name_list[i], ave_speed_figure])

        except Exception as e:
            print('=== エラー内容 ===')
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('e自身:' + str(e))
            print(jockey_result)

    print("## org ##")
    print(jockey_result)
    print("## sorted ##")
    print(sorted(jockey_result, reverse=True, key=lambda x: x[1]))
    elapsed_time = time.time() - start
    print("elapsed_time:{0}[sec]".format(elapsed_time))


    # 出走馬とジョッキーのスピード指数の平均をソートして表示
    total_result = []
    for i in range(len(horse_result)):
        total_result.append([(horse_result[i][1] + jockey_result[i][1]) / 2, horse_result[i][0], jockey_result[i][0]])
    total_result_ = sorted(total_result, reverse=True, key=lambda x: x[0])
    for i in range(len(total_result_)):
        print(total_result_[i])

