window.onload = function () {
  checkToken();
  getAttraction();
};

/* -------------------依據id顯示景點相關資料------------------- */
// https://ithelp.ithome.com.tw/articles/10204214
// https://blog.csdn.net/weixin_48594833/article/details/121786784
function getAttraction() {
  // 透過目前的網址取得id
  const url = window.location.href;
  const urlParts = url.split("/");
  const id = urlParts[urlParts.length - 1];

  fetch(`/api/attractions/${id}`)
    .then((response) => response.json())
    .then((responseData) => {
      if (responseData["error"]) {
        throw new Error(responseData["message"]); // 退出then，錯誤訊息傳遞到catch
      }
      data = responseData["data"];
      initializeContent();
      // 在資料載入後，預先載入所有圖片
      preloadImages(data.images).then(() => {
        const loadingSpinner = document.querySelector(".loading-spinner");
        const imagesElement = document.querySelector(".images");

        loadingSpinner.style.display = "none"; // 隱藏載入中效果
        imagesElement.style.display = "block";
      });
    })
    .catch((error) => {
      console.error(error);
    });
}

// 預先載入圖片
function preloadImages(imageUrls) {
  const promises = [];
  for (const imageUrl of imageUrls) {
    const image = new Image();
    image.src = imageUrl;
    const promise = new Promise((resolve) => {
      image.onload = resolve;
    });
    promises.push(promise);
  }
  return Promise.all(promises);
}

// 需要更新內容的部分，用物件打包起來
const elements = {
  leftImg: document.querySelector(".btn_left"),
  rightImg: document.querySelector(".btn_right"),
  images: document.querySelector(".images"),
  attractionName: document.querySelector(".attractionName"),
  category: document.querySelector(".category"),
  mrt: document.querySelector(".mrt"),
  description: document.querySelector(".description"),
  address: document.querySelector(".address"),
  transport: document.querySelector(".transport"),
  circleContainer: document.querySelector(".circle-container"),
};

// 初始化為第一張圖片
let imgIndex = 0;

//初始化內容
function initializeContent() {
  elements.images.src = data.images[imgIndex];
  elements.attractionName.textContent = data.name;
  elements.category.textContent = data.category;
  elements.mrt.textContent = data.mrt;
  elements.description.textContent = data.description;
  elements.address.textContent = data.address;
  elements.transport.textContent = data.transport;
  // 建立小圓點
  data["images"].forEach((_, i) => {
    //用_去忽略第一個參數
    const circleImg = document.createElement("img");
    circleImg.src =
      i === imgIndex
        ? "../static/IMG/circle_black.png"
        : "../static/IMG/circle_current.png";
    elements.circleContainer.appendChild(circleImg);
  });
}

// 更新顯示的圖片
function changeImage(action) {
  const newIndex = action === "prev" ? imgIndex - 1 : imgIndex + 1;
  if (newIndex >= 0 && newIndex < data.images.length) {
    imgIndex = newIndex;
    updateImageAndCircle();
  }
}

// 更新圖片和小圓點
function updateImageAndCircle() {
  // 在更新圖片之前，先將圖片的透明度設為 0
  elements.images.style.opacity = 0;
  elements.circleContainer.style.opacity = 0;
  elements.leftImg.style.opacity = 0;
  elements.rightImg.style.opacity = 0;

  // 使用 setTimeout 函數來延遲更新圖片，讓轉場效果有時間播放
  setTimeout(() => {
    elements.images.src = data.images[imgIndex];
    const circleImgs = elements.circleContainer.querySelectorAll("img");
    circleImgs.forEach((circleImg, index) => {
      circleImg.src =
        index === imgIndex
          ? "../static/IMG/circle_black.png"
          : "../static/IMG/circle_current.png";
    });
    // 更新圖片之後，將圖片的透明度設回為 1
    elements.images.style.opacity = 1;
    elements.circleContainer.style.opacity = 1;
    elements.leftImg.style.opacity = 1;
    elements.rightImg.style.opacity = 1;
  }, 500); // 同CSS轉場秒數
}

/* ------------------選擇時間按鈕----------------------------- */
function timeButton(buttonClass) {
  const button = document.querySelector(`.${buttonClass}`);
  button.src = "../static/IMG/btn_select.png";
  document.querySelector(".exp").textContent =
    buttonClass === "am_btn" ? "新台幣2,000元" : "新台幣2,500元";

  /* 不能同時選擇兩種時間 */

  // 如果當下選擇am，則otherClass就等於pm_btn
  const timeClass = buttonClass === "am_btn" ? "pm_btn" : "am_btn";
  //選擇對應的按鈕
  const otherButton = document.querySelector(`.${timeClass}`);
  //改變回沒被選擇時的圖示
  otherButton.src = "../static/IMG/btn.png";
}

// 初始化 Flatpickr 插件
// https://www.jsdelivr.com/package/npm/flatpickr
// https://juejin.cn/post/7225478065392287804
// https://www.cnblogs.com/webqiand/p/11004910.html

const dateInput = document.querySelector(".date-input");

//初始化格式
flatpickr(dateInput, {
  dateFormat: "Y/m/d",
});

const setDefaults = dateInput._flatpickr;

function openFlatpickr() {
  setDefaults.open();
}

/* ------------------預約行程------------------ */
async function submitBooking() {
  const bookingData = bookingCheck();

  if (!bookingData) {
    alert("請選擇完整的預定行程");
    return;
  }

  //取得後端傳過來的token
  const token = localStorage.getItem("token");

  try {
    const response = await fetch("/api/booking", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(bookingData),
    });

    const data = await response.json();

    if (response.status === 200) {
      // 轉預定頁面
      window.location.href = "/booking";
    } else if (response.status === 403) {
      // 未登錄
      console.error(data["message"]);
      openSignin();
    } else if (response.status === 400) {
      // 資料輸入不正確
      console.error(data["message"]);
    } else if (response.status === 500) {
      // 伺服器錯誤
      console.error(data["message"]);
    }
  } catch (error) {
    console.error(error);
  }
}

function bookingCheck() {
  //景點ID
  const url = window.location.href;
  const urlParts = url.split("/");
  const attractionId = urlParts[urlParts.length - 1];
  //日期
  const dateInput = document.querySelector(".date-input");
  const selectedDate = dateInput.value;
  //時間、價格
  let selectedTime = "";
  let price = "";
  const amButton = document.querySelector(".am");
  const pmButton = document.querySelector(".pm");
  //檢查圖片名稱，找出被選擇的選項
  if (amButton.querySelector("img").src.endsWith("btn_select.png")) {
    selectedTime = "morning";
    price = "2000";
  } else if (pmButton.querySelector("img").src.endsWith("btn_select.png")) {
    selectedTime = "afternoon";
    price = "2500";
  }

  // 檢查選項是否沒有選到
  if (!attractionId || !selectedDate || !selectedTime || !price) {
    return null; // 數據不完整
  }

  const bookingData = {
    attractionId: parseInt(attractionId),
    date: selectedDate,
    time: selectedTime,
    price: parseFloat(price),
  };

  return bookingData;
}
