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
