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





def scrBloodRaceDataFromSQL(logger, data_dir, race_url, foal_smp_num, horse_url_list, horse_name_list):
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

            # データからfoal_smp_num個無作為抽出
            if foal_smp_num <= len(foal_id_list):
                foal_id_list_idx_random_list = rand_ints_nodup(0, len(foal_id_list) - 1, foal_smp_num) 
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









def calcJockeyAveRankForDistance(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list, distance):
    rank_ave_list = []
    for i in range(len(jockey_race_data_list)):
        jockey_result_rank = []
        jockey_result_distance = []
        for j in range(len(jockey_race_data_list[i])):
            if type(jockey_race_data_list[i][j]["rank"]) == int and type(jockey_race_data_list[i][j]["race_course_m"] == int):
                jockey_result_rank.append(jockey_race_data_list[i][j]["rank"])
                jockey_result_distance.append(jockey_race_data_list[i][j]["race_course_m"])

        plt.clf()

        H = plt.hist2d(jockey_result_distance, jockey_result_rank, bins=[np.linspace(900,3600,28),np.linspace(0,20,21)], cmap=cm.jet)

        rank_ave = 0
        for dis_idx in range(len(H[1])):
            if H[1][dis_idx] == distance:
                rank_degree_list = H[0][dis_idx]
                rank_num = 0
                for rd_idx in range(len(rank_degree_list)):
                    rank_ave += rank_degree_list[rd_idx] * H[2][rd_idx]
                    rank_num += rank_degree_list[rd_idx]
                rank_ave /= rank_num
        rank_ave_list.append(rank_ave)

        logger.log(20, "[Jockey][dis] {} ave rank = {:.2f}".format(jockey_name_list[i], rank_ave))

        plt.close()

    return rank_ave_list




def calcTamerAveRankForDistance(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list, distance):
    rank_ave_list = []
    for i in range(len(tamer_race_data_list)):
        tamer_result_rank = []
        tamer_result_distance = []
        for j in range(len(tamer_race_data_list[i])):
            if type(tamer_race_data_list[i][j]["rank"]) == int and type(tamer_race_data_list[i][j]["race_course_m"] == int):
                tamer_result_rank.append(tamer_race_data_list[i][j]["rank"])
                tamer_result_distance.append(tamer_race_data_list[i][j]["race_course_m"])

        plt.clf()

        H = plt.hist2d(tamer_result_distance, tamer_result_rank, bins=[np.linspace(900,3600,28),np.linspace(0,20,21)], cmap=cm.jet)

        rank_ave = 0
        for dis_idx in range(len(H[1])):
            if H[1][dis_idx] == distance:
                rank_degree_list = H[0][dis_idx]
                rank_num = 0
                for rd_idx in range(len(rank_degree_list)):
                    rank_ave += rank_degree_list[rd_idx] * H[2][rd_idx]
                    rank_num += rank_degree_list[rd_idx]
                rank_ave /= rank_num
        rank_ave_list.append(rank_ave)

        logger.log(20, "[Tamer][dis] {} ave rank = {:.2f}".format(tamer_name_list[i], rank_ave))

        plt.close()

    return rank_ave_list




def calcBloodAveRankForDistance(result_dir, race_smp_num, horse_name_list, blood_race_data_list, distance):
    rank_ave_list = []
    for i in range(len(blood_race_data_list)):
        blood_result_rank = []
        blood_result_distance = []
        for j in range(len(blood_race_data_list[i])):
            if type(blood_race_data_list[i][j]["rank"]) == int and type(blood_race_data_list[i][j]["race_course_m"] == int):
                blood_result_rank.append(blood_race_data_list[i][j]["rank"])
                blood_result_distance.append(blood_race_data_list[i][j]["race_course_m"])

        plt.clf()

        H = plt.hist2d(blood_result_distance, blood_result_rank, bins=[np.linspace(900,3600,28),np.linspace(0,20,21)], cmap=cm.jet)

        rank_ave = 0
        for dis_idx in range(len(H[1])):
            if H[1][dis_idx] == distance:
                rank_degree_list = H[0][dis_idx]
                rank_num = 0
                for rd_idx in range(len(rank_degree_list)):
                    rank_ave += rank_degree_list[rd_idx] * H[2][rd_idx]
                    rank_num += rank_degree_list[rd_idx]
                rank_ave /= rank_num
        rank_ave_list.append(rank_ave)

        logger.log(20, "[Blood][dis] {} ave rank = {:.2f}".format(horse_name_list[i], rank_ave))

        plt.close()
    
    return rank_ave_list



