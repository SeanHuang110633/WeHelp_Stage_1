// burger選單
const burgerIcon = document.querySelector(".burger-icon");
const popupmenu = document.querySelector(".popup-menu");
const closeIcon = document.querySelector(".close-icon");

// 點擊burger圖示時顯示 popupmenu
burgerIcon.addEventListener("click", () => {
  popupmenu.style.display = "block";
});

// 點擊X圖示時隱藏 popupmenu
closeIcon.addEventListener("click", () => {
  popupmenu.style.display = "none";
});

// 寬度大於 600px 自動關閉popupmenu
window.addEventListener("resize", handleResize);
function handleResize() {
  const width = window.innerWidth; // 取得目前視窗的寬度
  if (width > 600) {
    popupmenu.style.display = "none";
  }
}

// 動態渲染
// API URL
const API_URL =
  "https://padax.github.io/taipei-day-trip-resources/taipei-attractions-assignment-1";

// DOM 元件
const mainContent = document.querySelector(".main-content");
const smallBoxesContainer = document.createElement("div");
smallBoxesContainer.classList.add("small-boxes");
const bigBoxesContainer = document.createElement("div");
bigBoxesContainer.classList.add("big-boxes");
const loadMoreButton = document.querySelector("#load-more");

// 定義 spots 渲染相關變數
let spotsList = []; // 儲存所有景點資料
let renderedCount = 0; // 已渲染的景點數量
const BATCH_SIZE = 10; // 每次載入的景點數量

// Fetch data
fetch(API_URL)
  .then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then((data) => {
    spotsList = data.data.results; // 儲存完整景點資料
    console.log(spotsList);
    renderBoxes(data);
  })
  .catch((error) => {
    console.error("Failed to fetch data:", error);
  });

// 初始化渲染:取前 13 筆
function renderBoxes(data) {
  const spots = data.data.results.slice(0, 13);
  renderedCount = 13; // 紀錄目前渲染到底幾筆

  spots.forEach((spot, index) => {
    const { stitle, file } = spot;

    // 提取第一張圖片
    const imageUrl = spot.filelist.split("https://")[1]
      ? `https://${spot.filelist.split("https://")[1]}`
      : "./image.jpg";

    if (index < 3) {
      // 前 3 個景點 -> 小框
      const smallBox = createSmallBox(stitle, imageUrl);
      smallBoxesContainer.appendChild(smallBox);
      mainContent.appendChild(smallBoxesContainer);
    } else {
      // 後 10 個景點 -> 大框
      const bigBox = createBigBox(stitle, imageUrl);

      bigBoxesContainer.appendChild(bigBox);
      mainContent.appendChild(bigBoxesContainer);
    }
  });
}

// 建立 Small Box
function createSmallBox(title, imageUrl) {
  const box = document.createElement("div");
  box.classList.add("small-box");

  const img = document.createElement("img");
  img.src = imageUrl;
  img.alt = title;

  const p = document.createElement("p");
  p.textContent = title;

  box.appendChild(img);
  box.appendChild(p);

  return box;
}

// 建立 Big Box Function
function createBigBox(title, imageUrl) {
  const box = document.createElement("div");
  box.classList.add("big-box");

  const img = document.createElement("img");
  img.src = imageUrl;
  img.alt = title;

  const starIcon = document.createElement("div");
  starIcon.classList.add("star-icon");

  const starImg = document.createElement("img");
  starImg.src = "./star.png";
  starImg.alt = "Star Icon";
  starIcon.appendChild(starImg);

  const titleBlock = document.createElement("div");
  titleBlock.classList.add("title-block");
  titleBlock.textContent = title;

  box.appendChild(img);
  box.appendChild(starIcon);
  box.appendChild(titleBlock);

  return box;
}

// load more 功能
let disableLoadMore = false; // 超過spotList長度就不能 load ，改為true
function renderNextBatch() {
  if (!disableLoadMore) {
    for (let i = renderedCount; i < renderedCount + BATCH_SIZE; i++) {
      // 同上面的渲染大框功能
      const { stitle, filelist } = spotsList[i];
      const imageUrl = filelist.split("https://")[1]
        ? `https://${filelist.split("https://")[1]}`
        : "./image.jpg";
      const bigBox = createBigBox(stitle, imageUrl);
      bigBoxesContainer.appendChild(bigBox);
      mainContent.appendChild(bigBoxesContainer);

      if (i === spotsList.length - 1) {
        disableLoadMore = true;
        break;
      }
    }
    renderedCount += BATCH_SIZE;
  } else {
    window.alert("沒有spots了");
  }
}

//  Load More Button
loadMoreButton.addEventListener("click", renderNextBatch);
