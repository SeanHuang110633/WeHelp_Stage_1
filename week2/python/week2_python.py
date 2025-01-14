import sys
sys.stdout.reconfigure(encoding='utf-8')  # 強制標準輸出使用 UTF-8
sys.stdin.reconfigure(encoding='utf-8')   # 強制標準輸入使用 UTF-8
sys.stderr.reconfigure(encoding='utf-8')  # 強制標準錯誤使用 UTF-8
print("================== task1 =======================")
# task1
def find_and_print(messages, current_station):
    # 列出綠線車站
    mrt_green_line = [
        "Songshan",
        "Nanjing Sanmin",
        "Taipei Arena",
        "Nanjing Fuxing",
        "Songjiang Nanjing",
        "Zhongshan",
        "Beimen",
        "Ximen",
        "Xiaonanmen",
        "Chiang Kai-Shek Memorial Hall",
        "Guting",
        "Taipower Building",
        "Gongguan",
        "Wanlong",
        "Jingmei",
        "Dapinglin",
        "Qizhang",
        "Xiaobitan",
        "Xindian City Hall",
        "Xindian"
    ]

    # 獲取自己所在地車站index
    my_station_index = mrt_green_line.index(current_station)

    # 初始化最小距離與最近朋友的變數
    min_distance = float('inf')  #  記錄自己車站與朋友車站的距離
    res = ""  # 記錄與自己最近的朋友

    for friend, message in messages.items():
        # 獲取朋友的位置描述(使用next生成器)
        station_name = next((station for station in mrt_green_line if station in message), None) 
        if station_name:
            # 獲取朋友車站的索引
            friend_station_index = mrt_green_line.index(station_name)
            # 計算自己與朋友的距離
            distance = abs(my_station_index - friend_station_index)

            if station_name == "Xiaobitan":
                # 任何地方到小碧潭的距離都等於其到Qizhang再加1
                distance = abs(my_station_index - mrt_green_line.index("Qizhang")) + 1

            if distance < min_distance:
                min_distance = distance # 如果比前一個朋友更近，就更新minDistance
                res = friend # 同時也更新res，代表目前找到最近的朋友
        else:
            print("兄弟，你沒朋友")

    print(res)


# 測試資料
messages = {
    "Leslie": "I'm at home near Xiaobitan station.",
    "Bob": "I'm at Ximen MRT station.",
    "Mary": "I have a drink near Jingmei MRT station.",
    "Copper": "I just saw a concert at Taipei Arena.",
    "Vivian": "I'm at Xindian station waiting for you."
}

find_and_print(messages, "Wanlong")  # print Mary
find_and_print(messages, "Songshan")  # print Copper
find_and_print(messages, "Qizhang")  # print Leslie
find_and_print(messages, "Ximen")  # print Bob
find_and_print(messages, "Xindian City Hall")  # print Vivian

print("================== task2 =======================")
# task2

# 建立顧問時間表的方法
def build_consultants_timetable(consultants):
    # 使用字典來存儲每位顧問的時間表
    res = {}
    for consultant in consultants:
        res[consultant['name']] = [True] * 24
    return res


def book(consultants, hour, duration, criteria):
    global consultants_timetable  # 使用全域變數的時間表

    # 考量價格 
    if criteria == "price":
        
        # 根據price排列諮詢師順序
        consultants.sort(key=lambda c: c['price'])

        for consultant in consultants:
            timetable = consultants_timetable[consultant['name']]  # 取得顧問的時間表
            available = True  # 一開始假定可以預約

            # 檢查時間段是否可用
            for i in range(duration):
                if not timetable[hour + i]:  # 時間段已被佔用
                    available = False
                    break  

            if available:
                # 標記時間段為不可用
                for i in range(duration):
                    timetable[hour + i] = False
                print(consultant['name'])  
                return

        # 沒得選
        print("No Service")

    else:  
        # 考量rate
        # 根據rate排列諮詢師順序
        consultants.sort(key=lambda c: c['rate'], reverse=True)

        
        for consultant in consultants:
            timetable = consultants_timetable[consultant['name']]  
            available = True 

            
            for i in range(duration):
                if not timetable[hour + i]:  
                    available = False
                    break  

            if available:
                
                for i in range(duration):
                    timetable[hour + i] = False
                print(consultant['name'])  
                return

        
        print("No Service")


