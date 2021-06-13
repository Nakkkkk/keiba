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
import logging
import sys




# 距離指数の計算
def calcDistanceFigure(base_time):
    return 100 / base_time



# 馬のSQLデータベースの読み込み
def readHorseSqlDatabase(sql_dir):
    dbname = '/Horse.db'
    conn = sqlite3.connect(sql_dir + dbname)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('SELECT * FROM horse order by race_id desc')
    horse_data_list = []
    for row in cur.fetchall():
        horse_data_list.append(dict(row))

    cur.close()
    conn.close()

    return horse_data_list



# レースのSQLデータベースの読み込み
def readRaceSqlDatabase(sql_dir):
    dbname = '/Race.db'
    conn = sqlite3.connect(sql_dir + dbname)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('SELECT * FROM race order by race_id desc')
    race_data_list = []
    for row in cur.fetchall():
        race_data_list.append(dict(row))

    cur.close()
    conn.close()

    return race_data_list



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
    for row in range(len(race_data_list)):
        ri = race_data_list[row]["race_id"]
        rt = race_data_list[row]["race_title"]
        rcg = race_data_list[row]["race_course_gnd"]
        w = race_data_list[row]["weather"]
        gs = race_data_list[row]["ground_status"]
        rcm = race_data_list[row]["race_course_m"]
        wr = race_data_list[row]["where_racecourse"]
        # 馬場指数
        if rcm == distance and place in wr and race_course_gnd in rcg and w == weather and gs == ground_status:
            gf_ri_list.append(ri)
        # ベースタイム
        if rcg == race_course_gnd:
            if rt == "W1" or rt == "W2" or rt == "WX":
                if rcm == distance:
                    if place in wr:
                        bt_ri_list.append(ri)

    # [ベースタイム] 上記の条件のヒット数が1以下であれば、天候の条件を無視
    if len(gf_ri_list) < 2:
        print("[gf_ri_list] conditions conditions did not hit !")
        gf_ri_list = []
        for row in range(len(race_data_list)):
            ri = race_data_list[row]["race_id"]
            rcg = race_data_list[row]["race_course_gnd"]
            w = race_data_list[row]["weather"]
            gs = race_data_list[row]["ground_status"]
            rcm = race_data_list[row]["race_course_m"]
            wr = race_data_list[row]["where_racecourse"]
            if rcm == distance and place in wr and race_course_gnd in rcg and gs == ground_status:
                gf_ri_list.append(ri)

    # [馬場指数] 上記の条件のヒット数が1以下であれば、指定の競馬場　かつ　指定の距離　かつ　芝ダ障　のrace_idをリストにする
    if len(bt_ri_list) < 2:
        print("[base_time] conditions did not hit !")
        bt_ri_list = []
        for row in range(len(race_data_list)):
            ri = race_data_list[row]["race_id"]
            rt = race_data_list[row]["race_title"]
            rcg = race_data_list[row]["race_course_gnd"]
            rcm = race_data_list[row]["race_course_m"]
            wr = race_data_list[row]["where_racecourse"]
            if rcg == race_course_gnd:
                if rcm == distance:
                    if place in wr:
                        bt_ri_list.append(ri)


    gf_ri_list_sort = natsorted(gf_ri_list, reverse=True)
    bt_ri_list_sort = natsorted(bt_ri_list, reverse=True)
    gf_ri_list_idx = 0
    bt_ri_list_idx = 0
    # 指定の競馬場　かつ　指定の距離　かつ　芝ダ障天候馬場　における1〜3位タイム平均を求める
    row = 0
    while True:
        if len(horse_data_list) == row:
            break

        ri = horse_data_list[row]["race_id"]
        r = horse_data_list[row]["rank"]

        gf_ri_bool = False
        if len(gf_ri_list) != gf_ri_list_idx:
            gf_ri_bool = (ri == gf_ri_list_sort[gf_ri_list_idx] and r == 1)
        bt_ri_bool = False
        if len(bt_ri_list) != bt_ri_list_idx:
            bt_ri_bool = (ri == bt_ri_list_sort[bt_ri_list_idx] and r == 1)
        if gf_ri_bool or bt_ri_bool:
            ave_gt = (horse_data_list[row]["goal_time"] + horse_data_list[row + 1]["goal_time"] + horse_data_list[row + 2]["goal_time"]) / 3
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
        if std_time == 0.0: # ave_time_listが全部同じ値だった時
            gnd_figure = "NULL"
        else:
            stand_base_time = (ave_time - base_time) / std_base_time    # ベースタイムからの標準正規分布におけるave_timeの記録
            stand_time = (base_time - ave_time) / std_time              # ave_timeからの標準正規分布におけるベースタイムの記録
            diff_time = stand_base_time - stand_time                    # ベースタイムより良いタイムが出る馬場だと、数値が低くなる。https://regist.netkeiba.com/?pid=faq_detail&id=1295
            gnd_figure = diff_time * 10


    # データベースに計算結果を保存
    updateDatabeseBaseTimeFigureAndGndFigure(place, distance, race_course_gnd, weather, ground_status, base_time, gnd_figure)


    return base_time, gnd_figure   # 指数として出力するため10かけている



