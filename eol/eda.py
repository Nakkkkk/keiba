# author Nakkkkk (https://github.com/Nakkkkk)
# このプログラムによって発生した損害に対し、いかなる責任をも負わないとする。
# I assume no responsibility for any damages caused by this program.


import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import os
from natsort import natsorted
import glob
#import seaborn as sns
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
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
import random



def init_logger(path, name):
    # ログの出力名を設定（1）
    logger = logging.getLogger(name)
    # ログレベルの設定（2）
    logger.setLevel(10)
    # ログのコンソール出力の設定（3）
    sh = logging.StreamHandler()
    logger.addHandler(sh)
    # ログのファイル出力先を設定（4）
    fh = logging.FileHandler(path + "/" + name + ".log")
    logger.addHandler(fh)
    # ログの出力形式の設定
    formatter = logging.Formatter('%(asctime)s:%(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    return logger



# 馬のSQLデータベースの読み込み
def readHorseSqlDatabase(data_dir):
    dbname = '/all_sq/Horse.db'
    conn = sqlite3.connect(data_dir + dbname)
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
def readRaceSqlDatabase(data_dir):
    dbname = '/all_sq/Race.db'
    conn = sqlite3.connect(data_dir + dbname)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('SELECT * FROM race order by race_id desc')
    race_data_list = []
    for row in cur.fetchall():
        race_data_list.append(dict(row))

    cur.close()
    conn.close()

    return race_data_list









def updateDatabeseBloodFather(logger, data_dir, horse_id_foal, horse_id_father):
    dbname = '/all_sq/BloodFather.db'
    conn = sqlite3.connect(data_dir + dbname)
    cur = conn.cursor()

    # データを入力 OR 更新
    cur.execute('SELECT * FROM blood_father WHERE horse_id_foal = "{}" AND horse_id_father = "{}"'.format(horse_id_foal, horse_id_father))
    row_fetched = cur.fetchall()
    if len(row_fetched) == 0:
        logger.log(20, "INSERT")
        cur.execute('INSERT INTO blood_father(horse_id_foal, horse_id_father) \
        values("{}","{}")'.format(horse_id_foal, horse_id_father))

    conn.commit()

    cur.close()
    conn.close()





def scrRaceData(logger, data_dir, race_url):
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    driver.get(race_url) # 速度ボトルネック
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    # 開催レース情報の取得
    racedata01_rows = driver.find_element_by_class_name('RaceData01').find_elements_by_tag_name("span")
    distance = int(racedata01_rows[0].text[-5:-1])
    race_course_gnd = ""
    if "芝" in racedata01_rows[0].text[0]:
        race_course_gnd = "T"
    elif "ダ" in racedata01_rows[0].text[0]:
        race_course_gnd = "D"
    if "障" in racedata01_rows[0].text[0]:
        race_course_gnd = "O"
    racedata02_rows = driver.find_element_by_class_name('RaceData02').find_elements_by_tag_name("span")
    place = racedata02_rows[1].text

    all_race_rows = driver.find_element_by_class_name('Shutuba_Table').find_elements_by_tag_name("tr")
    frame_number_list = []
    for r_row in range(2,len(all_race_rows)):
        #for r_row in range(2 + 4,2+5):
        frame_number_list.append(int(all_race_rows[r_row].find_elements_by_tag_name("td")[0].find_element_by_tag_name("span").text))



    return distance, race_course_gnd, place, frame_number_list




def scrHorseAndJockeyRaceNameAndUrl(logger, race_url):
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


    return horse_url_list, horse_name_list, jockey_url_list, jockey_name_list




def scrHorseRaceNameAndUrl(logger, race_url):
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

    return horse_url_list, horse_name_list





def scrJockeyRaceNameAndUrl(logger, race_url):
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    driver.get(race_url) # 速度ボトルネック
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    all_race_rows = driver.find_element_by_class_name('Shutuba_Table').find_elements_by_tag_name("tr")
    jockey_name_list = []
    jockey_url_list = []
    for r_row in range(2,len(all_race_rows)):
        #for r_row in range(2 + 4,2+5):
        jockey_name_list.append(all_race_rows[r_row].find_element_by_class_name('Jockey').find_element_by_tag_name("a").get_attribute("title"))
        jockey_url_list.append(all_race_rows[r_row].find_element_by_class_name('Jockey').find_element_by_tag_name("a").get_attribute("href"))


    return jockey_url_list, jockey_name_list





def scrTamerRaceNameAndUrl(logger, race_url):
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    driver.get(race_url) # 速度ボトルネック
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    all_race_rows = driver.find_element_by_class_name('Shutuba_Table').find_elements_by_tag_name("tr")
    tamer_name_list = []
    tamer_url_list = []
    for r_row in range(2,len(all_race_rows)):
        #for r_row in range(2 + 4,2+5):
        tamer_name_list.append(all_race_rows[r_row].find_element_by_class_name('Trainer').find_element_by_tag_name("a").get_attribute("title"))
        tamer_url_list.append(all_race_rows[r_row].find_element_by_class_name('Trainer').find_element_by_tag_name("a").get_attribute("href"))


    return tamer_url_list, tamer_name_list






def rand_ints_nodup(a, b, k):
    ns = []
    while len(ns) < k:
        n = random.randint(a, b)
        if not n in ns:
            ns.append(n)
    return ns




def scrJockeyRaceDataFromSQL(logger, data_dir, race_url, race_smp_num, jockey_url_list, jockey_name_list):
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    dbname_h = '/all_sq/Horse.db'
    conn_h = sqlite3.connect(data_dir + dbname_h)
    conn_h.row_factory = sqlite3.Row
    cur_h = conn_h.cursor()

    dbname_r = '/all_sq/Race.db'
    conn_r = sqlite3.connect(data_dir + dbname_r)
    conn_r.row_factory = sqlite3.Row
    cur_r = conn_r.cursor()

    # ジョッキーのレース成績をリストに保存（直近200試合を参照）
    jockey_race_data_list = []
    for r_row in range(len(jockey_name_list)):
        logger.log(20, jockey_name_list[r_row])
        #driver.get(jockey_url_list[r_row])
        jockey_id = jockey_url_list[r_row].split("/")[-2]

        cur_h.execute('SELECT * FROM horse WHERE rider_id = "{}" order by race_id desc'.format(jockey_id))
        
        #tmp0_jockey_race_data_list = cur_h.fetchall()
        tmp0_jockey_race_data_list = []
        cnt = 0
        cur_h_fetchall = cur_h.fetchall()
        logger.log(20, "len cur_h.fetchall() = {}".format(len(cur_h_fetchall)))

        # データからrace_smp_num個無作為抽出
        if race_smp_num <= len(cur_h_fetchall):
            race_random_num_list = rand_ints_nodup(0, len(cur_h_fetchall) - 1, race_smp_num) 
        else:
            race_random_num_list = list(range(len(cur_h_fetchall)))
            random.shuffle(race_random_num_list)

        for rnd_idx in race_random_num_list:
            row_h = cur_h_fetchall[rnd_idx]
            dict_row_h = dict(row_h)
            cur_r.execute('SELECT * FROM race WHERE race_id = {}'.format(dict_row_h["race_id"]))
            for row_r in cur_r.fetchall():
                dict_row_r = dict(row_r)
                place = dict_row_r["where_racecourse"].split("回")[1][:2]

                tmp0_jockey_race_data_list.append({"place":place, "weather":dict_row_r["weather"], "burden_weight":dict_row_h["burden_weight"], "race_course_gnd":dict_row_r["race_course_gnd"], "race_course_m":dict_row_r["race_course_m"], "ground_status":dict_row_r["ground_status"], "goal_time":dict_row_h["goal_time"], "rank":dict_row_h["rank"], "frame_number":dict_row_h["frame_number"]})
                logger.log(20, "{} {}".format(cnt, [place, dict_row_r["weather"], dict_row_h["burden_weight"], dict_row_r["race_course_gnd"], dict_row_r["race_course_m"], dict_row_r["ground_status"], dict_row_h["goal_time"], dict_row_h["rank"], dict_row_h["frame_number"]]))
                cnt += 1

            if cnt > race_smp_num:
                break

        jockey_race_data_list.append(tmp0_jockey_race_data_list)


    return jockey_race_data_list




def scrTamerRaceDataFromSQL(logger, data_dir, race_url, race_smp_num, tamer_url_list, tamer_name_list):
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    dbname_h = '/all_sq/Horse.db'
    conn_h = sqlite3.connect(data_dir + dbname_h)
    conn_h.row_factory = sqlite3.Row
    cur_h = conn_h.cursor()

    dbname_r = '/all_sq/Race.db'
    conn_r = sqlite3.connect(data_dir + dbname_r)
    conn_r.row_factory = sqlite3.Row
    cur_r = conn_r.cursor()

    # 調教師のレース成績をリストに保存（直近200試合を参照）
    tamer_race_data_list = []
    for r_row in range(len(tamer_name_list)):
        logger.log(20, tamer_name_list[r_row])
        #driver.get(tamer_url_list[r_row])
        tamer_id = tamer_url_list[r_row].split("/")[-2]

        cur_h.execute('SELECT * FROM horse WHERE tamer_id = "{}" order by race_id desc'.format(tamer_id))
        
        #tmp0_tamer_race_data_list = cur_h.fetchall()
        tmp0_tamer_race_data_list = []
        cnt = 0
        cur_h_fetchall = cur_h.fetchall()
        logger.log(20, "len cur_h.fetchall() = {}".format(len(cur_h_fetchall)))

        # データからrace_smp_num個無作為抽出
        if race_smp_num <= len(cur_h_fetchall):
            race_random_num_list = rand_ints_nodup(0, len(cur_h_fetchall) - 1, race_smp_num) 
        else:
            race_random_num_list = list(range(len(cur_h_fetchall)))
            random.shuffle(race_random_num_list)

        for rnd_idx in race_random_num_list:
            row_h = cur_h_fetchall[rnd_idx]
            dict_row_h = dict(row_h)
            cur_r.execute('SELECT * FROM race WHERE race_id = {}'.format(dict_row_h["race_id"]))
            for row_r in cur_r.fetchall():
                dict_row_r = dict(row_r)
                place = dict_row_r["where_racecourse"].split("回")[1][:2]

                tmp0_tamer_race_data_list.append({"place":place, "weather":dict_row_r["weather"], "burden_weight":dict_row_h["burden_weight"], "race_course_gnd":dict_row_r["race_course_gnd"], "race_course_m":dict_row_r["race_course_m"], "ground_status":dict_row_r["ground_status"], "goal_time":dict_row_h["goal_time"], "rank":dict_row_h["rank"], "frame_number":dict_row_h["frame_number"]})
                logger.log(20, "{} {}".format(cnt, [place, dict_row_r["weather"], dict_row_h["burden_weight"], dict_row_r["race_course_gnd"], dict_row_r["race_course_m"], dict_row_r["ground_status"], dict_row_h["goal_time"], dict_row_h["rank"], dict_row_h["frame_number"]]))
                cnt += 1

            if cnt > race_smp_num:
                break

        tamer_race_data_list.append(tmp0_tamer_race_data_list)


    return tamer_race_data_list







def scrHorseBloodline(logger, race_url, data_dir):
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
        logger.log(20, horse_name_list[r_row])

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

            dbname = '/all_sq/BloodFather.db'
            conn = sqlite3.connect(data_dir + dbname)
            cur = conn.cursor()
            # すでにfather_idがデータベースにあるか確認
            cur.execute('SELECT * FROM blood_father WHERE horse_id_father = "{}"'.format(father_id))
            row_fetched = cur.fetchall()
            if len(row_fetched) > 0:
                logger.log(20, "{} already exist in {}!".format(father_id, dbname))
                logger.log(20, "")
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
                    logger.log(20, "{}\tfoal_id = {}".format(cnt, foal_id))

                    bloodlilne_father_foal_list.append([foal_id, father_id])

                try:
                    target = driver.find_elements_by_link_text("次")[0]
                    driver.execute_script("arguments[0].click();", target) #javascriptでクリック処理
                except IndexError:
                    logger.log(20, "while break")
                    break

        
        # 父親とその子供のリストをデータベースに挿入
        for bff in bloodlilne_father_foal_list:
            updateDatabeseBloodFather(logger, data_dir, bff[0], bff[1])





def scrBloodRaceDataFromSQL(logger, data_dir, race_url, race_smp_num, horse_url_list, horse_name_list):
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    dbname_h = '/all_sq/Horse.db'
    conn_h = sqlite3.connect(data_dir + dbname_h)
    conn_h.row_factory = sqlite3.Row
    cur_h = conn_h.cursor()

    dbname_r = '/all_sq/Race.db'
    conn_r = sqlite3.connect(data_dir + dbname_r)
    conn_r.row_factory = sqlite3.Row
    cur_r = conn_r.cursor()

    dbname_bf = '/all_sq/BloodFather.db'
    conn_bf = sqlite3.connect(data_dir + dbname_bf)
    conn_bf.row_factory = sqlite3.Row
    cur_bf = conn_bf.cursor()


    # 出走馬の血統情報から、出走レースでのスピード指数を計算
    blood_race_data_list = []
    for r_row in range(len(horse_name_list)):
        cnt = 0
        logger.log(20, horse_name_list[r_row])

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
        tmp0_blood_race_data_list = []
        
        for father_id in bloodlilne_tree_horse_id_list:
            logger.log(20, "father_id = {}".format(father_id))
            cur_bf.execute('SELECT * FROM blood_father WHERE horse_id_father = "{}"'.format(father_id))
            foal_id_list = cur_bf.fetchall()

            # データから50個無作為抽出
            if 50 <= len(foal_id_list):
                foal_id_list_idx_random_list = rand_ints_nodup(0, len(foal_id_list) - 1, 50) 
            else:
                foal_id_list_idx_random_list = list(range(len(foal_id_list)))
                random.shuffle(foal_id_list_idx_random_list)

            cnt_foal = 0
            for foal_id_list_idx in foal_id_list_idx_random_list:
                foal_id = foal_id_list[foal_id_list_idx]

                cnt_foal += 1
                """
                if cnt_foal > 100:

                    break
                """

                cur_h.execute('SELECT * FROM horse WHERE horse_id = "{}" order by race_id desc'.format(foal_id[1]))
                for row_h in cur_h.fetchall():
                    dict_row_h = dict(row_h)

                    cur_r.execute('SELECT * FROM race WHERE race_id = {}'.format(dict_row_h["race_id"]))
                    for row_r in cur_r.fetchall():
                        dict_row_r = dict(row_r)

                        place = dict_row_r["where_racecourse"].split("回")[1][:2]

                        tmp0_blood_race_data_list.append({"place":place, "weather":dict_row_r["weather"], "burden_weight":dict_row_h["burden_weight"], "race_course_gnd":dict_row_r["race_course_gnd"], "race_course_m":dict_row_r["race_course_m"], "ground_status":dict_row_r["ground_status"], "goal_time":dict_row_h["goal_time"], "rank":dict_row_h["rank"], "frame_number":dict_row_h["frame_number"]})
                        logger.log(20, "{} {} {}".format(cnt, cnt_foal, [place, dict_row_r["weather"], dict_row_h["burden_weight"], dict_row_r["race_course_gnd"], dict_row_r["race_course_m"], dict_row_r["ground_status"], dict_row_h["goal_time"], dict_row_h["rank"], dict_row_h["frame_number"]]))
                        cnt += 1

        blood_race_data_list.append(tmp0_blood_race_data_list)


    return blood_race_data_list




def scrJockeyRaceData(logger, race_url, race_smp_num, jockey_url_list, jockey_name_list):
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,5)

    # ジョッキーのレース成績をリストに保存（直近200試合を参照）
    jockey_race_data_list = []
    for r_row in range(len(jockey_name_list)):
        logger.log(20, jockey_name_list[r_row])
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
                #if (racedata01_distance - 400 < distance and distance < racedata01_distance + 400) and racedata01_race_course_gnd == race_course_gnd:
                tmp1_jockey_race_data_list.append([place, weather, burden_weight, race_course_gnd, distance, ground_status, goal_time])
                logger.log(20, "{} {}".format(cnt, [place, weather, burden_weight, race_course_gnd, distance, ground_status, goal_time]))
                cnt += 1

                if cnt > race_smp_num:
                    break

            tmp0_jockey_race_data_list += tmp1_jockey_race_data_list

            
            if cnt > race_smp_num:
                break

            try:
                target = driver.find_elements_by_link_text("次")[0]
                #logger.log(20, driver.find_elements_by_link_text("次"))
                driver.execute_script("arguments[0].click();", target) #javascriptでクリック処理
            except IndexError:
                break
        
        jockey_race_data_list.append(tmp0_jockey_race_data_list)


    return jockey_race_data_list




