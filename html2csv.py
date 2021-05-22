import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import os
from natsort import natsorted

def get_rade_and_horse_data_by_html(race_id, html):
    race_list = [race_id]
    horse_list_list = []
    soup = BeautifulSoup(html, 'html.parser')

    # race基本情報
    data_intro = soup.find("div", class_="data_intro")
    race_list.append(data_intro.find("dt").get_text().strip("\n")) # race_round
    race_list.append(data_intro.find("h1").get_text().strip("\n")) # race_title
    race_details1 = data_intro.find("p").get_text().strip("\n").split("\xa0/\xa0")
    race_list.append(race_details1[0]) # race_course
    race_list.append(race_details1[1]) # weather
    race_list.append(race_details1[2]) # ground_status
    race_list.append(race_details1[3]) # time
    race_details2 = data_intro.find("p", class_="smalltxt").get_text().strip("\n").split(" ")
    race_list.append(race_details2[0]) # date
    race_list.append(race_details2[1]) # where_racecourse


    result_rows = soup.find("table", class_="race_table_01 nk_tb_common").findAll('tr') # レース結果
    # 上位3着の情報
    race_list.append(len(result_rows)-1) # total_horse_number
    for i in range(1,4):
        row = result_rows[i].findAll('td')
        race_list.append(row[1].get_text()) # frame_number_first or second or third
        race_list.append(row[2].get_text()) # horse_number_first or second or third


    # 払い戻し(単勝・複勝・三連複・3連単)
    pay_back_tables = soup.findAll("table", class_="pay_table_01")

    pay_back1 = pay_back_tables[0].findAll('tr') # 払い戻し1(単勝・複勝)
    #print(pay_back1)
    race_list.append(pay_back1[0].find("td", class_="txt_r").get_text()) #tansyo
    hukuren = pay_back1[1].find("td", class_="txt_r")
    tmp = []
    for string in hukuren.strings:
        tmp.append(string)
    for i in range(3):
        try:
            race_list.append(tmp[i]) # hukuren_first or second or third
        except IndexError:
            race_list.append("0")

    # 枠連
    try:
        race_list.append(pay_back1[2].find("td", class_="txt_r").get_text())
    except IndexError:
        race_list.append("0")

    # 馬連
    try:
        race_list.append(pay_back1[3].find("td", class_="txt_r").get_text())
    except IndexError:
        race_list.append("0")



    pay_back2 = pay_back_tables[1].findAll('tr') # 払い戻し2(三連複・3連単)
    #print(pay_back2)
    if len(pay_back2) == 0:
        for i in range(6):
            race_list.append("0")
    else:
        # wide 1&2
        wide = pay_back2[0].find("td", class_="txt_r")
        
        tmp = []
        for string in wide.strings:
            tmp.append(string)
        for i in range(3):
            try:
                race_list.append(tmp[i]) # hukuren_first or second or third
            except IndexError:
                race_list.append("0")

        # umatan
        try:
            race_list.append(pay_back2[1].find("td", class_="txt_r").get_text()) #umatan
        except IndexError:
            race_list.append("0")
        
        try:
            race_list.append(pay_back2[2].find("td", class_="txt_r").get_text()) #renhuku3
        except IndexError:
            race_list.append("0")
        
        try:
            race_list.append(pay_back2[3].find("td", class_="txt_r").get_text()) #rentan3
        except IndexError:
            race_list.append("0")

    # horse data
    for rank in range(1, len(result_rows)):
        horse_list = [race_id]
        result_row = result_rows[rank].findAll("td")
        #print(result_row)
        # rank
        horse_list.append(result_row[0].get_text())
        # frame_number
        horse_list.append(result_row[1].get_text())
        # horse_number
        horse_list.append(result_row[2].get_text())
        # horse_id
        horse_list.append(result_row[3].find('a').get('href').split("/")[-2])
        # sex_and_age
        horse_list.append(result_row[4].get_text())
        # burden_weight
        horse_list.append(result_row[5].get_text())
        # rider_id
        horse_list.append(result_row[6].find('a').get('href').split("/")[-2])
        # goal_time
        horse_list.append(result_row[7].get_text())
        # goal_time_dif
        horse_list.append(result_row[8].get_text())
        # time_value(premium)
        horse_list.append(result_row[9].get_text())
        # half_way_rank
        horse_list.append(result_row[10].get_text())
        # last_time(上り)
        horse_list.append(result_row[11].get_text())
        # odds
        horse_list.append(result_row[12].get_text())
        # popular
        horse_list.append(result_row[13].get_text())
        # horse_weight
        horse_list.append(result_row[14].get_text())
        # tame_time(premium)
        horse_list.append(result_row[15].get_text())
        # 16:コメント、17:備考
        # tamer_id
        try:
            horse_list.append(result_row[18].find('a').get('href').split("/")[-2])
        except:
            horse_list.append(-1)
        # owner_id
        try:
            horse_list.append(result_row[19].find('a').get('href').split("/")[-2])
        except:
            horse_list.append(-1)

        horse_list_list.append(horse_list)

    return race_list, horse_list_list