def scrHorseAndJockeyRaceData(race_url):
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    driver.get(race_url) # 速度ボトルネック
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    # 開催レース情報の取得
    racedata01_rows = driver.find_element_by_class_name('RaceData01').find_elements_by_tag_name("span")
    racedata01_distance = int(racedata01_rows[0].text[-5:-1])
    racedata01_race_course_gnd = ""
    if "芝" in racedata01_rows[0].text[0]:
        racedata01_race_course_gnd = "T"
    elif "ダ" in racedata01_rows[0].text[0]:
        racedata01_race_course_gnd = "D"
    if "障" in racedata01_rows[0].text[0]:
        racedata01_race_course_gnd = "O"
    racedata02_rows = driver.find_element_by_class_name('RaceData02').find_elements_by_tag_name("span")
    racedata02_place = racedata02_rows[1].text

    all_race_rows = driver.find_element_by_class_name('Shutuba_Table').find_elements_by_tag_name("tr")
    horse_name_list = []
    horse_url_list = []
    jockey_name_list = []
    jockey_url_list = []
    for r_row in range(2,len(all_race_rows)):
        #for r_row in range(2 + 4,2+5):
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

        tmp0_jockey_race_data_list = []
        cnt = 0
        while True:
            time.sleep(1)
            wait.until(EC.presence_of_all_elements_located)
            all_jockey_rows = driver.find_element_by_class_name('race_table_01').find_elements_by_tag_name("tr")

            tmp1_jockey_race_data_list = []
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

                if place == "" or weather == "" or burden_weight == "" or race_course_gnd == "" or distance == "" or ground_status == "" or goal_time == "":
                    
                    continue

                # 開催レース情報と合致する騎手データのみを取得
                if (racedata01_distance - 400 < distance and distance < racedata01_distance + 400) and racedata01_race_course_gnd == race_course_gnd:
                    tmp1_jockey_race_data_list.append([place, weather, burden_weight, race_course_gnd, distance, ground_status, goal_time])
                    print("{} {}".format(cnt, [place, weather, burden_weight, race_course_gnd, distance, ground_status, goal_time]))
                    cnt += 1

            tmp0_jockey_race_data_list += tmp1_jockey_race_data_list

            
            if cnt > 150:
                break

            try:
                target = driver.find_elements_by_link_text("次")[0]
                #print(driver.find_elements_by_link_text("次"))
                driver.execute_script("arguments[0].click();", target) #javascriptでクリック処理
            except IndexError:
                break
        
        jockey_race_data_list.append(tmp0_jockey_race_data_list)

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