consultants = [
    {"name": "John", "rate": 4.5, "price": 1000},
    {"name": "Bob", "rate": 3, "price": 1200},
    {"name": "Jenny", "rate": 3.8, "price": 800},
]

# 建立時間表
consultants_timetable = build_consultants_timetable(consultants)


book(consultants, 15, 1, "price")  # 輸出 Jenny
book(consultants, 11, 2, "price")  # 輸出 Jenny
book(consultants, 10, 2, "price")  # 輸出 John
book(consultants, 20, 2, "rate")   # 輸出 John
book(consultants, 11, 1, "rate")   # 輸出 Bob
book(consultants, 11, 2, "rate")   # 輸出 No Service
book(consultants, 14, 3, "price")  # 輸出 John

print("================== task3 =======================")
# task3
def find_unique_middle_name(*data):
    # 記錄各中間名出現次數
    middle_name_count = {}

    # 記錄名字與其中間名的映射
    name_to_middle_name = {}

    # 提取每個名字的中間名
    for name in data:
        if len(name) == 2:
            # 2個字，取第2個字
            middle_name = name[1]
        else:
            # 其他取倒數第 2 個字
            middle_name = name[-2]

        # 記錄名字與中間名的映射
        name_to_middle_name[name] = middle_name

        # 記錄中間名出現次數
        if middle_name in middle_name_count:
            middle_name_count[middle_name] += 1
        else:
            middle_name_count[middle_name] = 1

    # 遍歷名字，找到中間名出現次數為 1 的名字
    for name in data:
        middle_name = name_to_middle_name[name]
        if middle_name_count[middle_name] == 1:
            print(name)
            return

    print("沒有")


find_unique_middle_name("彭大牆", "陳王明雅", "吳明")  # 輸出 "彭大牆"
find_unique_middle_name("郭靜雅", "王立強", "郭林靜宜", "郭立恆", "林花花")  # 輸出 "林花花"
find_unique_middle_name("郭宣雅", "林靜宜", "郭宣恆", "林靜花")  # 輸出 "沒有"
find_unique_middle_name("郭宣雅", "夏曼藍波安", "郭宣恆")  # 輸出 "夏曼藍波安"


print("================== task4 =======================")
# task4

def get_number(index):
    arr = []  # 創建array存放題目的number sequence
    number = 0  
    j = 2  # j為索引，初始值為 2，每次 +3，即索引為 2、5、8、11...
    
    for i in range(index + 1):
        arr.append(number)  
        if i == j:  
            number -= 1
            j += 3
            continue  # 跳過後續的加 4 操作
        number += 4  
    
    print(arr.pop())  # 輸出數列的最後一個值


get_number(1) # print 4
get_number(5) # print 15
get_number(10) # print 25
get_number(30) # print 70


print("================== task5 =======================");
# task5
def find(spaces, stat, n):
    # 建立字典存儲可服務的車廂及其座位數
    serve_car_with_seats = {}
    for i in range(len(stat)):
        if stat[i]:  # 若該車廂可服務乘客
            serve_car_with_seats[i] = spaces[i]

    # 設定最小差值，及結果索引
    min_diff = float('inf')
    res = -1

    # 遍歷可服務車廂，找出符合條件者
    for key, value in serve_car_with_seats.items():
        if value >= n:  # 座位數須大於等於 n
            diff = value - n  
            if diff < min_diff:  
                min_diff = diff
                res = key

    print(res)  


find([3, 1, 5, 4, 3, 2], [0, 1, 0, 1, 1, 1], 2) # print 5
find([1, 0, 5, 1, 3], [0, 1, 0, 1, 1], 4) # print -1
find([4, 6, 5, 8], [0, 1, 1, 1], 4) # print 2
