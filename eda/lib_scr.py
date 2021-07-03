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


#from lib_db import *
#from lib_fig import *
#from lib_calc import *

from common_import import *




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
        #updateDatabeseBloodFather(logger, data_dir, -1,-1) # debug
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
    
    conn_h.commit()
    cur_h.close()
    conn_h.close()

    conn_r.commit()
    cur_r.close()
    conn_r.close()

    conn_bf.commit()
    cur_bf.close()
    conn_bf.close()

    return blood_race_data_list