def makeDatabeseBloodFather(sql_dir):
    # DBを作成する
    # すでに存在していれば、それにアスセスする。
    dbname = '/BloodFather.db'
    conn = sqlite3.connect(sql_dir + dbname)
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

    # DBにアスセス
    conn = sqlite3.connect(sql_dir + dbname)
    # sqliteを操作するカーソルオブジェクトを作成
    cur = conn.cursor()

    # btgfというtableを作成
    try:
        cur.execute('CREATE TABLE blood_father( \
        id INTEGER PRIMARY KEY AUTOINCREMENT, \
        horse_id_foal INTEGER, \
        horse_id_father INTEGER \
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





def updateDatabeseBloodFather(sql_dir, horse_id_foal, horse_id_father):
    dbname = '/BloodFather.db'
    conn = sqlite3.connect(sql_dir + dbname)
    cur = conn.cursor()

    # データを入力 OR 更新
    cur.execute('SELECT * FROM blood_father WHERE horse_id_foal = "{}" AND horse_id_father = "{}"'.format(horse_id_foal, horse_id_father))
    row_fetched = cur.fetchall()
    if len(row_fetched) == 0:
        print("INSERT")
        cur.execute('INSERT INTO blood_father(horse_id_foal, horse_id_father) \
        values("{}","{}")'.format(horse_id_foal, horse_id_father))

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





def scrHorseBloodline(race_url, sql_dir):
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
    for r_row in range(2,len(all_race_rows)):
        #for r_row in range(2 + 4,2+5):
        horse_name_list.append(all_race_rows[r_row].find_element_by_class_name('HorseInfo').find_element_by_tag_name("a").get_attribute("title"))
        horse_url_list.append(all_race_rows[r_row].find_element_by_class_name('HorseInfo').find_element_by_tag_name("a").get_attribute("href"))

    for r_row in range(len(horse_name_list)):
        print(horse_name_list[r_row])

        # 出走馬の詳細を検索
        driver.get(horse_url_list[r_row])
        time.sleep(1)
        wait.until(EC.presence_of_all_elements_located)

        bloodlilne_url = driver.find_element_by_class_name('db_prof_area_02').find_elements_by_class_name('detail_link')[0].find_element_by_tag_name("a").get_attribute("href")

        # 出走馬の血統図を検索
        driver.get(bloodlilne_url)
        time.sleep(1)
        wait.until(EC.presence_of_all_elements_located)

        bloodlilne_tree_table = driver.find_element_by_class_name('blood_table').find_elements_by_tag_name("tr")
        bloodlilne_tree_urls = [
            bloodlilne_tree_table[0].find_elements_by_tag_name("td")[0].find_elements_by_tag_name("a")[0].get_attribute("href"), # father
            #bloodlilne_tree_table[16].find_elements_by_tag_name("td")[0].find_elements_by_tag_name("a")[0].get_attribute("href"), # mother
            bloodlilne_tree_table[0].find_elements_by_tag_name("td")[1].find_elements_by_tag_name("a")[0].get_attribute("href"), # father's father
            bloodlilne_tree_table[16].find_elements_by_tag_name("td")[1].find_elements_by_tag_name("a")[0].get_attribute("href"), # mother's father
            #bloodlilne_tree_table[8].find_elements_by_tag_name("td")[0].find_elements_by_tag_name("a")[0].get_attribute("href"), # father's mother
            #bloodlilne_tree_table[24].find_elements_by_tag_name("td")[0].find_elements_by_tag_name("a")[0].get_attribute("href") # mother's mother
        ]

        # 出走馬の親の子供（Foal）の情報をデータベースに格納
        bloodlilne_father_foal_list = []
        for bt_url in bloodlilne_tree_urls:
            father_id = bt_url.split("/")[-2]

            dbname = '/BloodFather.db'
            conn = sqlite3.connect(sql_dir + dbname)
            cur = conn.cursor()
            # すでにfather_idがデータベースにあるか確認
            cur.execute('SELECT * FROM blood_father WHERE horse_id_father = "{}"'.format(father_id))
            row_fetched = cur.fetchall()
            if len(row_fetched) > 0:
                print("{} already exist in {}!".format(father_id, dbname))
                print("")
                conn.commit()
                cur.close()
                conn.close()

                continue
            else:
                conn.commit()
                cur.close()
                conn.close()


            driver.get(bt_url)
            time.sleep(1)
            wait.until(EC.presence_of_all_elements_located)

            foal_url = driver.find_elements_by_class_name('db_breeding_table_01')[0].find_elements_by_tag_name("tr")[1].find_elements_by_tag_name("a")[0].get_attribute("href")

            driver.get(foal_url)
            time.sleep(1)
            wait.until(EC.presence_of_all_elements_located)
            
            cnt = 0
            while True:
                time.sleep(1)
                wait.until(EC.presence_of_all_elements_located)

                foal_table = driver.find_element_by_class_name('race_table_01').find_elements_by_tag_name("tr")
                for i_f in range(1, len(foal_table)):
                    cnt += 1
                    foal_id = foal_table[i_f].find_elements_by_tag_name("td")[1].find_elements_by_tag_name("a")[0].get_attribute("href").split("/")[-2]
                    print("{}\tfoal_id = {}".format(cnt, foal_id))

                    bloodlilne_father_foal_list.append([foal_id, father_id])

                try:
                    target = driver.find_elements_by_link_text("次")[0]
                    driver.execute_script("arguments[0].click();", target) #javascriptでクリック処理
                except IndexError:
                    print("while break")
                    break

        
        # 父親とその子供のリストをデータベースに挿入
        for bff in bloodlilne_father_foal_list:
            updateDatabeseBloodFather(sql_dir, bff[0], bff[1])


        #father_url = bloodlilne_tree_table[0].find_elements_by_tag_name("a")[0].get_attribute("href")
        #mother_url = bloodlilne_tree_table[16].find_elements_by_tag_name("a")[0].get_attribute("href")
        #father_bloodlilne_tree_url = bloodlilne_tree_table[0].find_elements_by_tag_name("a")[0].get_attribute("href")
        #mother_bloodlilne_tree_url = bloodlilne_tree_table[16].find_elements_by_tag_name("a")[0].get_attribute("href")

        


def calcBloodlineSpeedFigure(race_url, sql_dir, race_data_list, horse_data_list):
    foal_result = []

    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    driver.get(race_url) # 速度ボトルネック
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    # 開催レース情報の取得（距離だけ）
    racedata01_rows = driver.find_element_by_class_name('RaceData01').find_elements_by_tag_name("span")
    racedata01_distance = int(racedata01_rows[0].text[-5:-1])

    print("racedata01_distance = {} {}".format(type(racedata01_distance), racedata01_distance))

    # 出走馬の名前とURLを取得
    all_race_rows = driver.find_element_by_class_name('Shutuba_Table').find_elements_by_tag_name("tr")
    horse_name_list = []
    horse_url_list = []
    for r_row in range(2,len(all_race_rows)):
        #for r_row in range(2 + 4,2+5):
        horse_name_list.append(all_race_rows[r_row].find_element_by_class_name('HorseInfo').find_element_by_tag_name("a").get_attribute("title"))
        horse_url_list.append(all_race_rows[r_row].find_element_by_class_name('HorseInfo').find_element_by_tag_name("a").get_attribute("href"))

    # 出走馬の血統情報から、出走レースでのスピード指数を計算
    for r_row in range(len(horse_name_list)):
        print(horse_name_list[r_row])

        # 出走馬の詳細を検索
        driver.get(horse_url_list[r_row])
        time.sleep(1)
        wait.until(EC.presence_of_all_elements_located)

        bloodlilne_url = driver.find_element_by_class_name('db_prof_area_02').find_elements_by_class_name('detail_link')[0].find_element_by_tag_name("a").get_attribute("href")

        # 出走馬の血統図を検索
        driver.get(bloodlilne_url)
        time.sleep(1)
        wait.until(EC.presence_of_all_elements_located)

        bloodlilne_tree_table = driver.find_element_by_class_name('blood_table').find_elements_by_tag_name("tr")
        bloodlilne_tree_horse_id_list = [
            bloodlilne_tree_table[0].find_elements_by_tag_name("td")[0].find_elements_by_tag_name("a")[0].get_attribute("href").split("/")[-2], # father
            #bloodlilne_tree_table[16].find_elements_by_tag_name("td")[0].find_elements_by_tag_name("a")[0].get_attribute("href").split("/")[-2], # mother
            bloodlilne_tree_table[0].find_elements_by_tag_name("td")[1].find_elements_by_tag_name("a")[0].get_attribute("href").split("/")[-2], # father's father
            bloodlilne_tree_table[16].find_elements_by_tag_name("td")[1].find_elements_by_tag_name("a")[0].get_attribute("href").split("/")[-2], # mother's father
            #bloodlilne_tree_table[8].find_elements_by_tag_name("td")[0].find_elements_by_tag_name("a")[0].get_attribute("href").split("/")[-2], # father's mother
            #bloodlilne_tree_table[24].find_elements_by_tag_name("td")[0].find_elements_by_tag_name("a")[0].get_attribute("href").split("/")[-2] # mother's mother
        ]
        """
        bloodlilne_tree_speed_figure_rate = [
            0.25, # father
            #0.25, # mother
            0.125, # father's father
            0.125, # mother's father
            #0.125, # father's mother
            #0.125, # mother's mother
        ]
        total_rate = 0
        for btsfr in bloodlilne_tree_speed_figure_rate:
            total_rate += btsfr
        fix_coef = 1.0 / total_rate # bloodlilne_tree_speed_figure_rate の合計が１になるように調整する係数
        """

        # 父親の子供の戦績データを収集
        foal_race_data_list = []
        foal_horse_data_list = []
        
        dbname_bf = '/BloodFather.db'
        conn_bf = sqlite3.connect(sql_dir + dbname_bf)
        cur_bf = conn_bf.cursor()
        for father_id in bloodlilne_tree_horse_id_list:
            print("father_id = {}".format(father_id))
            cur_bf.execute('SELECT * FROM blood_father WHERE horse_id_father = "{}"'.format(father_id))
            foal_id_list = cur_bf.fetchall()

            dbname_h = '/Horse.db'
            conn_h = sqlite3.connect(sql_dir + dbname_h)
            conn_h.row_factory = sqlite3.Row
            cur_h = conn_h.cursor()

            cnt_foal = 0
            for foal_id in foal_id_list:

                # DEBUG 最大100匹の子供のスピード指数を計算する
                cnt_foal += 1
                if cnt_foal > 100:

                    break

                cur_h.execute('SELECT * FROM horse WHERE horse_id = "{}" order by race_id desc'.format(foal_id[1]))
                #tmp_foal_horse_data_list = cur_h.fetchall()
                tmp_foal_horse_data_list = []
                for row in cur_h.fetchall():
                    tmp_foal_horse_data_list.append(dict(row))
                foal_horse_data_list += tmp_foal_horse_data_list

                dbname_r = '/Race.db'
                conn_r = sqlite3.connect(sql_dir + dbname_r)
                conn_r.row_factory = sqlite3.Row
                cur_r = conn_r.cursor()

                for frr in tmp_foal_horse_data_list:
                    cur_r.execute('SELECT * FROM race WHERE race_id = {}'.format(frr["race_id"]))
                    #tmp_foal_race_data_list = cur_r.fetchall()
                    tmp_foal_race_data_list = []
                    for row in cur_r.fetchall():
                        tmp_foal_race_data_list.append(dict(row))

                    if len(tmp_foal_race_data_list) == 0:
                        print("there is no race_id = {} in {}".format(frr["race_id"], dbname_r))
                        foal_race_data_list.append("NULL")
                    elif racedata01_distance - 400 < tmp_foal_race_data_list[0]["race_course_m"] and tmp_foal_race_data_list[0]["race_course_m"] < racedata01_distance + 400:
                        foal_race_data_list.append(tmp_foal_race_data_list[0])
                    else:
                        #print("race_id = {} in {} distance(m) out of range {} plus_minus 200".format(frr["race_id"], dbname_r, racedata01_distance))
                        foal_race_data_list.append("NULL")

                conn_r.commit()
                cur_r.close()
                conn_r.close()

            conn_h.commit()
            cur_h.close()
            conn_h.close()

        conn_bf.commit()
        cur_bf.close()
        conn_bf.close()


        # 父親の子供の過去の戦績（重複なし）
        foal_race_data_list_shr = []
        for foal_race_idx in range(len(foal_race_data_list)):
            if foal_race_data_list[foal_race_idx] == "NULL":
                continue

            place = foal_race_data_list[foal_race_idx]["where_racecourse"].split("回")[1][:2]
            if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
                weather = foal_race_data_list[foal_race_idx]["weather"]
                burden_weight = foal_horse_data_list[foal_race_idx]["burden_weight"]
                race_course_gnd = foal_race_data_list[foal_race_idx]["race_course_gnd"]
                distance = foal_race_data_list[foal_race_idx]["race_course_m"]
                ground_status = foal_race_data_list[foal_race_idx]["ground_status"]
                goal_time = foal_horse_data_list[foal_race_idx]["goal_time"]
                foal_race_data_list_shr.append([place, distance, race_course_gnd, weather, ground_status])
        foal_race_data_list_shr = get_unique_list(foal_race_data_list_shr)
        print("len foal_race_data_list_shr:{}".format(len(foal_race_data_list_shr)))


        # 父親の子供の過去の戦績（重複なし）に対する　ベースタイム　と　馬場指数
        foal_base_time_and_gnd_figure_list = []
        for i in range(len(foal_race_data_list_shr)):
            base_time, gf = calcBaseTimeFigureAndGndFigure(race_data_list, horse_data_list, foal_race_data_list_shr[i][0], foal_race_data_list_shr[i][1], foal_race_data_list_shr[i][2], foal_race_data_list_shr[i][3], foal_race_data_list_shr[i][4])
            foal_base_time_and_gnd_figure_list.append([base_time, gf])
        rap_time = time.time() - start


        # スピード指数の計算
        foal_speed_figure_list = []
        for foal_race_idx in range(len(foal_race_data_list)):
            if foal_race_data_list[foal_race_idx] == "NULL":
                continue

            place = foal_race_data_list[foal_race_idx]["where_racecourse"].split("回")[1][:2]
            if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
                weather = foal_race_data_list[foal_race_idx]["weather"]
                burden_weight = foal_horse_data_list[foal_race_idx]["burden_weight"]
                race_course_gnd = foal_race_data_list[foal_race_idx]["race_course_gnd"]
                distance = foal_race_data_list[foal_race_idx]["race_course_m"]
                ground_status = foal_race_data_list[foal_race_idx]["ground_status"]
                goal_time = foal_horse_data_list[foal_race_idx]["goal_time"]
                try:
                    idx = foal_race_data_list_shr.index([place, distance, race_course_gnd, weather, ground_status])
                    tmp = foal_base_time_and_gnd_figure_list[idx]
                    base_time = tmp[0]
                    gf = tmp[1]

                    #print("goal_time = {}".format(goal_time))
                    # ベースタイム算出
                    #print("base_time = {}".format(base_time))
                    # 距離指数算出
                    df = calcDistanceFigure(base_time)
                    #print("df = {}".format(df))
                    # 馬場指数算出
                    if gf == None or goal_time == None or base_time == None:

                        continue

                    #print("gf = {}".format(gf))
                    # スピード指数算出
                    speed_figure = (base_time*10 - goal_time*10) * df + gf + (burden_weight - 55) * 2 + 80
                    #print("speed_figure = {}".format(speed_figure))

                    foal_speed_figure_list.append(speed_figure)

                except:
                    print("can not find")
                    print([place, distance, race_course_gnd, weather, ground_status])

        ave_foal_speed_figure = statistics.mean(foal_speed_figure_list)
        std_foal_speed_figure = statistics.pstdev(foal_speed_figure_list)
        print("len = {}".format(len(foal_speed_figure_list)))
        print("[ave] speed_figure = {}".format(ave_foal_speed_figure))
        print("[std] speed_figure = {}".format(std_foal_speed_figure))

        foal_result.append([horse_name_list[r_row], ave_foal_speed_figure])

    return foal_result




def get_unique_list(seq):
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]



