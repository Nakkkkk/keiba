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
import datetime



# 馬のSQLデータベースのカーソルを作成
def makeHorseSqlDatabaseCursor(sql_dir):
    dbname = '/Horse.db'
    horse_data_conn = sqlite3.connect(sql_dir + dbname)
    horse_data_conn.row_factory = sqlite3.Row
    horse_data_cur = horse_data_conn.cursor()

    return horse_data_cur, horse_data_conn



# レースのSQLデータベースのカーソルを作成
def makeRaceSqlDatabaseCursor(sql_dir):
    dbname = '/Race.db'
    race_data_conn = sqlite3.connect(sql_dir + dbname)
    race_data_conn.row_factory = sqlite3.Row
    race_data_cur = race_data_conn.cursor()

    return race_data_cur, race_data_conn




def makeDatabeseRace(sql_dir):
    # DBを作成する
    # すでに存在していれば、それにアスセスする。
    dbname = '/Race.db'
    conn = sqlite3.connect(sql_dir + dbname)
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

    # DBにアスセス
    conn = sqlite3.connect(sql_dir + dbname)
    # sqliteを操作するカーソルオブジェクトを作成
    cur = conn.cursor()

    # horseというtableを作成
    try:
        cur.execute('CREATE TABLE race( \
        id INTEGER PRIMARY KEY AUTOINCREMENT, \
        race_id INTEGER, \
        race_round STRING, \
        race_title STRING, \
        race_course_m INTEGER, \
        race_course_lr STRING, \
        race_course_gnd STRING, \
        weather STRING, \
        ground_status STRING, \
        time STRING, \
        date STRING, \
        where_racecourse STRING, \
        total_horse_number INTEGER, \
        frame_number_first INTEGER, \
        horse_number_first INTEGER, \
        frame_number_second INTEGER, \
        horse_number_second INTEGER, \
        frame_number_third INTEGER, \
        horse_number_third INTEGER, \
        tansyo INTEGER, \
        hukusyo_first INTEGER, \
        hukusyo_second INTEGER, \
        hukusyo_third INTEGER, \
        wakuren INTEGER, \
        umaren INTEGER, \
        wide_1_2 INTEGER, \
        wide_1_3 INTEGER, \
        wide_2_3 INTEGER, \
        umatan INTEGER, \
        renhuku3 INTEGER, \
        rentan3 INTEGER \
        )')
    except(sqlite3.OperationalError):
        pass
    # データベースへコミット。これで変更が反映される。
    conn.commit()
    conn.close()



def updateDatabeseRace(
    sql_dir,
    race_id,
    race_round,
    race_title,
    race_course_m,
    race_course_lr,
    race_course_gnd,
    weather,
    ground_status,
    time,
    date,
    where_racecourse,
    total_horse_number,
    frame_number_first,
    horse_number_first,
    frame_number_second,
    horse_number_second,
    frame_number_third,
    horse_number_third,
    tansyo,
    hukusyo_first,
    hukusyo_second,
    hukusyo_third,
    wakuren,
    umaren,
    wide_1_2,
    wide_1_3,
    wide_2_3,
    umatan,
    renhuku3,
    rentan3
):

    dbname = '/Race.db'
    conn = sqlite3.connect(sql_dir + dbname)
    cur = conn.cursor()

    # データを入力 OR 更新
    cur.execute('SELECT * FROM race WHERE race_id = {}'.format(race_id))
    row_fetched = cur.fetchall()
    if len(row_fetched) == 0:
        print("INSERT")
        cur.execute('INSERT INTO race( \
        race_id, \
        race_round, \
        race_title, \
        race_course_m, \
        race_course_lr, \
        race_course_gnd, \
        weather, \
        ground_status, \
        time, \
        date, \
        where_racecourse, \
        total_horse_number, \
        frame_number_first, \
        horse_number_first, \
        frame_number_second, \
        horse_number_second, \
        frame_number_third, \
        horse_number_third, \
        tansyo, \
        hukusyo_first, \
        hukusyo_second, \
        hukusyo_third, \
        wakuren, \
        umaren, \
        wide_1_2, \
        wide_1_3, \
        wide_2_3, \
        umatan, \
        renhuku3, \
        rentan3) \
        values({},"{}","{}",{},"{}","{}","{}","{}","{}","{}","{}",{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})'.format(
            race_id,
            race_round,
            race_title,
            race_course_m,
            race_course_lr,
            race_course_gnd,
            weather,
            ground_status,
            time,
            date,
            where_racecourse,
            total_horse_number,
            frame_number_first,
            horse_number_first,
            frame_number_second,
            horse_number_second,
            frame_number_third,
            horse_number_third,
            tansyo,
            hukusyo_first,
            hukusyo_second,
            hukusyo_third,
            wakuren,
            umaren,
            wide_1_2,
            wide_1_3,
            wide_2_3,
            umatan,
            renhuku3,
            rentan3
            ))

    conn.commit()

    cur.close()
    conn.close()