race_data_columns=[
    'race_id',
    'race_round',
    'race_title',
    'race_course',
    'weather',
    'ground_status',
    'time',
    'date',
    'where_racecourse',
    'total_horse_number',
    'frame_number_first',
    'horse_number_first',
    'frame_number_second',
    'horse_number_second',
    'frame_number_third',
    'horse_number_third',
    'tansyo',
    'hukusyo_first',
    'hukusyo_second',
    'hukusyo_third',
    'wakuren',
    'umaren',
    'wide_1_2',
    'wide_1_3',
    'wide_2_3',
    'umatan',
    'renhuku3',
    'rentan3'
    ]

horse_data_columns=[
    'race_id',
    'rank',
    'frame_number',
    'horse_number',
    'horse_id',
    'sex_and_age',
    'burden_weight',
    'rider_id',
    'goal_time',
    'goal_time_dif',
    'time_value',
    'half_way_rank',
    'last_time',
    'odds',
    'popular',
    'horse_weight',
    'tame_time',
    'tamer_id',
    'owner_id'
]


# 月ごとに検索
s_year = 1975
s_month = 1
e_year = 2021
e_month = 4


CSV_DIR = "csv"
if not os.path.isdir(CSV_DIR):
    os.makedirs(CSV_DIR)
if not os.path.isdir(CSV_DIR+"/org"):
    os.makedirs(CSV_DIR+"/org")
save_race_csv = CSV_DIR+"/org"+"/race-"+str(s_year)+"_"+str(s_month)+"-"+str(e_year)+"_"+str(e_month)
horse_race_csv = CSV_DIR+"/org"+"/horse-"+str(s_year)+"_"+str(s_month)+"-"+str(e_year)+"_"+str(e_month)

race_df = pd.DataFrame(columns=race_data_columns )
horse_df = pd.DataFrame(columns=horse_data_columns )

#cnt = 97462
cnt = 0

html_dir = "all_html/20210501html/html"+"/"+str(s_year)+"_"+str(s_month)+"-"+str(e_year)+"_"+str(e_month)
if os.path.isdir(html_dir):
    file_list = natsorted(os.listdir(html_dir),reverse=True)
    for file_name in file_list:
        with open(html_dir+"/"+file_name, "r") as f:
            #print("")
            #print(file_name)
            #print("")
            html = f.read()
            list = file_name.split(".")
            race_id = list[-2]
            race_list, horse_list_list = get_rade_and_horse_data_by_html(race_id, html) # 長くなるので省略
            for horse_list in horse_list_list:
                horse_se = pd.Series( horse_list, index=horse_df.columns)
                horse_df = horse_df.append(horse_se, ignore_index=True)
            race_se = pd.Series(race_list, index=race_df.columns )
            race_df = race_df.append(race_se, ignore_index=True )

            cnt += 1
            print(cnt)
            if cnt % 1000 == 0:
                # 1000件ごとにCSVを作る（メモリ対策）
                race_df.to_csv(save_race_csv + "_" + str(cnt) + ".csv", header=True, index=False)
                horse_df.to_csv(horse_race_csv + "_" + str(cnt) + ".csv", header=True, index=False)
                # データフレーム初期化
                race_df = pd.DataFrame(columns=race_data_columns )
                horse_df = pd.DataFrame(columns=horse_data_columns )
    else:
        print(cnt)
        # 残りのデータフレームのCSVを作る（メモリ対策）
        race_df.to_csv(save_race_csv + "_" + str(cnt) + ".csv", header=True, index=False)
        horse_df.to_csv(horse_race_csv + "_" + str(cnt) + ".csv", header=True, index=False)