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
from lib_calc import *


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




if __name__ == "__main__":

    # 開催レースのURL
    race_url_list = [
        "https://race.netkeiba.com/race/shutuba.html?race_id=202105030606&rf=race_submenu"
    ]
    data_dir = "../../data"
    result_dir = "../../result"
    race_smp_num = 10

    for race_url in race_url_list:
        # ロガーの初期化
        log_name = "[eda]" + race_url.split("?")[-1].split("&")[0]
        logger = init_logger(result_dir + "/log", log_name)

        logger.log(20, "XXXXXXXXXXXXXXXXXXX")
        logger.log(20, log_name)
        logger.log(20, "XXXXXXXXXXXXXXXXXXX")

        calcJockeySpeedFigure(logger, race_url, data_dir, result_dir, race_smp_num)