# ベースタイムと馬場指数の計算 TODO
def calcBaseTimeFigureAndGndFigure(logger, data_dir, race_data_list, horse_data_list, place, distance, race_course_gnd, weather, ground_status):
    ave_time_list = [] # 1〜3位平均タイム
    base_time_list = [] # ベースタイム
    bt_ri_list = [] # ベースタイム用のrace_idリスト
    gf_ri_list = [] # 馬場指数用のrace_idリスト


    # ベースタイム　と　馬場指数　のデータベースと照合
    # データベースにデータがあれば、それをリターン
    db_list = readDatabeseBaseTimeFigureAndGndFigure(data_dir)
    horse_race_data_list_shr_trim = []
    for i in range(len(db_list)):
        if db_list[i][1] == place and \
           db_list[i][2] == distance and \
           db_list[i][3] == race_course_gnd and \
           db_list[i][4] == weather and \
           db_list[i][5] == ground_status:

            logger.log(20, "REUSE")
            
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
        logger.log(20, "[gf_ri_list] conditions conditions did not hit !")
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
        logger.log(20, "[base_time] conditions did not hit !")
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
        
        logger.log(20, "")
        logger.log(20, "")
        logger.log(20, "#######    len(gf_ri_list) != len(ave_time_list) or len(bt_ri_list) != len(base_time_list)")
        logger.log(20, "")
        logger.log(20, "")

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
    updateDatabeseBaseTimeFigureAndGndFigure(logger, data_dir, place, distance, race_course_gnd, weather, ground_status, base_time, gnd_figure)


    return base_time, gnd_figure   # 指数として出力するため10かけている



