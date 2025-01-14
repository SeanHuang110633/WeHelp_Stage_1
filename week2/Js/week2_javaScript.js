console.log("================== task1 =======================");
/* task1 */
function findAndPrint(messages, currentStation) {
  // 列出綠線車站(讓Xiaobitan再第一個元素)
  const mrtGreenLine = [
    "Xiaobitan",
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
    "Xindian City Hall",
    "Xindian",
  ];

  // 獲取自己所在地車站index
  const myStationIndex = mrtGreenLine.indexOf(currentStation);
  let minDistance = Infinity; // 記錄自己車站與朋友車站的距離
  let res = ""; // 記錄與自己最近的朋友
  let a = [];

  for (let friend in messages) {
    const message = messages[friend]; // 取得朋友的位置描述

    // 遍歷 mrtGreenLine 找出位置描述中的車站名稱
    const stationName = mrtGreenLine.find((station) =>
      message.includes(station)
    );

    if (stationName) {
      const friendStationIndex = mrtGreenLine.indexOf(stationName);
      let distance;
      // 如果自己跟朋友都在小碧潭
      if (stationName == "Xiaobitan" && currentStation == "Xiaobitan") {
        distance = 0;
      } else if (stationName == "Xiaobitan") {
        // 如果朋友在小碧潭，那到朋友的距離等於到Qizhang再加1
        distance =
          Math.abs(myStationIndex - mrtGreenLine.indexOf("Qizhang")) + 1;
      } else if (currentStation == "Xiaobitan") {
        // 如果自己在小碧潭，那到任何朋友的距離，等於從Qizhang出發到朋友所在地的距離再加1
        distance =
          Math.abs(friendStationIndex - mrtGreenLine.indexOf("Qizhang")) + 1;
      } else {
        distance = Math.abs(myStationIndex - friendStationIndex); // 計算自己與朋友的距離
      }

      if (distance < minDistance) {
        minDistance = distance; // 如果比前一個朋友更近，就更新minDistance
        res = friend; // 同時也更新res，代表目前找到最近的朋友
      }
    } else {
      console.log("兄弟，你沒朋友");
    }
  }
  console.log(res);
}

messages = {
  Leslie: "I'm at home near Xiaobitan station.",
  Bob: "I'm at Ximen MRT station.",
  Mary: "I have a drink near Jingmei MRT station.",
  Copper: "I just saw a concert at Taipei Arena.",
  Vivian: "I'm at Xindian station waiting for you.",
};

findAndPrint(messages, "Wanlong"); // print Mary
findAndPrint(messages, "Songshan"); // print Copper
findAndPrint(messages, "Qizhang"); // print Leslie
findAndPrint(messages, "Ximen"); // print Bob
findAndPrint(messages, "Xindian City Hall"); // print Vivian

console.log("================== task2 =======================");
/* task2 */

// 建立顧問時間表的方法
function buildConsultantsTimetable(consultants) {
  let res = new Map();
  consultants.forEach((element) => {
    res.set(element.name, new Array(24).fill(true));
  });
  return res;
}

function book(consultants, hour, duration, criteria) {
  if (criteria === "price") {
    /* 考量價格*/

    // 根據price排列諮詢師順序
    consultants.sort((a, b) => a.price - b.price);

    for (let consultant of consultants) {
      let timetable = consultantsTimetable.get(consultant.name); // 取得諮詢師時間表
      let avaliable = true; // 一開始假定可以預約

      // 檢查時間段是否可用
      for (let i = 0; i < duration; i++) {
        if (!timetable[hour + i]) {
          // 申請時間段已被佔用
          avaliable = false;
          break;
        }
      }
      if (avaliable) {
        // 標記時間段為不可用
        for (let i = 0; i < duration; i++) {
          timetable[hour + i] = false;
        }
        console.log(consultant.name);
        return;
      }
    }

    // 沒得選
    console.log("No Service");
  } else {
    /* 考量評價*/

    // 根據rate排列諮詢師順序
    consultants.sort((a, b) => b.rate - a.rate);

    for (let consultant of consultants) {
      let timetable = consultantsTimetable.get(consultant.name);
      let avaliable = true;
      for (let i = 0; i < duration; i++) {
        if (!timetable[hour + i]) {
          avaliable = false;
          break;
        }
      }
      if (avaliable) {
        for (let i = 0; i < duration; i++) {
          timetable[hour + i] = false;
        }
        console.log(consultant.name);
        return;
      }
    }

    // 4. 沒得選
    console.log("No Service");
  }
}

