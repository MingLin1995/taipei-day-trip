window.onload = async function () {
  const isLoggedIn = await checkToken();
  if (!isLoggedIn) {
    window.location.href = "/"; // 沒登錄就回首頁
  } else {
    fetchBookingInfo(); // 取得訂單資訊

    const userNameElements = document.querySelectorAll(".userName"); // 使用者名稱
    userNameElements.forEach((element) => {
      element.textContent = isLoggedIn.data.name;
    });

    document.getElementById("contactName").value = isLoggedIn.data.name; // 輸入資訊 使用者名稱
    document.getElementById("contactEmail").value = isLoggedIn.data.email; // 輸入資訊 EMAIL

    setupTapPay();
  }
};

let bookingData = {};

async function fetchBookingInfo() {
  //取得後端傳過來的token
  const token = localStorage.getItem("token");
  try {
    const response = await fetch("/api/booking", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (response.status === 200) {
      if (data.error) {
        console.log(data.message);
      } else if (data.data) {
        bookingData = {
          price: data.data.price,
          attractionId: data.data.attraction.id,
          attractionName: data.data.attraction.name,
          attractionAddress: data.data.attraction.address,
          attractionImage: data.data.attraction.image,
          date: data.data.date,
          time: data.data.time,
        };

        //如果有訂單資料
        //更新畫面資訊
        const frame1 = document.getElementById("frame1");
        const frame2 = document.getElementById("frame2");
        frame1.style.display = "none";
        frame2.style.display = "block";
        document.querySelector(".footer.special").style.display = "none";

        document.getElementById("image").src = data.data.attraction.image;
        document.getElementById("name").textContent = data.data.attraction.name;
        document.getElementById("date").textContent = data.data.date;
        document.getElementById("time").textContent = data.data.time;

        if (data.data.time == "morning") {
          document.getElementById("time").textContent = "早上9點到中午12點";
        } else {
          document.getElementById("time").textContent = "中午12點到下午4點";
        }

        if (data.data.price == 2000) {
          document.getElementById("price").textContent = "新台幣2,000元";
          document.getElementById("priceText").textContent = "新台幣2,000元";
        } else {
          document.getElementById("price").textContent = "新台幣2,500元";
          document.getElementById("priceText").textContent = "新台幣2,500元";
        }

        document.getElementById("address").textContent =
          data.data.attraction.address;
      } else {
        //如果沒有訂單資料
        document.querySelector(".footer.normal").style.display = "none";

        console.log(data.data);
      }
    } else if (response.status === 403) {
      console.log(data.message);
    } else {
      console.log(data.message);
    }
  } catch (error) {
    console.error(error);
  }
}

function delButton() {
  const token = localStorage.getItem("token");
  const apiUrl = "/api/booking";
  fetch(apiUrl, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.ok) {
        console.log(data);
        window.location.reload(); //刪除訂單資訊後重新整理頁面
      } else {
        console.log("刪除失敗");
      }
    })
    .catch((error) => {
      console.error(error);
    });
}

/* -------------------------金流串接---------------------------------- */
// https://github.com/TapPay/tappay-web-example/tree/master/TapPay_Fields

async function setupTapPay() {
  try {
    const config = await get_config();
    APP_ID = config["APP_ID"];
    APP_KEY = config["APP_KEY"];
    TPDirect.setupSDK(APP_ID, APP_KEY, "sandbox");

    var fields = {
      number: {
        element: "#card-number",
        placeholder: "**** **** **** ****",
      },
      expirationDate: {
        element: document.getElementById("card-expiration-date"),
        placeholder: "MM / YY",
      },
      ccv: {
        element: "#card-ccv",
        placeholder: "CCV",
      },
    };

    TPDirect.card.setup({
      fields: fields,
      styles: {
        // Style all elements
        input: {
          color: "gray",
        },
        // style valid state
        ".valid": {
          color: "green",
        },
        // style invalid state
        ".invalid": {
          color: "red",
        },
        // Media queries
        // Note that these apply to the iframe, not the root window.
        "@media screen and (max-width: 400px)": {
          input: {
            color: "orange",
          },
        },
      },
      // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
      isMaskCreditCardNumber: true,
      maskCreditCardNumberRange: {
        beginIndex: 6,
        endIndex: 11,
      },
    });
  } catch (error) {
    console.error("Error:", error);
  }
}

async function get_config() {
  try {
    const response = await fetch("/api/config");
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
}

function onSubmit(event) {
  event.preventDefault();

  const contactName = document.getElementById("contactName").value;
  const contactEmail = document.getElementById("contactEmail").value;
  const contactPhone = document.getElementById("contactPhone").value;

  // 檢查是否有空白輸入
  if (
    contactName.trim() === "" ||
    contactEmail.trim() === "" ||
    contactPhone.trim() === ""
  ) {
    alert("請輸入完整的聯絡資訊");
    return;
  }

  // 驗證格式
  if (!isValidName(contactName)) {
    alert("姓名格式不正確，請輸入中文或英文，至少兩個字元");
    return;
  }

  if (!isValidEmail(contactEmail)) {
    alert("email格式不正確，請輸入正確的email");
    return;
  }

  if (!isValidPhone(contactPhone)) {
    alert("手機號碼格式不正確");
    return;
  }
  //https://toolbox.tw/regexcode/ 正則表達產生器
  //https://regex101.com/ 驗證
  function isValidName(contactName) {
    // 姓名格式驗證，只能是中文、英文或空格，至少兩個字元
    const namePattern = /^[\u4e00-\u9fa5A-Za-z\s]{2,}$/;
    return namePattern.test(contactName);
  }

  function isValidEmail(contactEmail) {
    // email格式驗證
    const emailPattern =
      /\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}/;
    return emailPattern.test(contactEmail);
  }

  function isValidPhone(contactPhone) {
    // 手機格式驗證
    const phonePattern = /^[0-9]{10}$/;
    return phonePattern.test(contactPhone);
  }

  // 取得 TapPay Fields 的 status
  const tappayStatus = TPDirect.card.getTappayFieldsStatus();
  // 確認是否可以 getPrime
  if (tappayStatus.canGetPrime === false) {
    alert("請輸入完整的信用卡資訊");
    return;
  }

  // Get prime
  TPDirect.card.getPrime((result) => {
    if (result.status !== 0) {
      alert("get prime error " + result.msg);
      return;
    }
    //alert("get prime 成功，prime: " + result.card.prime);
    const prime = result.card.prime;

    // 將prime發送到後端API
    sendPrimeToBackend(prime);
  });
}

function sendPrimeToBackend(prime) {
  const contactName = document.getElementById("contactName").value;
  const contactEmail = document.getElementById("contactEmail").value;
  const contactPhone = document.getElementById("contactPhone").value;

  const orderData = {
    prime: prime,
    order: {
      price: bookingData.price,
      trip: {
        attraction: {
          id: bookingData.attractionId,
          name: bookingData.attractionName,
          address: bookingData.attractionAddress,
          image: bookingData.attractionImage,
        },
        date: bookingData.date,
        time: bookingData.time,
      },
      contact: {
        name: contactName,
        email: contactEmail,
        phone: contactPhone,
      },
    },
  };

  const token = localStorage.getItem("token");

  // 使用 Fetch API 發送 POST 請求到後端
  fetch("/api/orders", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(orderData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.data.payment.status === 0) {
        //alert("Payment successful");
        const orderNumber = data.data.number;
        window.location.href = `/thankyou?number=${orderNumber}`;
      } else {
        alert("Payment failed");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