def makeDatabeseHorse(sql_dir):
    # DBを作成する
    # すでに存在していれば、それにアスセスする。
    dbname = '/Horse.db'
    conn = sqlite3.connect(sql_dir + dbname)
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

    # DBにアスセス
    conn = sqlite3.connect(sql_dir + dbname)
    # sqliteを操作するカーソルオブジェクトを作成
    cur = conn.cursor()

    # horseというtableを作成
    try:
        cur.execute('CREATE TABLE horse( \
        id INTEGER PRIMARY KEY AUTOINCREMENT, \
        race_id INTEGER, \
        rank INTEGER, \
        frame_number INTEGER, \
        horse_number INTEGER, \
        horse_id INTEGER, \
        age INTEGER, \
        sex STRING, \
        burden_weight REAL, \
        rider_id INTEGER, \
        goal_time REAL, \
        goal_time_dif STRING, \
        half_way_rank STRING, \
        last_time REAL, \
        odds REAL, \
        popular INTEGER, \
        horse_weight REAL, \
        weight_change REAL, \
        tamer_id INTEGER, \
        owner_id INTEGER \
        )')
    except(sqlite3.OperationalError):
        pass
    # データベースへコミット。これで変更が反映される。
    conn.commit()
    conn.close()



def updateDatabeseHorse(
    sql_dir,
    race_id, 
    rank, 
    frame_number, 
    horse_number, 
    horse_id, 
    age, 
    sex, 
    burden_weight, 
    rider_id, 
    goal_time, 
    goal_time_dif, 
    half_way_rank, 
    last_time, 
    odds, 
    popular, 
    horse_weight, 
    weight_change, 
    tamer_id, 
    owner_id
):

    dbname = '/Horse.db'
    conn = sqlite3.connect(sql_dir + dbname)
    cur = conn.cursor()

    # データを入力 OR 更新
    cur.execute('SELECT * FROM horse WHERE race_id = {} AND horse_id = {}'.format(race_id, horse_id))
    row_fetched = cur.fetchall()
    if len(row_fetched) == 0:
        print("INSERT")
        cur.execute('INSERT INTO horse( \
        race_id, \
        rank, \
        frame_number, \
        horse_number, \
        horse_id, \
        age, \
        sex, \
        burden_weight, \
        rider_id, \
        goal_time, \
        goal_time_dif, \
        half_way_rank, \
        last_time, \
        odds, \
        popular, \
        horse_weight, \
        weight_change, \
        tamer_id, \
        owner_id) \
        values({},{},{},{},{},{},"{}",{},{},{},"{}","{}",{},{},{},{},{},{},{})'.format(
            race_id, 
            rank, 
            frame_number, 
            horse_number, 
            horse_id, 
            age, 
            sex, 
            burden_weight, 
            rider_id, 
            goal_time, 
            goal_time_dif, 
            half_way_rank, 
            last_time, 
            odds, 
            popular, 
            horse_weight, 
            weight_change, 
            tamer_id, 
            owner_id
            ))

    conn.commit()

    cur.close()
    conn.close()