const consultants = [
  { name: "John", rate: 4.5, price: 1000 },
  { name: "Bob", rate: 3, price: 1200 },
  { name: "Jenny", rate: 3.8, price: 800 },
];

let consultantsTimetable = buildConsultantsTimetable(consultants);

book(consultants, 15, 1, "price"); // Jenny
book(consultants, 11, 2, "price"); // Jenny
book(consultants, 10, 2, "price"); // John
book(consultants, 20, 2, "rate"); // John
book(consultants, 11, 1, "rate"); // Bob
book(consultants, 11, 2, "rate"); // No Service
book(consultants, 14, 3, "price"); // John

console.log("================== task3 =======================");

/* task3 */
function findUniqueMiddleName(...data) {
  // 記錄每個中間名出現的次數
  const middleNameCount = {};

  // 記錄名字與其中間名的映射
  const nameToMiddleName = {};

  // 提取每個名字的中間名
  data.forEach((name) => {
    let middleName;

    if (name.length === 2) {
      // 2 個字，取第 2 個字
      middleName = name[1];
    } else {
      // 其他取倒數第 2 個字
      middleName = name[name.length - 2];
    }

    // 記錄名字與其中間名的映射
    nameToMiddleName[name] = middleName;

    // 計算中間名出現次數
    if (middleNameCount[middleName]) {
      middleNameCount[middleName]++;
    } else {
      middleNameCount[middleName] = 1;
    }
  });

  // 遍歷名字，找到中間名出現次數為 1 的名字
  for (const name of data) {
    const middleName = nameToMiddleName[name];
    if (middleNameCount[middleName] === 1) {
      console.log(name);
      return;
    }
  }

  console.log("沒有");
}

findUniqueMiddleName("彭大牆", "陳王明雅", "吳明"); // print "彭大牆"
findUniqueMiddleName("郭靜雅", "王立強", "郭林靜宜", "郭立恆", "林花花"); // print "林花花"
findUniqueMiddleName("郭宣雅", "林靜宜", "郭宣恆", "林靜花"); // print "沒有"
findUniqueMiddleName("郭宣雅", "夏曼藍波安", "郭宣恆"); // print "夏曼藍波安"

console.log("================== task4 =======================");

/* task4 */
function getNumber(index) {
  let arr = []; // 創建array存放題目的number sequence
  let number = 0;
  let j = 2; // j為索引，起始為2，每次+3，即索引為2、5、8、11...
  for (let i = 0; i <= index; i++) {
    arr.push(number);
    if (i === j) {
      number -= 1;
      j += 3;
      continue; // 跳過後續的加 4 操作
    }
    number += 4;
  }
  console.log(arr.pop()); // 輸出數列的最後一個值
}
getNumber(1); // print 4
getNumber(5); // print 15
getNumber(10); // print 25
getNumber(30); // print 70

console.log("================== task5 =======================");
/* task5 */
function find(spaces, stat, n) {
  // 獲取當前可serve passengers的車廂編號
  const serveCarNumberWithSeats = new Map();
  for (let i = 0; i < stat.length; i++) {
    if (stat[i]) {
      serveCarNumberWithSeats.set(i, spaces[i]);
    }
  }

  // 設定最小差值，及結果索引
  let min = Infinity;
  let res = -1;
  // 遍歷可服務車廂，找出符合條件者
  serveCarNumberWithSeats.forEach((value, key) => {
    if (value - n < min && value - n >= 0) {
      min = value - n;
      res = key;
    }
  });

  console.log(res);
}
find([3, 1, 5, 4, 3, 2], [0, 1, 0, 1, 1, 1], 2); // print 5
find([1, 0, 5, 1, 3], [0, 1, 0, 1, 1], 4); // print -1
find([4, 6, 5, 8], [0, 1, 1, 1], 4); // print 2
