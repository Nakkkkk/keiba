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
from lib_fig import *
from lib_calc import *


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


