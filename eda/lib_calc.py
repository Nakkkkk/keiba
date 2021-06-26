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


from lib_scr import *
from lib_db import *
from lib_fig import *




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

    # ジョッキーのURLと名前をスクレイピング
    jockey_url_list, jockey_name_list = scrJockeyRaceNameAndUrl(logger, race_url)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))
 
    # ジョッキーのレース成績をSQLから取得
    jockey_race_data_list = scrJockeyRaceDataFromSQL(logger, data_dir, race_url, race_smp_num, jockey_url_list, jockey_name_list)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

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





def calcJockeySpeedFigure(logger, race_url, data_dir, result_dir, race_smp_num):

    start = time.time()

    # sqlデータの読み込み
    horse_data_list = readHorseSqlDatabase(data_dir)
    race_data_list = readRaceSqlDatabase(data_dir)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    """
    # 出走馬のURLと名前をスクレイピング
    horse_url_list, horse_name_list = scrHorseRaceNameAndUrl(logger, race_url)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    # ジョッキーのURLと名前をスクレイピング
    jockey_url_list, jockey_name_list = scrJockeyRaceNameAndUrl(logger, race_url)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))
    """

    # 調教師のURLと名前をスクレイピング
    tamer_url_list, tamer_name_list = scrTamerRaceNameAndUrl(logger, race_url)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))

    """
    # ジョッキーのレース成績をSQLから取得
    jockey_race_data_list = scrJockeyRaceDataFromSQL(logger, data_dir, race_url, race_smp_num, jockey_url_list, jockey_name_list)
    rap_time = time.time() - start
    logger.log(20, "rap_time:{0}[sec]".format(rap_time))
    """

    # 調教師のレース成績をSQLから取得
    tamer_race_data_list = scrTamerRaceDataFromSQL(logger, data_dir, race_url, race_smp_num, tamer_url_list, tamer_name_list)
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
    #genJockeyRankAndDistanceFig(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対距離のグラフ描画（ジョッキー）
    #genJockeyFrameNumberAndRankFig(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対距離のグラフ描画（ジョッキー）
    #genJockeyFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対距離のグラフ描画（調教師）
    #genTamerRankAndDistanceFig(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対距離のグラフ描画（調教師）
    genTamerFrameNumberAndRankFig(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対距離のグラフ描画（調教師）
    #genTamerFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)
