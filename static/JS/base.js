// 檢查 JWT token 是否有效
async function checkToken() {
  //取得後端傳過來的token
  const token = localStorage.getItem("token");
  try {
    const response = await fetch("/api/user/auth", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();
    const loginButton = document.getElementById("loginButton");

    if (data !== null) {
      // 使用者已登入，顯示「登出系統」
      loginButton.innerText = "登出系统";
      loginButton.onclick = logout;
    } else {
      // 使用者未登入，顯示「登入/註冊」
      loginButton.innerText = "登入/註冊";
      loginButton.onclick = openSignin;
    }
  } catch (error) {
    console.error("連接錯誤:", error);
  }
}

// 登出
async function logout() {
  const token = localStorage.getItem("token");
  try {
    const response = await fetch("/api/user/auth", {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await response.json();
    if (data["type"] === "success") {
      // 清除 Local Storage 中的 token
      localStorage.removeItem("token");
      // 重新導向到登入頁面
      window.location.reload();
    }
  } catch (error) {
    console.error("連接錯誤:", error);
  }
}
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
/* ---------------------------註冊--------------------------- */
async function submitSignup() {
  const name = document.getElementById("signup-name").value;
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;

  //判斷是否為空白欄位
  //使用 .trim() 方法刪除首、尾空白字符，然後進行比較(否則還是可以輸入空白)
  if (name.trim() == "" || email.trim() == "" || password.trim() == "") {
    alert("註冊欄位不得為空白");
    return; //若空白就跳出，不執行下面程式碼
  }

  // 驗證格式
  if (!isValidName(name)) {
    alert("姓名格式不正確，請輸入中文或英文，至少兩個字元");
    return;
  }

  if (!isValidEmail(email)) {
    alert("email格式不正確，請輸入正確的email");
    return;
  }

  if (!isValidPassword(password)) {
    alert("密碼格式不正確，請輸入英文或數字，至少六個字元");
    return;
  }
  //https://toolbox.tw/regexcode/ 正則表達產生器
  //https://regex101.com/ 驗證
  function isValidName(name) {
    // 姓名格式驗證，只能是中文、英文或空格，至少兩個字元
    const namePattern = /^[\u4e00-\u9fa5A-Za-z\s]{2,}$/;
    return namePattern.test(name);
  }

  function isValidEmail(email) {
    // email格式驗證
    const emailPattern =
      /\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}/;
    return emailPattern.test(email);
  }

  function isValidPassword(password) {
    // 密碼格式驗證，只能是英文或數字，至少六個字元
    const passwordPattern = /^[A-Za-z0-9]{6,}$/;
    return passwordPattern.test(password);
  }

  //將要重送到後端的值，用物件（字典）打包起來
  const requestData = {
    name: name,
    email: email,
    password: password,
  };

  try {
    const response = await fetch("/api/user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    const data = await response.json();
    if (data["ok"] == true) {
      document.getElementById("signup-message").innerText = "註冊成功";
      document.getElementById("signup-message").style.color = "green";
    } else {
      document.getElementById("signup-message").innerText = data["message"];
      document.getElementById("signup-message").style.color = "red";
    }
  } catch (error) {
    console.error("連接錯誤:", error);
  }
}

/* ---------------------------登入--------------------------- */
async function submitSignin() {
  const email = document.getElementById("signin-email").value;
  const password = document.getElementById("signin-password").value;

  if (email.trim() == "" || password.trim() == "") {
    alert("登入欄位不得為空白");
    return;
  }

  if (!isValidEmail(email)) {
    alert("email格式不正確，請輸入正確的email");
    return;
  }

  if (!isValidPassword(password)) {
    alert("密碼格式不正確，請輸入英文或數字，至少六個字元");
    return;
  }

  function isValidEmail(email) {
    // email格式驗證
    const emailPattern =
      /\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}/;
    return emailPattern.test(email);
  }

  function isValidPassword(password) {
    // 密碼格式驗證，只能是英文或數字，至少六個字元
    const passwordPattern = /^[A-Za-z0-9]{6,}$/;
    return passwordPattern.test(password);
  }

  const requestData = {
    email: email,
    password: password,
  };

  try {
    const response = await fetch("/api/user/auth", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    const data = await response.json();
    if (data["token"] == null) {
      // 登入失敗
      document.getElementById("signin-message").innerText = data["message"];
      document.getElementById("signin-message").style.color = "red";
    } else {
      // 將 token 儲存到 Local Storage
      localStorage.setItem("token", data["token"]);

      //登入成功重新載入頁面
      window.location.reload();
    }
  } catch (error) {
    console.error("連接錯誤:", error);
  }
}