if __name__ == '__main__':
    
    race_url = "https://race.netkeiba.com/race/shutuba.html?race_id=202105030411&rf=race_submenu"
    sql_dir = "../data/all_sq"

    # 血統情報のデータベースを作成
    makeDatabeseBloodFather(sql_dir)

    # ベースタイム　と　馬場指数　のデータベースを作成
    makeDatabeseBaseTimeFigureAndGndFigure()

    start = time.time()

    # sqlデータの読み込み
    horse_data_list = readHorseSqlDatabase(sql_dir)
    race_data_list = readRaceSqlDatabase(sql_dir)
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))

    # 出走馬の血統情報をデータベース書き込み
    scrHorseBloodline(race_url, sql_dir)
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))

    # 血統情報から出走馬のスピード指数を計算
    foal_result = calcBloodlineSpeedFigure(race_url, sql_dir, race_data_list, horse_data_list)
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))

    # 出走馬、ジョッキーの過去の戦績
    horse_race_data_list, horse_name_list, jockey_race_data_list, jockey_name_list = scrHorseAndJockeyRaceData(race_url)
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))

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
            print(horse_result)


    print("## org ##")
    print(horse_result)
    print("## sorted ##")
    print(sorted(horse_result, reverse=True, key=lambda x: x[1]))
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))
    

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
                #print(place)
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
                        #print("goal_time = {}".format(goal_time))
                        # ベースタイム算出
                        #print("base_time = {}".format(base_time))
                        # 距離指数算出
                        df = calcDistanceFigure(base_time)
                        #print("df = {}".format(df))
                        # 馬場指数算出
                        if gf == None:

                            continue

                        #print("gf = {}".format(gf))
                        # スピード指数算出
                        speed_figure = (base_time*10 - goal_time*10) * df + gf + (burden_weight - 55) * 2 + 80
                        #print("speed_figure = {}".format(speed_figure))

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
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))


    # 出走馬の血統馬と出走馬、ジョッキーのスピード指数から総合的にスピード指数を計算してソートして表示
    total_result = []
    for i in range(len(horse_result)):
        horse_blood_result = (foal_result[i][1] + horse_result[i][1]) / 2
        total_result.append([(horse_blood_result + jockey_result[i][1]) / 2, horse_result[i][0], jockey_result[i][0]])
    total_result_ = sorted(total_result, reverse=True, key=lambda x: x[0])
    for i in range(len(total_result_)):
        print(total_result_[i])

