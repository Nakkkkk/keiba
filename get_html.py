import os
import requests
import time
import random

# 月ごとに検索
s_year = 1975
s_month = 1
e_year = 2021
e_month = 4

dummy = ["70.0.3538.16.0", "70.0.3538.67.0", "70.0.3538.97.0", "71.0.3578.30.0", "71.0.3578.33.0", "71.0.3578.80.0", "71.0.3578.137.0", "72.0.3626.7.0", "72.0.3626.69.0", "73.0.3683.20.0", "73.0.3683.68.0", "74.0.3729.6.0", "75.0.3770.8.0", "75.0.3770.90.0", "75.0.3770.140.0", "76.0.3809.12.0", "76.0.3809.25.0", "76.0.3809.68.0", "76.0.3809.126.0", "77.0.3865.10.0", "77.0.3865.40.0", "78.0.3904.11.0", "78.0.3904.70.0", "78.0.3904.105.0", "79.0.3945.16.0", "79.0.3945.36.0", "80.0.3987.16.0", "80.0.3987.106.0", "81.0.4044.20.0", "81.0.4044.69.0", "81.0.4044.138.0", "83.0.4103.14.0", "83.0.4103.39.0", "84.0.4147.30.0", "85.0.4183.38.0", "85.0.4183.83.0", "85.0.4183.87.0", "86.0.4240.22.0", "87.0.4280.20.0", "87.0.4280.87.0", "87.0.4280.88.0", "88.0.4324.27.0", "88.0.4324.27.1", "88.0.4324.96.0", "89.0.4389.23.0", "90.0.4430.24.0", "91.0.4472.19.0"]

Apple = random.randrange(50)
Chrome = random.randrange(99)
Safari = random.randrange(50)
headers_dic = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537." + str(Apple) + " (KHTML, like Gecko) Chrome/78.0.3904." + str(Chrome) + " Safari/537." + str(Safari)}

save_dir = "html"+"/"+str(s_year)+"_"+str(s_month)+"-"+str(e_year)+"_"+str(e_month)
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
        
with open(str(s_year)+"_"+str(s_month)+"-"+str(e_year)+"_"+str(e_month)+"_199305010112"+".txt", "r") as f:
    urls = f.read().splitlines()
    cnt = 0
    for url in urls:
        print(url)
        cnt += 1
        if cnt == 100:
            print("sleep...")
            time.sleep(5.1)
            cnt = 0
        list = url.split("/")
        race_id = list[-2]
        save_file_path = save_dir+"/"+race_id+'.html'
        response = requests.get(url, headers=headers_dic)
        response.encoding = response.apparent_encoding
        html = response.text
        time.sleep(0.1)
        with open(save_file_path, 'w') as file:
            file.write(html)