# TODO BaseTimeAndGndFigure.db　を　dataディレクトリに移動
def readDatabeseBaseTimeFigureAndGndFigure(data_dir):
    dbname = '/all_sq/BaseTimeAndGndFigure.db'
    conn = sqlite3.connect(data_dir + dbname)
    cur = conn.cursor()

    cur.execute('SELECT * FROM btgf')
    row_fetched = cur.fetchall()

    cur.close()
    conn.close()

    return row_fetched



def updateDatabeseBaseTimeFigureAndGndFigure(logger, data_dir, place, distance, race_course_gnd, weather, ground_status, basetime, gndfigure):
    dbname = '/all_sq/BaseTimeAndGndFigure.db'
    conn = sqlite3.connect(data_dir + dbname)
    cur = conn.cursor()

    # データを入力 OR 更新
    cur.execute('SELECT * FROM btgf WHERE place = "{}" AND distance = {} AND race_course_gnd = "{}" AND weather = "{}" AND ground_status = "{}"'.format(place, distance, race_course_gnd, weather, ground_status))
    row_fetched = cur.fetchall()
    if len(row_fetched) == 0:
        logger.log(20, "INSERT")
        cur.execute('INSERT INTO btgf(place, distance, race_course_gnd, weather, ground_status, basetime, gndfigure) \
        values("{}",{},"{}","{}","{}",{},{})'.format(place, distance, race_course_gnd, weather, ground_status, basetime, gndfigure))
    else:
        logger.log(20, "UPDATE")
        cur.execute('UPDATE btgf SET basetime = {}, gndfigure = {} WHERE id = {}'.format(basetime, gndfigure, row_fetched[0][0]))

    conn.commit()

    cur.close()
    conn.close()





