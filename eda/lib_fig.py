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
#from lib_calc import *

from common_import import *

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



