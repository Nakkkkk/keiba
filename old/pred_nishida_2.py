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

    # [ベースタイム] 上記の条件のヒット数が1以下であれば、天候の条件を無視
    if len(gf_ri_list) < 2:
        print("[gf_ri_list] conditions conditions did not hit !")
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

    # [馬場指数] 上記の条件のヒット数が1以下であれば、指定の競馬場　かつ　指定の距離　かつ　芝ダ障　のrace_idをリストにする
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
        gnd_figure = None
    else:
        ave_time = statistics.mean(ave_time_list)
        std_time = statistics.pstdev(ave_time_list)
        stand_base_time = (ave_time - base_time) / std_base_time    # ベースタイムからの標準正規分布におけるave_timeの記録
        stand_time = (base_time - ave_time) / std_time              # ave_timeからの標準正規分布におけるベースタイムの記録
        diff_time = stand_base_time - stand_time                    # ベースタイムより良いタイムが出る馬場だと、数値が低くなる。https://regist.netkeiba.com/?pid=faq_detail&id=1295
        gnd_figure = diff_time * 10

    return base_time, gnd_figure   # 指数として出力するため10かけている



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

    result = []

    # csvデータの読み込み
    csv_dir = "../data/all"
    race_data_list, horse_data_list = read_csv_data(csv_dir)
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))


    # 出走馬リスト
    horse_name_list = ["レイモンドバローズ", "アナザーリリック", "ルークズネスト", "バスラットレオン", "リッケンバッカー", "シティレインボー", "タイムトゥヘヴン", "グレナディアガーズ", "ゴールドチャリス", "ソングライン", "ヴェイルネビュラ", "ランドオブリバティ", "ホウオウアマゾン", "ショックアクション", "シュネルマイスター", "ロードマックス", "グレイイングリーン", "ピクシーナイト"]


    # 出走馬の過去の戦績（重複なし）
    #test_list = [['中山', 2500, 'T', 'S', 'G'], ['東京', 2400, 'T', 'C', 'G'], ['中山', 2500, 'T', 'C', 'G'], ['京都', 3000, 'T', 'S', 'G'], ['阪神', 2400, 'T', 'R0', 'G'], ['阪神', 2000, 'T', 'S', 'H0'], ['京都', 1800, 'T', 'S', 'G'], ['京都', 2000, 'T', 'S', 'G'], ['阪神', 3000, 'T', 'C', 'H1'], ['中山', 2000, 'T', 'C', 'G'], ['中京', 2200, 'T', 'S', 'G'], ['京都', 2200, 'T', 'C', 'G'], ['中山', 2000, 'T', 'S', 'H0'], ['阪神', 2400, 'T', 'S', 'G'], ['京都', 2000, 'T', 'C', 'G'], ['京都', 2000, 'T', 'S', 'H1'], ['中山', 2200, 'T', 'C', 'H0'], ['京都', 2200, 'T', 'R1', 'H1'], ['東京', 2400, 'T', 'C', 'H1'], ['京都', 2000, 'T', 'S', 'H0'], ['中山', 2000, 'T', 'S', 'G'], ['東京', 2400, 'T', 'S', 'G'], ['東京', 1800, 'T', 'S', 'G'], ['東京', 1600, 'T', 'C', 'G'], ['中山', 1600, 'T', 'S', 'G'], ['東京', 1800, 'T', 'C', 'G'], ['中山', 2200, 'T', 'C', ''], ['新潟', 2000, 'T', 'S', 'G'], ['東京', 2000, 'T', 'C', 'G'], ['阪神', 2200, 'T', 'S', 'G'], ['阪神', 1800, 'T', 'S', 'G'], ['京都', 1600, 'T', 'S', 'H0'], ['阪神', 1800, 'T', 'C', 'G'], ['東京', 2000, 'T', 'S', 'G'], ['中山', 2000, 'T', 'C', 'H0'], ['中山', 1800, 'T', 'C', 'H0'], ['阪神', 3200, 'T', 'S', 'G'], ['中京', 2000, 'T', 'S', 'G'], ['中京', 2200, 'T', 'S', 'H1'], ['阪神', 2000, 'T', 'C', 'G'], ['東京', 2500, 'T', 'C', 'G'], ['京都', 3200, 'T', 'C', 'G'], ['阪神', 3000, 'T', 'C', 'G'], ['京都', 3200, 'T', 'S', 'G'], ['東京', 3400, 'T', 'C', 'G'], ['京都', 3000, 'T', 'C', 'G'], ['新潟', 2200, 'T', 'S', 'G'], ['京都', 2200, 'T', 'S', 'G'], ['阪神', 2000, 'T', 'S', 'G'], ['阪神', 2200, 'T', 'C', 'G'], ['中山', 2500, 'T', 'C', 'H0'], ['札幌', 2000, 'T', 'C', 'H0'], ['東京', 2000, 'T', 'R1', ''], ['京都', 2200, 'T', 'S', 'H0'], ['東京', 3400, 'T', 'S', 'G'], ['中京', 3000, 'T', 'C', 'G'], ['東京', 2400, 'T', 'C', 'H0'], ['阪神', 1800, 'T', 'C', 'H1'], ['中京', 2200, 'T', 'C', 'G'], ['新潟', 2200, 'T', 'C', 'H0'], ['新潟', 2400, 'T', 'S', 'G'], ['阪神', 1800, 'D', 'S', 'G'], ['京都', 1800, 'T', 'R1', 'G'], ['京都', 1600, 'T', 'C', 'G'], ['中山', 2000, 'T', 'C', 'H1'], ['函館', 1800, 'T', 'C', 'G'], ['阪神', 2600, 'T', 'S', 'G'], ['小倉', 2600, 'T', 'C', 'H1'], ['阪神', 2400, 'T', 'S', 'H0'], ['京都', 2400, 'T', 'C', 'G'], ['阪神', 2400, 'T', 'C', 'G'], ['阪神', 2600, 'T', 'C', 'G'], ['中京', 2000, 'T', 'R0', 'H0'], ['阪神', 2400, 'T', 'C', 'H0'], ['京都', 2400, 'T', 'S', 'G'], ['小倉', 2000, 'T', 'S', 'G'], ['京都', 1800, 'T', 'C', 'G'], ['京都', 1600, 'T', 'S', 'G'], ['東京', 1400, 'T', 'S', 'G'], ['東京', 1400, 'T', 'R0', 'G'], ['中京', 1200, 'T', 'S', 'G'], ['函館', 1200, 'T', 'S', 'G'], ['東京', 1600, 'T', 'S', 'G'], ['東京', 1400, 'T', 'C', 'H0'], ['中山', 1600, 'T', 'R1', 'H0'], ['中京', 1200, 'T', 'C', 'G'], ['中山', 1600, 'T', 'R1', 'G'], ['中山', 1200, 'T', 'C', 'G'], ['新潟', 1600, 'T', 'S', 'G'], ['福島', 1200, 'T', 'R0', ''], ['東京', 1600, 'T', 'R1', ''], ['中山', 1600, 'T', 'R0', 'G'], ['阪神', 1600, 'T', 'C', 'H0'], ['中山', 1200, 'T', 'S', 'G'], ['新潟', 1400, 'T', 'R1', ''], ['函館', 1200, 'T', 'C', 'G'], ['中京', 1200, 'T', 'R1', 'H0'], ['新潟', 1400, 'T', 'S', 'G'], ['新潟', 1200, 'T', 'S', 'G'], ['新潟', 1600, 'T', 'R0', 'H0'], ['福島', 1200, 'T', 'S', 'G'], ['福島', 1200, 'T', 'C', 'G'], ['福島', 1000, 'D', 'S', 'G'], ['中山', 1200, 'D', 'C', 'G'], ['札幌', 1000, 'D', 'R0', 'H0'], ['札幌', 1000, 'D', 'S', 'G'], ['中山', 3600, 'T', 'R0', 'H0'], ['福島', 2000, 'T', 'C', 'H1'], ['中山', 2200, 'T', 'S', 'G'], ['中山', 2200, 'T', 'C', 'H1'], ['福島', 2600, 'T', 'S', 'G'], ['東京', 2400, 'T', 'R1', ''], ['中山', 2200, 'T', 'C', 'G'], ['中京', 2000, 'T', 'R0', 'G'], ['阪神', 2200, 'T', 'C', 'H0'], ['中山', 3600, 'T', 'S', 'G'], ['中山', 2000, 'T', 'R1', 'H1'], ['阪神', 1800, 'T', '', 'G'], ['京都', 1800, 'T', 'S', 'H0'], ['中山', 2500, 'T', 'S', 'H0'], ['京都', 2400, 'T', 'S', 'H0'], ['小倉', 2600, 'T', 'S', 'H0'], ['福島', 2600, 'T', 'C', 'G'], ['札幌', 2600, 'T', 'S', 'G'], ['函館', 2600, 'T', 'S', 'G'], ['東京', 2400, 'T', 'R0', 'H0'], ['札幌', 1800, 'T', 'C', 'H0'], ['新潟', 1800, 'D', 'S', 'G'], ['阪神', 1800, 'D', 'C', 'H0'], ['阪神', 1800, 'D', 'R0', 'G'], ['東京', 2100, 'D', 'S', 'G'], ['東京', 2100, 'D', 'R0', 'H0'], ['京都', 1800, 'D', 'C', 'H0'], ['中山', 1800, 'D', 'S', 'G'], ['阪神', 2000, 'D', 'S', 'G'], ['京都', 1800, 'D', 'S', 'G'], ['阪神', 1800, 'D', 'S', 'H1'], ['阪神', 1800, 'D', 'S', 'H0'], ['京都', 1800, 'D', 'S', 'H1'], ['京都', 1800, 'D', 'R1', 'H1'], ['小倉', 1700, 'D', 'S', 'G'], ['小倉', 1700, 'D', 'C', 'G'], ['小倉', 1700, 'D', 'S', 'H1'], ['京都', 1800, 'D', 'C', 'H1'], ['阪神', 1800, 'D', 'C', 'H1'], ['小倉', 1800, 'T', 'C', 'G'], ['福島', 2000, 'T', 'S', 'G'], ['福島', 2000, 'T', 'C', 'H0'], ['小倉', 2000, 'T', 'C', 'G'], ['小倉', 2000, 'T', 'R0', 'H1'], ['札幌', 1800, 'T', 'S', 'G'], ['札幌', 2000, 'T', 'S', 'G'], ['函館', 1800, 'T', 'C', 'H0'], ['福島', 1800, 'T', 'S', 'G'], ['中京', 1900, 'D', 'S', 'G'], ['福島', 1800, 'T', 'C', 'G'], ['中京', 1600, 'T', 'S', 'H0'], ['阪神', 1600, 'T', 'C', 'H1'], ['中京', 1600, 'T', 'S', 'G'], ['阪神', 1800, 'T', 'R1', 'G'], ['札幌', 1500, 'T', 'S', 'H0'], ['札幌', 1800, 'T', 'C', 'G'], ['中京', 1600, 'T', 'C', 'G']]
    horse_race_data_list = []
    for i in range(len(horse_name_list)):
        print(horse_name_list[i])
        # 馬の過去の戦績をスクレイピング
        horse_race_data_list = horse_race_data_list + scrapHorseRaceData(horse_name_list[i])
    print(len(horse_race_data_list))
    horse_race_data_list_shr = []
    for i in range(len(horse_race_data_list)):
        place = horse_race_data_list[i][0]
        if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
            weather = horse_race_data_list[i][1]
            burden_weight = horse_race_data_list[i][2]
            race_course_gnd = horse_race_data_list[i][3]
            distance = horse_race_data_list[i][4]
            ground_status = horse_race_data_list[i][5]
            goal_time = horse_race_data_list[i][6]
            horse_race_data_list_shr.append([place, distance, race_course_gnd, weather, ground_status])
    horse_race_data_list_shr = get_unique_list(horse_race_data_list_shr)
    print(len(horse_race_data_list_shr))
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))
    

    # 出走馬の過去の戦績（重複なし）に対する　ベースタイム　と　馬場指数
    base_time_and_gnd_figure_list = []
    for i in range(len(horse_race_data_list_shr)):
        base_time, gf = calcBaseTimeFigureAndGndFigure(race_data_list, horse_data_list, horse_race_data_list_shr[i][0], horse_race_data_list_shr[i][1], horse_race_data_list_shr[i][2], horse_race_data_list_shr[i][3], horse_race_data_list_shr[i][4])
        print("base_time = {}".format(base_time))
        print("gf = {}".format(gf))
        base_time_and_gnd_figure_list.append([base_time, gf])
    rap_time = time.time() - start
    print("rap_time:{0}[sec]".format(rap_time))


    # 各出走馬のスピード指数の算出
    for horse_name in horse_name_list:
        try:
            print(horse_name)
            print("")
            # 馬の過去の戦績をスクレイピング
            horse_race_data_list = scrapHorseRaceData(horse_name)
            speed_figure_list = []
            for i in range(len(horse_race_data_list)):
                place = horse_race_data_list[i][0]
                if place in ["中山","阪神","東京","中京","札幌","函館","福島","新潟","京都","小倉"]: # 日本の中央競馬限定
                    weather = horse_race_data_list[i][1]
                    burden_weight = horse_race_data_list[i][2]
                    race_course_gnd = horse_race_data_list[i][3]
                    distance = horse_race_data_list[i][4]
                    ground_status = horse_race_data_list[i][5]
                    goal_time = horse_race_data_list[i][6]
                    try:
                        idx = horse_race_data_list_shr.index([place, distance, race_course_gnd, weather, ground_status])
                        tmp = base_time_and_gnd_figure_list[idx]
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
                        if base_time == None:

                            continue

                        df = calcDistanceFigure(base_time)
                        print("df = {}".format(df))
                        # 馬場指数算出
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

            result.append([horse_name, ave_speed_figure])

        except Exception as e:
            print('=== エラー内容 ===')
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('message:' + e.message)
            print('e自身:' + str(e))
            print(result)

    print(sorted(result, reverse=True, key=lambda x: x[1]))
    elapsed_time = time.time() - start
    print("elapsed_time:{0}[sec]".format(elapsed_time))
    

