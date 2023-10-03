window.onload = async function () {
  const isLoggedIn = await checkToken();
  if (!isLoggedIn) {
    window.location.href = "/"; // 沒登錄就回首頁
  } else {
    get_order();
  }
};

function get_order() {
  //取得URL要求字串
  const urlParams = new URLSearchParams(window.location.search);
  const orderNumber = urlParams.get("number");

  const token = localStorage.getItem("token");
  fetch(`/api/order/${orderNumber}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      const orderNumberElement = document.getElementById("orderNumber");

      // 檢查是否有訂單編號
      if (data.data) {
        orderNumberElement.textContent = data.data.number;
      } else {
        document.getElementById("successMessage").textContent = ""; // 清空行程預定成功消息
        document.getElementById("order").textContent = ""; // 清空訂單資訊
        document.getElementById("orderInfo").textContent = ""; // 清空訂單資訊
        document.getElementById("order").textContent = "查無任何訂單編號";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