def makeHorseAndRaceDatabaseUpdateList(sql_dir):
    # 今日の日付
    dt_now = datetime.datetime.now()
    dt_now_strf = dt_now.strftime('%Y-%m-%d-%H-%M-%S')


    # sqlデータの読み込み
    horse_data_cur, horse_data_conn = makeHorseSqlDatabaseCursor(sql_dir)
    race_data_cur, race_data_conn = makeRaceSqlDatabaseCursor(sql_dir)

    # スクレイピングのスタートアップ
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,10)

    # スクレイピング開始
    URL = "https://db.netkeiba.com/?pid=race_search_detail"
    driver.get(URL)
    print(driver.current_url)
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    # 中央競馬場をチェック
    for i in range(1,11):
        terms = driver.find_element_by_id("check_Jyo_"+ str(i).zfill(2))
        terms.click()
            
    # 表示件数を選択(20,50,100の中から最大の100へ)
    list_element = driver.find_element_by_name('list')
    list_select = Select(list_element)
    list_select.select_by_value("100")

    # フォームを送信
    frm = driver.find_element_by_css_selector("#db_search_detail_form > form")
    frm.submit()
    time.sleep(3)
    wait.until(EC.presence_of_all_elements_located)

    # URLをテキストファイルで一旦保存
    path_db_update_list = "db_update_url_list_" + dt_now_strf + ".txt"
    with open(path_db_update_list, mode='w') as f:
        flg_exit_update = False
        while True:
            time.sleep(5)
            wait.until(EC.presence_of_all_elements_located)
            all_rows = driver.find_element_by_class_name('race_table_01').find_elements_by_tag_name("tr")
            for row in range(1, len(all_rows)):
                race_href=all_rows[row].find_elements_by_tag_name("td")[4].find_element_by_tag_name("a").get_attribute("href")
                race_id = race_href.split("/")[-2]
                race_data_cur.execute('SELECT * FROM race WHERE race_id = {}'.format(race_id))
                race_data_fetched = race_data_cur.fetchall()
                if len(race_data_fetched) == 0:
                    print(race_href)
                    f.write(race_href+"\n")
                else:
                    print("====== exit DB update ======")
                    print(race_href)
                    flg_exit_update = True
                    break

            if flg_exit_update == True:
                break

            try:
                target = driver.find_elements_by_link_text("次")[0]
                driver.execute_script("arguments[0].click();", target) #javascriptでクリック処理
            except IndexError:
                break

    return path_db_update_list



