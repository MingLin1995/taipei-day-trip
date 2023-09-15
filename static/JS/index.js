window.onload = function () {
  getMrts();
  loadAttractions(nextPage, keyword);
};

/* ------------------插入捷運站名稱、點擊後顯示在搜尋欄------------------ */
// 使用fetch()函數獲取API數據
function getMrts() {
  fetch("/api/mrts")
    .then((response) => response.json()) //回傳資料解析成JSON格式
    .then((data) => {
      if (data["error"]) {
        console.log(data["message"]);
      } else {
        // data包含了從API獲取的捷運站名稱數據
        data["data"].forEach((station) => {
          // 創建新的<li>元素
          const listItem = document.createElement("li");
          listItem.textContent = station; // 將捷運站名稱設定為<li>的內容
          list.appendChild(listItem); // 將<li>添加到<ul>

          // 添加點擊事件監聽器到每個<li>元素
          listItem.onclick = function () {
            const stationName = listItem.textContent; // 獲取點擊的捷運站名稱
            const inputElement = document.querySelector(".search-input");
            inputElement.value = stationName; // 將捷運站名稱設為輸入框的值

            // 执行搜索操作
            searchAttractions();
          };
        });
        // 取得捷運站名稱後，再取得li寬度
        listItemWidth = document.querySelector(".list li").offsetWidth;
      }
    })
    .catch((error) => {
      console.error("發生錯誤：", error);
    });
}

/* -----------------------------scroll-button------------------------------ */
//https://www.shubo.io/element-size-scrolling/
//https://juejin.cn/post/7129062026055254029
const list = document.querySelector(".list");
let listItemWidth; //透過getMrts()取得li寬度
let scrollDistance = 0; //初始捲動距離

function scrollNext() {
  //(已捲動寬度+可視範圍寬度) < 總寬度(避免點擊時一直算次數)，就可以增加1個li寬度
  if (scrollDistance + list.offsetWidth < list.scrollWidth) {
    scrollDistance += listItemWidth; //一次移動一個li寬度
    list.scrollTo({
      left: scrollDistance, //水平捲動
      behavior: "smooth", //平滑捲動效果
    });
  }
}

function scrollPrev() {
  //已經捲動距離>0，才可以往回移動(避免一直計算點擊次數)
  if (scrollDistance > 0) {
    scrollDistance -= listItemWidth; //沒有right屬性，所以用-回去的
    list.scrollTo({
      left: scrollDistance,
      behavior: "smooth",
    });
  }
}

/* ------------------------頁面景點顯示、搜尋功能------------------------- */
//https://www.techiedelight.com/zh-tw/handle-resize-event-javascript/
//https://ithelp.ithome.com.tw/articles/10273729
let nextPage = 0; // 預設頁碼為0
let keyword = "";

// 滑動視窗
window.onscroll = function () {
  if (nextPage !== null && checkBottom()) {
    loadAttractions(nextPage, keyword);
  }
};
// 縮放視窗
window.onresize = function () {
  if (nextPage !== null && checkBottom()) {
    loadAttractions(nextPage, keyword);
  }
};

// 檢查是否滑動到到底部
function checkBottom() {
  //計算的當下，值不會變，所以用const
  const scrollTop = window.scrollY; // 已經滾動的高度
  const clientHeight = window.innerHeight; // 整個視窗可見範圍的高度
  const scrollHeight = document.body.scrollHeight; // 完整内容的高度
  const bottomThreshold = 10; // 底部距離
  // 所有高度-(滾動+可視範圍) < 10 代表接近底部
  return scrollHeight - (scrollTop + clientHeight) < bottomThreshold;
}

// 點擊搜尋按鈕，觸發取得景點資訊功能
const searchInput = document.querySelector(".search-input");
function searchAttractions() {
  keyword = searchInput.value.trim(); //去除首尾空格，避免發生錯誤
  nextPage = 0; // 預設為0
  loadAttractions(nextPage, keyword);
}
// 按下enter，觸發點擊搜尋按鈕功能
searchInput.addEventListener("keyup", function (event) {
  if (event.key === "Enter") {
    // 如果按下的是 Enter 按鍵，執行搜尋功能
    searchAttractions();
  }
});

let loadingStatus = false; // 載入狀態，預設還沒載入(避免網路時間差，連續呼叫)
// 取得景點資訊功能
function loadAttractions(page, keyword) {
  //如果還沒載入，就往下執行，如果載入了，就跳出不要繼續執行。
  if (loadingStatus) {
    return;
  }

  loadingStatus = true; //載入狀態開始

  //檢查是否有輸入keyword，有輸入就加入keyword
  let apiUrl = `/api/attractions?page=${page}`;
  if (keyword) {
    apiUrl += `&keyword=${keyword}`;
  }

  fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
      if (data["error"]) {
        throw new Error(data["message"]);
      }
      const attractionsList = document.querySelector(".attractions");

      if (page === 0) {
        attractionsList.innerHTML = ""; // 清空內容
      }

      // 如果data沒有任何資料，就顯示查無任何景點資料
      if (data["data"].length === 0) {
        const noResultsMessage = document.createElement("div");
        noResultsMessage.className = "centered-text";
        noResultsMessage.textContent = "查無任何景點資料";
        attractionsList.appendChild(noResultsMessage);
      } else {
        data["data"].forEach((attraction) => {
          const attractionItem = document.createElement("li");
          attractionItem.className = "attraction";

          //轉跳景點頁面
          attractionItem.onclick = function () {
            const attractionId = attraction["id"];
            const redirectUrl = `/attraction/${attractionId}`;
            window.location.href = redirectUrl;
          };
          attractionsList.appendChild(attractionItem);

          //img
          const img = document.createElement("img");
          img.src = attraction["images"][0];
          attractionItem.appendChild(img);

          //.detail-1
          const detail1 = document.createElement("div");
          detail1.className = "detail-1";
          detail1.textContent = attraction["name"];
          attractionItem.appendChild(detail1);

          //.detail-2
          const detail2 = document.createElement("div");
          detail2.className = "detail-2";
          attractionItem.appendChild(detail2);

          //.detail-2>p
          const p1 = document.createElement("p");
          p1.textContent = attraction["mrt"];
          detail2.appendChild(p1);

          //.detail-2>p
          const p2 = document.createElement("p");
          p2.textContent = attraction["category"];
          detail2.appendChild(p2);
        });
      }

      if (data["nextPage"] === null) {
        nextPage = null;
      } else {
        nextPage = data["nextPage"]; // 更新下一頁的頁碼
      }

      loadingStatus = false; // 載入狀態結束
    })
    .catch((error) => {
      console.error(error);
    });
}

//建立標籤、屬性
function createElement(tag, className, textContent) {
  const element = document.createElement(tag);
  element.className = className;
  if (textContent) element.textContent = textContent;
  return element;
}
