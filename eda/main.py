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


#from lib_scr import *
#from lib_db import *
#from lib_fig import *
#from lib_calc import *

from common_import import *

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






def stateCalcJockeySpeedFigure(logger, race_url, data_dir, result_dir, race_smp_num, foal_smp_num):


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

    # 着順対枠のグラフ描画（ジョッキー）
    genJockeyFrameNumberAndRankFig(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対枠対距離のグラフ描画（ジョッキー）
    genJockeyFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, jockey_name_list, jockey_race_data_list)

    # 着順対距離のグラフ描画（調教師）
    genTamerRankAndDistanceFig(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対枠のグラフ描画（調教師）
    genTamerFrameNumberAndRankFig(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対枠対距離のグラフ描画（調教師）
    genTamerFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, tamer_name_list, tamer_race_data_list)

    # 着順対距離のグラフ描画（出走馬の血統馬）
    genBloodRankAndDistanceFig(result_dir, race_smp_num, horse_name_list, blood_race_data_list)

    # 着順対枠のグラフ描画（出走馬の血統馬）
    genBloodFrameNumberAndRankFig(result_dir, race_smp_num, horse_name_list, blood_race_data_list)

    # 着順対枠対距離のグラフ描画（出走馬の血統馬）
    genBloodFrameNumberAndRankFigAndDistance(result_dir, race_smp_num, horse_name_list, blood_race_data_list)




if __name__ == "__main__":

    # 開催レースのURL
    race_url_list = [
        "https://race.netkeiba.com/race/shutuba.html?race_id=202103010211&rf=race_list"
    ]
    data_dir = "../../data"
    result_dir = "../../result"
    race_smp_num = 10
    foal_smp_num = 5

    for race_url in race_url_list:
        # ロガーの初期化
        log_name = "[eda]" + race_url.split("?")[-1].split("&")[0]
        logger = init_logger(result_dir + "/log", log_name)

        logger.log(20, "XXXXXXXXXXXXXXXXXXX")
        logger.log(20, log_name)
        logger.log(20, "XXXXXXXXXXXXXXXXXXX")

        stateCalcJockeySpeedFigure(logger, race_url, data_dir, result_dir, race_smp_num, foal_smp_num)