def getInfoFromHorseAndRaceDatabaseUpdateList(txtname):
    # sqlデータの読み込み
    sql_dir = "../data/all_sq"
    horse_data_cur, horse_data_conn = makeHorseSqlDatabaseCursor(sql_dir)
    race_data_cur, race_data_conn = makeRaceSqlDatabaseCursor(sql_dir)

    # スクレイピングのスタートアップ
    options = Options()
    options.add_argument('--headless')    # ヘッドレスモードに
    driver = webdriver.Chrome(chrome_options=options) 
    wait = WebDriverWait(driver,10)


    # テキストファイルでデータベースを更新
    with open(txtname, mode='r') as f:
        urls = f.read().splitlines()
        race_info_list = []
        horse_infos_list = []
        for url in urls:
            # スクレイピング開始
            driver.get(url)
            print(driver.current_url)
            time.sleep(1)
            wait.until(EC.presence_of_all_elements_located)


            # race基本情報
            race_info = []
            race_info.append(int(url.split("/")[-2])) # race_id
            dl_racedata = driver.find_element_by_class_name('racedata')
            
            race_info.append(dl_racedata.find_elements_by_tag_name("dt")[0].text) # race_round
            t_ = dl_racedata.find_elements_by_tag_name("h1")[0].text
            print()
            print(t_)
            title = ""
            if "未勝利" in t_ or "新馬" in t_:
                title = "F"
            elif "1勝" in t_: # = "500万下" or "400万下"
                title = "W1"
            elif "2勝" in t_: # = "1000万下" or "900万下"
                title = "W2"
            elif "3勝" in t_: # = "1600万下" or "1500万下" or "1400万下"
                title = "W3"
            elif "オープン" in t_ or "OP" in t_:
                title = "OP"
            elif "L" in t_:
                title = "L"
            elif "G1" in t_:
                title = "G1"
            elif "G2" in t_:
                title = "G2"
            elif "G3" in t_:
                title = "G3"
            else:
                title = "WX"
            race_info.append(title) # race_title
            race_details1 = dl_racedata.find_elements_by_tag_name("p")[0].text.split(" / ")

            #race_info.append(race_details1[0]) # race_course
            race_course_m = int(race_details1[0][-5:-1])
            race_course_gnd = ""
            if "芝" in race_details1[0][0]:
                race_course_gnd = "T"
            elif "ダ" in race_details1[0][0]:
                race_course_gnd = "D"
            if "障" in race_details1[0][0]:
                race_course_gnd = "O"
            race_course_lr = ""
            if "左" in race_details1[0][1]:
                race_course_lr = "L"
            elif "右" in race_details1[0][1]:
                race_course_lr = "R"
            race_info.append(race_course_m) # race_course meter
            race_info.append(race_course_lr) # race_course lr
            race_info.append(race_course_gnd) # race_course ground type
            weather = ""
            if "晴" in race_details1[1]:
                weather = "S"
            elif "曇" in race_details1[1]:
                weather = "C"
            elif "小雨" in race_details1[1]:
                weather = "R0"
            elif "雨" in race_details1[1]:
                weather = "R1"
            race_info.append(weather) # weather
            ground_status = ""
            if "不良" in race_details1[2]:
                ground_status = "B"
            elif "稍" in race_details1[2]:
                ground_status = "H0"
            elif "重" in race_details1[2]:
                ground_status = "H1"
            elif "良" in race_details1[2]:
                ground_status = "G"
            race_info.append(ground_status) # ground_status
            race_info.append(race_details1[3]) # time
            race_details2 = driver.find_element_by_class_name('smalltxt').text.strip("\n").split(" ")
            race_info.append(race_details2[0]) # date
            race_info.append(race_details2[1]) # where_racecourse

            # もし、タイトルだけでランクが判別不能(WX時)である場合、ランクを書き換える
            if race_info[2] == "WX":
                t_ = race_details2[2] # race title
                title = ""
                if "500万下" in t_ or "400万下" in t_:
                    title = "W1"
                elif "1000万下" in t_ or "900万下" in t_:
                    title = "W2"
                elif "1600万下" in t_ or "1500万下" in t_ or "1400万下" in t_:
                    title = "W3"
                else:
                    title = "WX"
                race_info[2] = title

            result_rows = driver.find_element_by_class_name('race_table_01').find_elements_by_tag_name("tr")
            # 上位3着の情報
            race_info.append(len(result_rows)-1) # total_horse_number
            for i in range(1,4):
                row = result_rows[i].find_elements_by_tag_name("td")
                race_info.append(int(row[1].text)) # frame_number_first or second or third
                race_info.append(int(row[2].text)) # horse_number_first or second or third


            # 払い戻し(単勝・複勝・三連複・3連単)
            pay_back_tables = driver.find_elements_by_class_name('pay_table_01')

            pay_back1 = pay_back_tables[0].find_elements_by_tag_name("tr") # 払い戻し1(単勝・複勝)
            tansyo = int(pay_back1[0].find_elements_by_class_name('txt_r')[0].text.split("\n")[0].replace(",",""))
            race_info.append(tansyo) #tansyo
            hukuren = pay_back1[1].find_elements_by_class_name('txt_r')[0].text.replace(",","").split("\n")
            for i in range(3):
                try:
                    race_info.append(int(hukuren[i])) # hukuren_first or second or third
                except IndexError:
                    race_info.append(0)

            # 枠連
            try:
                race_info.append(int(pay_back1[2].find_elements_by_class_name('txt_r')[0].text.split("\n")[0].replace(",","")))
            except IndexError:
                race_info.append(0)

            # 馬連
            try:
                race_info.append(int(pay_back1[3].find_elements_by_class_name('txt_r')[0].text.split("\n")[0].replace(",","")))
            except IndexError:
                race_info.append(0)

            pay_back2 = pay_back_tables[1].find_elements_by_tag_name("tr") # 払い戻し2(三連複・3連単)
            if len(pay_back2) == 0:
                for i in range(6):
                    race_info.append(0)
            else:
                # wide 1&2
                wide = pay_back2[0].find_elements_by_class_name('txt_r')[0].text.replace(",","").split("\n")
                for i in range(3):
                    try:
                        race_info.append(int(wide[i])) # hukuren_first or second or third
                    except IndexError:
                        race_info.append(0)

                # umatan
                try:
                    race_info.append(int(pay_back2[1].find_elements_by_class_name('txt_r')[0].text.split("\n")[0].replace(",",""))) #umatan
                except IndexError:
                    race_info.append(0)
                
                try:
                    race_info.append(int(pay_back2[2].find_elements_by_class_name('txt_r')[0].text.split("\n")[0].replace(",",""))) #renhuku3
                except IndexError:
                    race_info.append(0)
                
                try:
                    race_info.append(int(pay_back2[3].find_elements_by_class_name('txt_r')[0].text.split("\n")[0].replace(",",""))) #rentan3
                except IndexError:
                    race_info.append(0)

            print(race_info)

            race_info_list.append(race_info)



            # horse基本情報
            horse_infos = []
            for rank in range(1, len(result_rows)):
                horse_info = []
                horse_info.append(int(url.split("/")[-2])) # race_id
                result_row = result_rows[rank].find_elements_by_tag_name("td")
                #print(result_row)
                # rank
                try:
                    horse_info.append(int(result_row[0].text))
                except:
                    print(result_row[0].text)
                    horse_info.append("NULL")
                # frame_number
                horse_info.append(int(result_row[1].text))
                # horse_number
                horse_info.append(int(result_row[2].text))
                # horse_id
                horse_info.append(int(result_row[3].find_element_by_tag_name("a").get_attribute("href").split("/")[-2]))
                # sex_and_age
                sex = ""
                tmp = ""
                if "牡" in result_row[4].text:
                    sex = "M"
                    tmp = "牡"
                elif "セ" in result_row[4].text:
                    sex = "S"
                    tmp = "セ"
                elif "牝" in result_row[4].text:
                    sex = "F"
                    tmp = "牝"
                age = int(result_row[4].text.split(tmp)[-1])
                horse_info.append(age)
                horse_info.append(sex)
                # burden_weight
                horse_info.append(float(result_row[5].text))
                # rider_id
                horse_info.append(int(result_row[6].find_element_by_tag_name("a").get_attribute("href").split("/")[-2]))
                # goal_time
                goal_time = "NULL"
                if type(result_row[7].text) == float:
                    goal_time = result_row[7].text
                elif result_row[7].text == "":
                    goal_time = "NULL"
                else:
                    gt = result_row[7].text.split(":")
                    if len(gt) == 1:
                        time_ = float(gt[0])
                    elif len(gt) == 2:
                        time_ = float(gt[1]) + float(gt[0])*60
                    else:
                        time_ = "NULL"
                    goal_time = time_
                horse_info.append(goal_time)
                # goal_time_dif
                horse_info.append(result_row[8].text)
                # half_way_rank
                horse_info.append(result_row[10].text)
                # last_time(上り)
                try:
                    horse_info.append(float(result_row[11].text))
                except:
                    print(result_row[11].text)
                    horse_info.append("NULL")
                # odds
                try:
                    horse_info.append(float(result_row[12].text))
                except:
                    print(result_row[12].text)
                    horse_info.append("NULL")
                # popular
                try:
                    horse_info.append(int(result_row[13].text))
                except:
                    print(result_row[13].text)
                    horse_info.append("NULL")
                # horse_weight
                weight = "NULL"
                change = "NULL"
                if type(result_row[14].text) == float:
                    weight = "NULL"
                    change = "NULL"
                    horse_info.append(weight)
                    horse_info.append(change)
                elif result_row[14].text == "計不" or result_row[14].text == "":
                    weight = "NULL"
                    change = "NULL"
                    horse_info.append(weight)
                    horse_info.append(change)
                else:
                    hw = result_row[14].text.split("(")
                    if len(hw) == 1:
                        weight = float(hw[0])
                        change = "NULL"
                    elif len(hw) > 1:
                        weight = float(hw[0])
                        wc = hw[1][0:-1]
                        change = 0
                        if "+" in wc:
                            change = float(wc[1:])
                        elif "-" in wc:
                            change = float(wc[1:]) * -1
                        else:
                            change = float(wc)
                    horse_info.append(float(weight))
                    horse_info.append(float(change))
                # 16:コメント、17:備考
                # tamer_id
                try:
                    horse_info.append(int(result_row[18].find_element_by_tag_name("a").get_attribute("href").split("/")[-2]))
                except:
                    horse_info.append(-1)
                # owner_id
                try:
                    horse_info.append(int(result_row[19].find_element_by_tag_name("a").get_attribute("href").split("/")[-2]))
                except:
                    horse_info.append(-1)

                horse_infos.append(horse_info)
            
            horse_infos_list.append(horse_infos)

    horse_data_cur.close()
    horse_data_conn.close()
    race_data_cur.close()
    race_data_conn.close()

    return race_info_list, horse_infos_list




