// save dark mode preference
const darkMode = localStorage.getItem("darkMode");
if (darkMode == "enabled") {
  document.body.classList.add("dark-mode");
}

const passwordInput = document.getElementById("password");
function addNumber(number) {
  // delete last character if x is pressed
  if (number == "x") {
    passwordInput.value = passwordInput.value.slice(0, -1);
    return;
  } else if (number == "✓") {
    unlockDoor(passwordInput.value);
    passwordInput.value = "";
    return;
  } else {
    passwordInput.value += number;
  }
}

function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  if (darkMode == "enabled") {
    localStorage.setItem("darkMode", null);
  } else {
    localStorage.setItem("darkMode", "enabled");
  }
}