def calcJockeyAveRankForFrameNumber(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list, frame_number_list):
    rank_ave_list = []
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

        rank_ave = 0
        for fn_idx in range(len(H[1])):
            if H[1][fn_idx] == frame_number_list[i]:
                rank_degree_list = H[0][fn_idx]
                rank_num = 0
                for rd_idx in range(len(rank_degree_list)):
                    rank_ave += rank_degree_list[rd_idx] * H[2][rd_idx]
                    rank_num += rank_degree_list[rd_idx]
                rank_ave /= rank_num
        rank_ave_list.append(rank_ave)

        logger.log(20, "[Jockey][fn] {} ave rank = {:.2f}".format(jockey_name_list[i], rank_ave))

        plt.close()

    return rank_ave_list




def calcTamerAveRankForFrameNumber(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list, frame_number_list):
    rank_ave_list = []
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

        rank_ave = 0
        for fn_idx in range(len(H[1])):
            if H[1][fn_idx] == frame_number_list[i]:
                rank_degree_list = H[0][fn_idx]
                rank_num = 0
                for rd_idx in range(len(rank_degree_list)):
                    rank_ave += rank_degree_list[rd_idx] * H[2][rd_idx]
                    rank_num += rank_degree_list[rd_idx]
                rank_ave /= rank_num
        rank_ave_list.append(rank_ave)

        logger.log(20, "[Tamer][fn] {} ave rank = {:.2f}".format(tamer_name_list[i], rank_ave))

        plt.close()

    return rank_ave_list




def calcBloodAveRankForFrameNumber(result_dir, race_smp_num, horse_name_list, blood_race_data_list, frame_number_list):
    rank_ave_list = []
    for i in range(len(blood_race_data_list)):
        blood_result_rank = []
        blood_result_distance = []
        blood_result_frame_number = []
        for j in range(len(blood_race_data_list[i])):
            if type(blood_race_data_list[i][j]["rank"]) == int and type(blood_race_data_list[i][j]["race_course_m"] == int):
                blood_result_rank.append(blood_race_data_list[i][j]["rank"])
                blood_result_frame_number.append(blood_race_data_list[i][j]["frame_number"])
                blood_result_distance.append(blood_race_data_list[i][j]["race_course_m"])

        plt.clf()

        H = plt.hist2d(blood_result_frame_number, blood_result_rank, bins=[np.linspace(900,3600,28),np.linspace(0,20,21)], cmap=cm.jet)
        print(H)

        rank_ave = 0
        for fn_idx in range(len(H[1])):
            if H[1][fn_idx] == frame_number_list[i]:
                rank_degree_list = H[0][fn_idx]
                rank_num = 0
                for rd_idx in range(len(rank_degree_list)):
                    rank_ave += rank_degree_list[rd_idx] * H[2][rd_idx]
                    rank_num += rank_degree_list[rd_idx]
                rank_ave /= rank_num
        rank_ave_list.append(rank_ave)

        logger.log(20, "[Blood][fn] {} ave rank = {:.2f}".format(horse_name_list[i], rank_ave))

        plt.close()
    
    return rank_ave_list






def get_unique_list(seq):
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]




