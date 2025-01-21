import csv
import json
import sys
import requests
import urllib.request
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')  
sys.stdin.reconfigure(encoding='utf-8')   
sys.stderr.reconfigure(encoding='utf-8')  

# ============================================ task1 ======================================================
url_1 = "https://padax.github.io/taipei-day-trip-resources/taipei-attractions-assignment-1"
url_2 = "https://padax.github.io/taipei-day-trip-resources/taipei-attractions-assignment-2"

# 從 URL 讀取資料的函數
def read_file_from_url(url):
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:  
                content = response.read().decode('utf-8')
                return json.loads(content)  
            else:
                print(f"Failed to read file from URL {url}: HTTP {response.status}")
                return {}
    except Exception as e:
        print(f"Failed to read file from URL {url}: {e}")
        return {}

# 解析第一個檔案資料
def parse_data_file_1(data):
    spot_list = []
    for item in data.get("data", {}).get("results", []):
        title = item.get("stitle", "")  # 景點名稱
        SERIAL_NO = item.get("SERIAL_NO","") # 景點編號
        longitude = item.get("longitude", "")  # 經度
        latitude = item.get("latitude", "")  # 緯度

        # 提取圖片 URL，只保留第一張
        image_url = item.get("filelist", "").split("https://")[1:]
        image_url = "https://" + image_url[0] if image_url else ""

        # 先將SERIAL_NO存入，後面將值改成對應的行政區
        spot_list.append([title, SERIAL_NO, longitude, latitude, image_url])
    return spot_list


# 解析第二個檔案 : 建立編號(SERIAL_NO)與行政區的關係
def build_serial_to_district_map(data):
    serial_to_district = {}
    for item in data["data"]:
        serial_no = item["SERIAL_NO"]
        address = item["address"]
        district = address.split("  ")[1].split("區")[0] + "區"
        serial_to_district[serial_no] = district
    return serial_to_district

# 將 SERIAL_NO 的值更換成行政區(完成 spot.cvs)
def add_districts(spot_list, serial_to_district_map):
    for spot in spot_list:
        serial_no = spot[1]
        spot[1] = serial_to_district_map[serial_no]
    return spot_list

# 建立 MRT 與景點的對應關係(完成 mrt.cvs)
def build_mrt_to_spots_map(spot_data, mrt_data):
    mrt_map = {}
    serial_to_station ={}
    # 先建立MRT和SERIAL_NO的映射serial_to_station
    for item in mrt_data["data"]:
        serial_no = item["SERIAL_NO"]
        mrt = item["MRT"]
        serial_to_station[serial_no] = mrt
    # 遍歷第一個檔案資料，根據自身SERIAL_NO和serial_to_station建立MRT和所屬景點的映射
    for item in spot_data.get("data", {}).get("results", []):
        spot_name = item["stitle"]
        serial_no = item["SERIAL_NO"]
        mrt_station = serial_to_station[serial_no]
        if mrt_station:
            if mrt_station not in mrt_map:
                mrt_map[mrt_station] = []
            mrt_map[mrt_station].append(spot_name)
    return mrt_map

# Step 6: 儲存資料為 spot.csv
def save_spot_to_csv(spot_list, filename="spot.csv"):
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(spot_list)


# Step 6: 儲存資料為 mrt.csv
def save_mrt_to_csv(mrt_spot_list, filename="mrt.csv"):
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        for mrt, spots in mrt_spot_list.items():
            writer.writerow([mrt] + spots)

# task1主程式
if __name__ == "__main__":
    # 讀取資料
    data_1 = read_file_from_url(url_1)
    data_2 = read_file_from_url(url_2)

    # 提取第一個檔案的基本資料
    spot_list = parse_data_file_1(data_1)

    # 建立編號(SERIAL_NO)與行政區的關係
    smap = build_serial_to_district_map(data_2)

    # 建立行政區資料
    spot_list = add_districts(spot_list, smap)

    # 儲存為 spot.csv
    save_spot_to_csv(spot_list)
    print("1. spot.csv complete！")
    
    mrt_spot_list = build_mrt_to_spots_map(data_1,data_2)
    save_mrt_to_csv(mrt_spot_list)  
    print("2. mrt.csv complete！")

# ============================================ task2 ======================================================

# 定義目標 URL 
BASE_URL = "https://www.ptt.cc"
START_URL = f"{BASE_URL}/bbs/Lottery/index.html"

# 獲取 HTML
def fetch_page_content(url):
    try:
        # pass年齡驗證
        headers = {
            "Cookie": "over18=1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            return response.read()
    except Exception as e:
        print(f"Failed to fetch page: {url}, Error: {e}")
        return None


# 解析每頁文章列表，並提取「上一頁」的 URL
def parse_articles_and_prevPage(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    articles = []
    
    # 提取文章列表
    for item in soup.find_all("div", class_="r-ent"):
        try:
            title = item.find("div", class_="title").get_text(strip=True)
            link = item.find("a")["href"] if item.find("a") else None
            if link and "(本文已被刪除)" not in title:
                articles.append({"title": title, "url": f"{BASE_URL}{link}"})
        except Exception:
            continue
    
    # 提取「上一頁」 URL
    prev_link = soup.find("a", string="‹ 上頁")
    prev_page_url = f"{BASE_URL}{prev_link['href']}" if prev_link else None
    
    return articles, prev_page_url

# 紀錄推/噓文、發佈時間
def extract_article_details(article):
    try:
        # 異常狀況處理
        html_content = fetch_page_content(article["url"])
        if not html_content:
            return {"title": "未知標題", "push_boooo": 0, "publish_time": ""}
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 記錄發佈時間
        meta_info = soup.find_all("span", class_="article-meta-value")
        publish_time = meta_info[-1].get_text() if meta_info else ""

        # 計算推/噓文
        count = 0
        push = soup.find_all("span", class_="hl push-tag")
        for item in push:
            text = item.get_text()
            if text =='推 ':
                count+=1

        boooo = soup.find_all("span", class_="f1 hl push-tag")
        for item in boooo:
            text = item.get_text()
            if text =='噓 ':
                count-=1

        return {"title": article["title"], "push_boooo": count, "publish_time": publish_time}
    except Exception as e:
        print(f"Failed to fetch page: {article["url"]}, Error: {e}")
        return {"title": "未知標題", "push_boooo": 0, "publish_time": ""}

# save as CSV
def save_to_csv(article_list, filename="article.csv"):
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(article_list)

# task2主程式
if __name__ == "__main__":
    all_articles = []
    current_url = START_URL  # 從首頁開始
    for _ in range(3):  # 抓取前三頁
        html_content = fetch_page_content(current_url)
        if not html_content:
            break
        
        # 解析當前頁面文章列表和上一頁 URL
        articles, prev_page_url = parse_articles_and_prevPage(html_content)
        
        # 提取文章詳細資訊
        for article in articles:
            details = extract_article_details(article)
            all_articles.append([details["title"], details["push_boooo"], details["publish_time"]])
        
        # 更新當前 URL 為上一頁 URL
        current_url = prev_page_url
        if not current_url:
            break
    
    # 儲存 CSV 檔案
    save_to_csv(all_articles)
    print("3. article.csv complete！")