def calcBaseTimeFigureAndGndFigureWithoutDup(logger, data_dir, race_data_list, horse_data_list, scr_race_data_list):
    # 過去の戦績（重複なし）
    scr_race_data_list_shr = []
    for i in range(len(scr_race_data_list)):
        for j in range(len(scr_race_data_list[i])):
            place = scr_race_data_list[i][j][0]
            if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
                weather = scr_race_data_list[i][j][1]
                burden_weight = scr_race_data_list[i][j][2]
                race_course_gnd = scr_race_data_list[i][j][3]
                distance = scr_race_data_list[i][j][4]
                ground_status = scr_race_data_list[i][j][5]
                goal_time = scr_race_data_list[i][j][6]
                scr_race_data_list_shr.append([place, distance, race_course_gnd, weather, ground_status])
    scr_race_data_list_shr = get_unique_list(scr_race_data_list_shr)
    logger.log(20, "len scr_race_data_list_shr:{}".format(len(scr_race_data_list_shr)))


    # 過去の戦績（重複なし）に対する　ベースタイム　と　馬場指数
    base_time_and_gnd_figure_list = []
    for i in range(len(scr_race_data_list_shr)):
        base_time, gf = calcBaseTimeFigureAndGndFigure(logger, data_dir, race_data_list, horse_data_list, scr_race_data_list_shr[i][0], scr_race_data_list_shr[i][1], scr_race_data_list_shr[i][2], scr_race_data_list_shr[i][3], scr_race_data_list_shr[i][4])
        base_time_and_gnd_figure_list.append([base_time, gf])


    return base_time_and_gnd_figure_list, scr_race_data_list_shr



# 距離指数の計算
def calcDistanceFigure(base_time):
    return 100 / base_time



