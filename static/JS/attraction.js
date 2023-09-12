getAttraction();

/* -------------------登入/註冊視窗功能-------------------- */
function openSignin() {
  document.querySelector(".dialog-section").style.display = "block";
  document.querySelector(".signin").style.display = "block";
}

function closeDialog() {
  document.querySelector(".dialog-section").style.display = "none";
  document.querySelector(".signin").style.display = "none";
  document.querySelector(".signup").style.display = "none";
}

function showSignup() {
  document.querySelector(".signin").style.display = "none";
  document.querySelector(".signup").style.display = "block";
}

function showSignin() {
  document.querySelector(".signin").style.display = "block";
  document.querySelector(".signup").style.display = "none";
}

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
      // 初始化內容
      initializeContent();
    })
    .catch((error) => {
      console.error(error);
    });
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

// 按按鈕，更新圖片index
function changeImage(action) {
  const newIndex = action === "prev" ? imgIndex - 1 : imgIndex + 1;
  //避免可以按過頭
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
  }, 700); // 同CSS轉場秒數
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
