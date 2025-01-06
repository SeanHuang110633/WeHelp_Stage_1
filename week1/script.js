const burgerIcon = document.querySelector('.burger-icon');
const popupmenu = document.querySelector('.popup-menu');
const closeIcon = document.querySelector('.close-icon');

// 點擊burger圖示時顯示 popupmenu
burgerIcon.addEventListener('click', () => {
    popupmenu.style.display = 'block';
});

// 點擊X圖示時隱藏 popupmenu
closeIcon.addEventListener('click', () => {
    popupmenu.style.display = 'none';
});

// 寬度大於 600px 自動關閉popupmenu
window.addEventListener('resize', handleResize);
function handleResize() {
    const width = window.innerWidth; // 取得目前視窗的寬度
    if (width > 600) {
        popupmenu.style.display = "none"; 
    }
}
  