def calcSpeedFigure(logger, scr_name_list, scr_race_data_list, scr_race_data_list_shr, base_time_and_gnd_figure_list):
    scr_result_ave = []
    scr_result_list = []
    for i in range(len(scr_name_list)):
        try:
            logger.log(20, scr_name_list[i])
            logger.log(20, "")
            # 出走馬の過去の戦績
            scr_race_data = scr_race_data_list[i]
            speed_figure_list = []
            race_distance_list = []
            for j in range(len(scr_race_data)):
                place = scr_race_data[j][0]
                if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
                    weather = scr_race_data[j][1]
                    burden_weight = scr_race_data[j][2]
                    race_course_gnd = scr_race_data[j][3]
                    distance = scr_race_data[j][4]
                    ground_status = scr_race_data[j][5]
                    goal_time = scr_race_data[j][6]
                    #try:
                    idx = scr_race_data_list_shr.index([place, distance, race_course_gnd, weather, ground_status])
                    tmp = base_time_and_gnd_figure_list[idx]
                    base_time = tmp[0]
                    gf = tmp[1]

                    # ゴールタイム表記変換
                    """
                    gt = goal_time.split(":")
                    if len(gt) == 1:
                        goal_time = float(gt[0])
                    elif len(gt) == 2:
                        goal_time = float(gt[1]) + float(gt[0])*60
                    else:
                        goal_time = None
                    """
                    #logger.log(20, "goal_time = {}".format(goal_time))
                    # ベースタイム算出
                    #logger.log(20, "base_time = {}".format(base_time))
                    # 距離指数算出
                    df = calcDistanceFigure(base_time)
                    #logger.log(20, "df = {}".format(df))
                    # 馬場指数算出
                    if gf == None or goal_time == None or base_time == None:

                        continue

                    #logger.log(20, "gf = {}".format(gf))
                    # スピード指数算出
                    speed_figure = (base_time*10 - goal_time*10) * df + gf + (burden_weight - 55) * 2 + 80
                    #logger.log(20, "speed_figure = {}".format(speed_figure))

                    speed_figure_list.append(speed_figure)
                    race_distance_list.append(int(distance))

                    #except:
                    #    logger.log(20, "can not find")
                    #    logger.log(20, [place, distance, race_course_gnd, weather, ground_status])

            ave_speed_figure = statistics.mean(speed_figure_list)
            std_speed_figure = statistics.pstdev(speed_figure_list)
            logger.log(20, "[ave] speed_figure = {}".format(ave_speed_figure))
            logger.log(20, "[std] speed_figure = {}".format(std_speed_figure))

            scr_result_ave.append([scr_name_list[i], ave_speed_figure])

            # グラフ生成などに必要なデータを格納
            scr_result_list.append([speed_figure_list, race_distance_list])

        except Exception as e:
            logger.log(20, '=== エラー内容 ===')
            logger.log(20, 'type:' + str(type(e)))
            logger.log(20, 'args:' + str(e.args))
            logger.log(20, 'e自身:' + str(e))
            logger.log(20, scr_result_ave)

    logger.log(20, "## org ##")
    logger.log(20, scr_result_ave)
    logger.log(20, "## sorted ##")
    logger.log(20, sorted(scr_result_ave, reverse=True, key=lambda x: x[1]))


    return scr_result_list




def genJockeySpeedFigureAndDistanceFig(result_dir, race_smp_num, jockey_name_list, jockey_result_list):
    for i in range(len(jockey_name_list)):
        jockey_result_speed_figure = jockey_result_list[i][0]
        jockey_result_distance = jockey_result_list[i]["race_course_m"]

        plt.clf()
        plt.scatter(jockey_result_distance, jockey_result_speed_figure)
        plt.xlabel('Distance')
        plt.ylabel('Speed Figure')
        plt.title('race_smp_num={}'.format(len(jockey_result_speed_figure)),loc='left',fontsize=20)
        plt.xlim(900,3600)
        plt.ylim(0.0,150)
        #plt.grid(True)
        plt.savefig(result_dir + "/image/jockey/eda_distance_and_speed_figure" + '/Speed_Figure_Distance_{}.png'.format(jockey_name_list[i]))
        plt.close()



def genJockeyRankAndDistanceFig(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list):
    for i in range(len(jockey_race_data_list)):
        jockey_result_rank = []
        jockey_result_distance = []
        for j in range(len(jockey_race_data_list[i])):
            if type(jockey_race_data_list[i][j]["rank"]) == int and type(jockey_race_data_list[i][j]["race_course_m"] == int):
                jockey_result_rank.append(jockey_race_data_list[i][j]["rank"])
                jockey_result_distance.append(jockey_race_data_list[i][j]["race_course_m"])

        plt.clf()

        H = plt.hist2d(jockey_result_distance, jockey_result_rank, bins=[np.linspace(900,3600,28),np.linspace(0,20,21)], cmap=cm.jet)
        plt.colorbar(H[3])


        #plt.scatter(jockey_result_distance, jockey_result_rank)
        plt.xlabel('Distance')
        plt.ylabel('Rank')
        plt.title('race_smp_num={}'.format(len(jockey_result_rank)),loc='left',fontsize=20)
        #plt.xlim(900,3600)
        plt.ylim(20,0)
        #plt.grid(True)
        plt.savefig(result_dir + "/image/jockey/eda_distance_and_rank" + '/Rank_Distance_{}.png'.format(jockey_name_list[i]))
        plt.close()




def genJockeyFrameNumberAndRankFig(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list):

    for i in range(len(jockey_race_data_list)):
        jockey_result_rank = []
        jockey_result_frame_number = []
        jockey_result_distance = []
        for j in range(len(jockey_race_data_list[i])):
            if type(jockey_race_data_list[i][j]["rank"]) == int and type(jockey_race_data_list[i][j]["frame_number"] == int):
                jockey_result_rank.append(jockey_race_data_list[i][j]["rank"])
                jockey_result_frame_number.append(jockey_race_data_list[i][j]["frame_number"])
                jockey_result_distance.append(jockey_race_data_list[i][j]["race_course_m"])

        plt.clf()

        H = plt.hist2d(jockey_result_frame_number, jockey_result_rank, bins=[np.linspace(0,10,11),np.linspace(0,20,21)], cmap=cm.jet)
        plt.colorbar(H[3])


        #plt.scatter(jockey_result_frame_number, jockey_result_rank)
        plt.xlabel('Frame Number')
        plt.ylabel('Rank')
        plt.title('race_smp_num={}'.format(len(jockey_result_rank)),loc='left',fontsize=20)
        #plt.xlim(0,10)
        plt.ylim(20,0)
        #plt.grid(True)
        plt.savefig(result_dir + "/image/jockey/eda_distance_and_frame_number" + '/Rank_Frame_Number_{}.png'.format(jockey_name_list[i]))
        plt.close()




def genJockeyFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list):
    dis_range = [1000, 1400, 1800, 2200, 2600, 3000, 3400]
    for k in range(len(dis_range) - 1):
        for i in range(len(jockey_race_data_list)):
            jockey_folder = "/" + jockey_name_list[i]
            jockey_path = result_dir + "/image/jockey/eda_distance_and_frame_number_distance" + jockey_folder
            if not os.path.exists(jockey_path):
                os.mkdir(jockey_path)
            jockey_result_rank = []
            jockey_result_frame_number = []
            jockey_result_distance = []
            for j in range(len(jockey_race_data_list[i])):
                if type(jockey_race_data_list[i][j]["rank"]) == int and \
                    type(jockey_race_data_list[i][j]["frame_number"] == int) and \
                    type(jockey_race_data_list[i][j]["race_course_m"] == int):
                    if dis_range[k] < jockey_race_data_list[i][j]["race_course_m"] and jockey_race_data_list[i][j]["race_course_m"] < dis_range[k+1] - 1:
                        jockey_result_rank.append(jockey_race_data_list[i][j]["rank"])
                        jockey_result_frame_number.append(jockey_race_data_list[i][j]["frame_number"])
                        jockey_result_distance.append(jockey_race_data_list[i][j]["race_course_m"])

            plt.clf()
            H = plt.hist2d(jockey_result_frame_number, jockey_result_rank, bins=[np.linspace(0,10,11),np.linspace(0,20,21)], cmap=cm.jet)
            H[3].set_clim(0,15)
            plt.colorbar(H[3])
            plt.xlabel('Frame Number')
            plt.ylabel('Rank')
            plt.title('race_smp_num={}, distance={}-{}'.format(len(jockey_result_rank), dis_range[k], dis_range[k+1] - 1),loc='left',fontsize=15)
            #plt.xlim(0,10)
            plt.ylim(20,0)
            plt.savefig(result_dir + "/image/jockey/eda_distance_and_frame_number_distance" + jockey_folder + '/Rank_Frame_Number_{}_{}-{}.png'.format(jockey_name_list[i], dis_range[k], dis_range[k+1] - 1))
            plt.close()





def genTamerRankAndDistanceFig(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list):
    tamer_folder = "/eda_distance_and_rank"
    tamer_path = result_dir + "/image/tamer" + tamer_folder
    if not os.path.exists(tamer_path):
        os.mkdir(tamer_path)

    for i in range(len(tamer_race_data_list)):
        tamer_result_rank = []
        tamer_result_distance = []
        for j in range(len(tamer_race_data_list[i])):
            if type(tamer_race_data_list[i][j]["rank"]) == int and type(tamer_race_data_list[i][j]["race_course_m"] == int):
                tamer_result_rank.append(tamer_race_data_list[i][j]["rank"])
                tamer_result_distance.append(tamer_race_data_list[i][j]["race_course_m"])

        plt.clf()

        H = plt.hist2d(tamer_result_distance, tamer_result_rank, bins=[np.linspace(900,3600,28),np.linspace(0,20,21)], cmap=cm.jet)
        plt.colorbar(H[3])


        #plt.scatter(tamer_result_distance, tamer_result_rank)
        plt.xlabel('Distance')
        plt.ylabel('Rank')
        plt.title('race_smp_num={}'.format(len(tamer_result_rank)),loc='left',fontsize=20)
        #plt.xlim(900,3600)
        plt.ylim(20,0)
        #plt.grid(True)
        plt.savefig(result_dir + "/image/tamer/eda_distance_and_rank" + '/Rank_Distance_{}.png'.format(tamer_name_list[i]))
        plt.close()






def genTamerFrameNumberAndRankFig(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list):
    tamer_folder = "/eda_distance_and_frame_number"
    tamer_path = result_dir + "/image/tamer" + tamer_folder
    if not os.path.exists(tamer_path):
        os.mkdir(tamer_path)

    for i in range(len(tamer_race_data_list)):
        tamer_result_rank = []
        tamer_result_frame_number = []
        tamer_result_distance = []
        for j in range(len(tamer_race_data_list[i])):
            if type(tamer_race_data_list[i][j]["rank"]) == int and type(tamer_race_data_list[i][j]["frame_number"] == int):
                tamer_result_rank.append(tamer_race_data_list[i][j]["rank"])
                tamer_result_frame_number.append(tamer_race_data_list[i][j]["frame_number"])
                tamer_result_distance.append(tamer_race_data_list[i][j]["race_course_m"])

        plt.clf()

        H = plt.hist2d(tamer_result_frame_number, tamer_result_rank, bins=[np.linspace(0,10,11),np.linspace(0,20,21)], cmap=cm.jet)
        plt.colorbar(H[3])


        #plt.scatter(tamer_result_frame_number, tamer_result_rank)
        plt.xlabel('Frame Number')
        plt.ylabel('Rank')
        plt.title('race_smp_num={}'.format(len(tamer_result_rank)),loc='left',fontsize=20)
        #plt.xlim(0,10)
        plt.ylim(20,0)
        #plt.grid(True)
        plt.savefig(result_dir + "/image/tamer/eda_distance_and_frame_number" + '/Rank_Frame_Number_{}.png'.format(tamer_name_list[i]))
        plt.close()




def genTamerFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list):
    tamer_folder = "/eda_distance_and_frame_number_distance"
    tamer_path = result_dir + "/image/tamer" + tamer_folder
    if not os.path.exists(tamer_path):
        os.mkdir(tamer_path)

    dis_range = [1000, 1400, 1800, 2200, 2600, 3000, 3400]
    for k in range(len(dis_range) - 1):
        for i in range(len(tamer_race_data_list)):
            tamer_folder = "/" + tamer_name_list[i]
            tamer_path = result_dir + "/image/tamer/eda_distance_and_frame_number_distance" + tamer_folder
            if not os.path.exists(tamer_path):
                os.mkdir(tamer_path)
            tamer_result_rank = []
            tamer_result_frame_number = []
            tamer_result_distance = []
            for j in range(len(tamer_race_data_list[i])):
                if type(tamer_race_data_list[i][j]["rank"]) == int and \
                    type(tamer_race_data_list[i][j]["frame_number"] == int) and \
                    type(tamer_race_data_list[i][j]["race_course_m"] == int):
                    if dis_range[k] < tamer_race_data_list[i][j]["race_course_m"] and tamer_race_data_list[i][j]["race_course_m"] < dis_range[k+1] - 1:
                        tamer_result_rank.append(tamer_race_data_list[i][j]["rank"])
                        tamer_result_frame_number.append(tamer_race_data_list[i][j]["frame_number"])
                        tamer_result_distance.append(tamer_race_data_list[i][j]["race_course_m"])

            plt.clf()
            H = plt.hist2d(tamer_result_frame_number, tamer_result_rank, bins=[np.linspace(0,10,11),np.linspace(0,20,21)], cmap=cm.jet)
            plt.colorbar(H[3])
            plt.xlabel('Frame Number')
            plt.ylabel('Rank')
            plt.title('race_smp_num={}, distance={}-{}'.format(len(tamer_result_rank), dis_range[k], dis_range[k+1] - 1),loc='left',fontsize=15)
            #plt.xlim(0,10)
            plt.ylim(20,0)
            plt.savefig(result_dir + "/image/tamer/eda_distance_and_frame_number_distance" + tamer_folder + '/Rank_Frame_Number_{}_{}-{}.png'.format(tamer_name_list[i], dis_range[k], dis_range[k+1] - 1))
            plt.close()





def genBloodRankAndDistanceFig(result_dir, race_smp_num, horse_name_list, blood_race_data_list):
    blood_folder = "/eda_distance_and_rank"
    blood_path = result_dir + "/image/blood" + blood_folder
    if not os.path.exists(blood_path):
        os.mkdir(blood_path)

    for i in range(len(blood_race_data_list)):
        blood_result_rank = []
        blood_result_distance = []
        for j in range(len(blood_race_data_list[i])):
            if type(blood_race_data_list[i][j]["rank"]) == int and type(blood_race_data_list[i][j]["race_course_m"] == int):
                blood_result_rank.append(blood_race_data_list[i][j]["rank"])
                blood_result_distance.append(blood_race_data_list[i][j]["race_course_m"])

        plt.clf()

        H = plt.hist2d(blood_result_distance, blood_result_rank, bins=[np.linspace(900,3600,28),np.linspace(0,20,21)], cmap=cm.jet)
        plt.colorbar(H[3])


        #plt.scatter(blood_result_distance, blood_result_rank)
        plt.xlabel('Distance')
        plt.ylabel('Rank')
        plt.title('race_smp_num={}'.format(len(blood_result_rank)),loc='left',fontsize=20)
        #plt.xlim(900,3600)
        plt.ylim(20,0)
        #plt.grid(True)
        plt.savefig(result_dir + "/image/blood/eda_distance_and_rank" + '/Rank_Distance_{}.png'.format(horse_name_list[i]))
        plt.close()




def genBloodFrameNumberAndRankFig(result_dir, race_smp_num, blood_name_list, blood_race_data_list):
    blood_folder = "/eda_distance_and_frame_number"
    blood_path = result_dir + "/image/blood" + blood_folder
    if not os.path.exists(blood_path):
        os.mkdir(blood_path)

    for i in range(len(blood_race_data_list)):
        blood_result_rank = []
        blood_result_frame_number = []
        blood_result_distance = []
        for j in range(len(blood_race_data_list[i])):
            if type(blood_race_data_list[i][j]["rank"]) == int and type(blood_race_data_list[i][j]["frame_number"] == int):
                blood_result_rank.append(blood_race_data_list[i][j]["rank"])
                blood_result_frame_number.append(blood_race_data_list[i][j]["frame_number"])
                blood_result_distance.append(blood_race_data_list[i][j]["race_course_m"])

        plt.clf()

        H = plt.hist2d(blood_result_frame_number, blood_result_rank, bins=[np.linspace(0,10,11),np.linspace(0,20,21)], cmap=cm.jet)
        plt.colorbar(H[3])


        #plt.scatter(blood_result_frame_number, blood_result_rank)
        plt.xlabel('Frame Number')
        plt.ylabel('Rank')
        plt.title('race_smp_num={}'.format(len(blood_result_rank)),loc='left',fontsize=20)
        #plt.xlim(0,10)
        plt.ylim(20,0)
        #plt.grid(True)
        plt.savefig(result_dir + "/image/blood/eda_distance_and_frame_number" + '/Rank_Frame_Number_{}.png'.format(blood_name_list[i]))
        plt.close()




def genBloodFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, blood_name_list, blood_race_data_list):
    blood_folder = "/eda_distance_and_frame_number_distance"
    blood_path = result_dir + "/image/blood" + blood_folder
    if not os.path.exists(blood_path):
        os.mkdir(blood_path)

    dis_range = [1000, 1400, 1800, 2200, 2600, 3000, 3400]
    for k in range(len(dis_range) - 1):
        for i in range(len(blood_race_data_list)):
            blood_folder = "/" + blood_name_list[i]
            blood_path = result_dir + "/image/blood/eda_distance_and_frame_number_distance" + blood_folder
            if not os.path.exists(blood_path):
                os.mkdir(blood_path)
            blood_result_rank = []
            blood_result_frame_number = []
            blood_result_distance = []
            for j in range(len(blood_race_data_list[i])):
                if type(blood_race_data_list[i][j]["rank"]) == int and \
                    type(blood_race_data_list[i][j]["frame_number"] == int) and \
                    type(blood_race_data_list[i][j]["race_course_m"] == int):
                    if dis_range[k] < blood_race_data_list[i][j]["race_course_m"] and blood_race_data_list[i][j]["race_course_m"] < dis_range[k+1] - 1:
                        blood_result_rank.append(blood_race_data_list[i][j]["rank"])
                        blood_result_frame_number.append(blood_race_data_list[i][j]["frame_number"])
                        blood_result_distance.append(blood_race_data_list[i][j]["race_course_m"])

            plt.clf()
            H = plt.hist2d(blood_result_frame_number, blood_result_rank, bins=[np.linspace(0,10,11),np.linspace(0,20,21)], cmap=cm.jet)
            plt.colorbar(H[3])
            plt.xlabel('Frame Number')
            plt.ylabel('Rank')
            plt.title('race_smp_num={}, distance={}-{}'.format(len(blood_result_rank), dis_range[k], dis_range[k+1] - 1),loc='left',fontsize=15)
            #plt.xlim(0,10)
            plt.ylim(20,0)
            plt.savefig(result_dir + "/image/blood/eda_distance_and_frame_number_distance" + blood_folder + '/Rank_Frame_Number_{}_{}-{}.png'.format(blood_name_list[i], dis_range[k], dis_range[k+1] - 1))
            plt.close()




def get_unique_list(seq):
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]




def calcJockeySpeedFigure(logger, race_url, data_dir, result_dir, race_smp_num):

    start = time.time()

    # sqlデータの読み込み
    horse_data_list = readHorseSqlDatabase(data_dir)
    race_data_list = readRaceSqlDatabase(data_dir)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    # 開催レース基本情報のスクレイピング
    distance, race_course_gnd, place, frame_number_list = scrRaceData(logger, data_dir, race_url)
    logger.log(20, "race distance = {}".format(distance))
    logger.log(20, "race race_course_gnd = {}".format(race_course_gnd))
    logger.log(20, "race place = {}".format(place))
    logger.log(20, "frame_number_list = {}".format(frame_number_list))
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))
    
    # 出走馬のURLと名前をスクレイピング
    horse_url_list, horse_name_list = scrHorseRaceNameAndUrl(logger, race_url)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    
    """
    debug_idx = -1
    for i in range(len(horse_name_list)):
        if horse_name_list[i] == "エイペクス":
            debug_idx = i
    horse_name_list = [horse_name_list[debug_idx]]
    horse_url_list = [horse_url_list[debug_idx]]
    """


    # ジョッキーのURLと名前をスクレイピング
    jockey_url_list, jockey_name_list = scrJockeyRaceNameAndUrl(logger, race_url)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))
    
    # 調教師のURLと名前をスクレイピング
    tamer_url_list, tamer_name_list = scrTamerRaceNameAndUrl(logger, race_url)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    # ジョッキーのレース成績をSQLから取得
    jockey_race_data_list = scrJockeyRaceDataFromSQL(logger, data_dir, race_url, race_smp_num, jockey_url_list, jockey_name_list)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    # 調教師のレース成績をSQLから取得
    tamer_race_data_list = scrTamerRaceDataFromSQL(logger, data_dir, race_url, race_smp_num, tamer_url_list, tamer_name_list)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    # 出走馬の血統情報をデータベース書き込み
    scrHorseBloodline(logger, race_url, data_dir)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    # 出走馬の血統馬のレース成績をSQLから取得
    blood_race_data_list = scrBloodRaceDataFromSQL(logger, data_dir, race_url, race_smp_num, horse_url_list, horse_name_list)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    """
    # ジョッキーのベースタイムと馬場指数を算出
    jockey_base_time_and_gnd_figure_list, jockey_race_data_list_shr = calcBaseTimeFigureAndGndFigureWithoutDup(logger, data_dir, race_data_list, horse_data_list, jockey_race_data_list)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    # スピード指数の計算
    jockey_result_list = calcSpeedFigure(logger, jockey_name_list, jockey_race_data_list, jockey_race_data_list_shr, jockey_base_time_and_gnd_figure_list)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    # スピード指数対距離のグラフ描画
    genJockeySpeedFigureAndDistanceFig(result_dir, race_smp_num, jockey_name_list, jockey_result_list)
    """
    # 着順対距離のグラフ描画（ジョッキー）
    genJockeyRankAndDistanceFig(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対距離のグラフ描画（ジョッキー）
    genJockeyFrameNumberAndRankFig(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対距離のグラフ描画（ジョッキー）
    genJockeyFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対距離のグラフ描画（調教師）
    genTamerRankAndDistanceFig(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対距離のグラフ描画（調教師）
    genTamerFrameNumberAndRankFig(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対距離のグラフ描画（調教師）
    genTamerFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対距離のグラフ描画（出走馬の血統馬）
    genBloodRankAndDistanceFig(result_dir, race_smp_num, horse_name_list, blood_race_data_list)

    # 着順対距離のグラフ描画（出走馬の血統馬）
    genBloodFrameNumberAndRankFig(result_dir, race_smp_num, horse_name_list, blood_race_data_list)

    # 着順対距離のグラフ描画（出走馬の血統馬）
    genBloodFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, horse_name_list, blood_race_data_list)


if __name__ == "__main__":

    # 開催レースのURL
    race_url_list = [
        "https://race.netkeiba.com/race/shutuba.html?race_id=202109030411&rf=race_list"
    ]
    data_dir = "../../data"
    result_dir = "../../result"
    race_smp_num = 1000

    for race_url in race_url_list:
        # ロガーの初期化
        log_name = "[eda]" + race_url.split("?")[-1].split("&")[0]
        logger = init_logger(result_dir + "/log", log_name)

        logger.log(20, "XXXXXXXXXXXXXXXXXXX")
        logger.log(20, log_name)
        logger.log(20, "XXXXXXXXXXXXXXXXXXX")

        calcJockeySpeedFigure(logger, race_url, data_dir, result_dir, race_smp_num)


