import time

from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')    # ヘッドレスモードに
driver = webdriver.Chrome(chrome_options=options) 
wait = WebDriverWait(driver,10)

URL = "https://db.netkeiba.com/?pid=race_search_detail"
driver.get(URL)
print(driver.current_url)
time.sleep(1)
wait.until(EC.presence_of_all_elements_located)

# 月ごとに検索
s_year = 1975
s_month = 1
e_year = 1998
e_month = 1

# 期間を選択
start_year_element = driver.find_element_by_name('start_year')
start_year_select = Select(start_year_element)
start_year_select.select_by_value(str(s_year))
start_mon_element = driver.find_element_by_name('start_mon')
start_mon_select = Select(start_mon_element)
start_mon_select.select_by_value(str(s_month))
end_year_element = driver.find_element_by_name('end_year')
end_year_select = Select(end_year_element)
end_year_select.select_by_value(str(e_year))
end_mon_element = driver.find_element_by_name('end_mon')
end_mon_select = Select(end_mon_element)
end_mon_select.select_by_value(str(e_month))

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




# URLの保存
with open(str(s_year)+"_"+str(s_month)+"-"+str(e_year)+"_"+str(e_month)+".txt", mode='w') as f:
    while True:
        time.sleep(5)
        wait.until(EC.presence_of_all_elements_located)
        all_rows = driver.find_element_by_class_name('race_table_01').find_elements_by_tag_name("tr")
        for row in range(1, len(all_rows)):
            race_href=all_rows[row].find_elements_by_tag_name("td")[4].find_element_by_tag_name("a").get_attribute("href")
            print(race_href)
            f.write(race_href+"\n")
        try:
            target = driver.find_elements_by_link_text("次")[0]
            #print(driver.find_elements_by_link_text("次"))
            driver.execute_script("arguments[0].click();", target) #javascriptでクリック処理
        except IndexError:
            break




