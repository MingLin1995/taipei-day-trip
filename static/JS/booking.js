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
  }
};

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
      if (data != null) {
        console.log("刪除失敗");
      } else {
        console.log(data);
        window.location.reload(); //刪除訂單資訊後重新整理頁面
      }
    })
    .catch((error) => {
      console.error(error);
    });
}