def calcJockeySpeedFigure(logger, race_url, data_dir, result_dir, race_smp_num, foal_smp_num):

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
    blood_race_data_list = scrBloodRaceDataFromSQL(logger, data_dir, race_url, foal_smp_num, horse_url_list, horse_name_list)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    # 着順対距離のグラフ描画（ジョッキー）
    #genJockeyRankAndDistanceFig(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対距離のグラフ描画（ジョッキー）
    #genJockeyFrameNumberAndRankFig(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対距離のグラフ描画（ジョッキー）
    #genJockeyFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対距離のグラフ描画（調教師）
    #genTamerRankAndDistanceFig(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対距離のグラフ描画（調教師）
    #genTamerFrameNumberAndRankFig(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対距離のグラフ描画（調教師）
    #genTamerFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対距離のグラフ描画（出走馬の血統馬）
    genBloodRankAndDistanceFig(result_dir, race_smp_num, horse_name_list, blood_race_data_list)

    # 着順対距離のグラフ描画（出走馬の血統馬）
    genBloodFrameNumberAndRankFig(result_dir, race_smp_num, horse_name_list, blood_race_data_list)

    # 着順対距離のグラフ描画（出走馬の血統馬）
    genBloodFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, horse_name_list, blood_race_data_list)

    jockey_rank_ave_for_dist_list = calcJockeyAveRankForDistance(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list, distance)
    tamer_rank_ave_for_dist_list = calcTamerAveRankForDistance(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list, distance)
    blood_rank_ave_for_dist_list = calcBloodAveRankForDistance(result_dir, race_smp_num, horse_name_list, blood_race_data_list, distance)

    jockey_rank_ave_for_fn_list = calcJockeyAveRankForFrameNumber(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list, frame_number_list)
    tamer_rank_ave_for_fn_list = calcTamerAveRankForFrameNumber(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list, frame_number_list)
    blood_rank_ave_for_fn_list = calcBloodAveRankForFrameNumber(result_dir, race_smp_num, horse_name_list, blood_race_data_list, frame_number_list)

    total_rank_ave_list = []
    for i in range(len(horse_name_list)):
        total_rank_ave = (jockey_rank_ave_for_dist_list[i] + tamer_rank_ave_for_dist_list[i] + blood_rank_ave_for_dist_list[i]) / 3
        #total_rank_ave = (jockey_rank_ave_for_dist_list[i] + tamer_rank_ave_for_dist_list[i] + blood_rank_ave_for_dist_list[i] + jockey_rank_ave_for_fn_list[i] + tamer_rank_ave_for_fn_list[i] + blood_rank_ave_for_fn_list[i]) / 6
        total_rank_ave_list.append([total_rank_ave, \
                                    jockey_name_list[i], jockey_rank_ave_for_dist_list[i], jockey_rank_ave_for_fn_list[i], \
                                    tamer_name_list[i], tamer_rank_ave_for_dist_list[i], tamer_rank_ave_for_fn_list[i], \
                                    horse_name_list[i], blood_rank_ave_for_dist_list[i], blood_rank_ave_for_fn_list[i]])
        
    total_rank_ave_list_sorted = sorted(total_rank_ave_list, key=lambda x: x[0])
    for i in range(len(total_rank_ave_list_sorted)):
        tmp_trals = total_rank_ave_list_sorted[i]
        logger.log(20, "total rank ave = {:.2f} [{}, {}, {}]".format(tmp_trals[0], tmp_trals[1], tmp_trals[4], tmp_trals[7]))



if __name__ == "__main__":

    # 開催レースのURL
    race_url_list = [
        "https://race.netkeiba.com/race/shutuba.html?race_id=202109030411&rf=race_list"
    ]
    data_dir = "../data"
    result_dir = "../result"
    race_smp_num = 1000
    foal_smp_num = 50

    for race_url in race_url_list:
        # ロガーの初期化
        log_name = "[pred]" + race_url.split("?")[-1].split("&")[0]
        logger = init_logger(result_dir + "/log", log_name)

        logger.log(20, "XXXXXXXXXXXXXXXXXXX")
        logger.log(20, log_name)
        logger.log(20, "XXXXXXXXXXXXXXXXXXX")

        calcJockeySpeedFigure(logger, race_url, data_dir, result_dir, race_smp_num, foal_smp_num)