def readDatabese(dbname, tablename):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    cur.execute('SELECT * FROM '+tablename)
    row_fetched = cur.fetchall()

    cur.close()
    conn.close()

    return row_fetched




if __name__ == "__main__":
    sql_dir = "../data/all_sq"

    # Horse, Raceデータベースの作成
    #makeDatabeseHorse(sql_dir)
    #makeDatabeseRace(sql_dir)

    # Horse, Raceデータベースの更新
    path_db_update_list = makeHorseAndRaceDatabaseUpdateList(sql_dir)
    race_info_list, horse_infos_list = getInfoFromHorseAndRaceDatabaseUpdateList(path_db_update_list)
    print("### update Race.db ###")
    for ri in race_info_list:
        updateDatabeseRace(sql_dir, ri[0], ri[1], ri[2], ri[3], ri[4], ri[5], ri[6], ri[7], ri[8], ri[9], ri[10], ri[11], ri[12], ri[13], ri[14], ri[15], ri[16], ri[17], ri[18], ri[19], ri[20], ri[21], ri[22], ri[23], ri[24], ri[25], ri[26], ri[27], ri[28], ri[29])
    print("### update Horse.db ###")
    for horse_infos in horse_infos_list:
        for hi in horse_infos:
            updateDatabeseHorse(sql_dir, hi[0], hi[1], hi[2], hi[3], hi[4], hi[5], hi[6], hi[7], hi[8], hi[9], hi[10], hi[11], hi[12], hi[13], hi[14], hi[15], hi[16], hi[17], hi[18])

    # Bloodデータベースの更新
    #blood_info_list = getInfoFromHBloodDatabaseUpdateList(path_db_update_list)

    
    """
    # データベースチェック
    row_fetched = readDatabese("../data/all_sq/Horse.db", "horse")
    print(row_fetched[-16])
    print(row_fetched[-17])
    """