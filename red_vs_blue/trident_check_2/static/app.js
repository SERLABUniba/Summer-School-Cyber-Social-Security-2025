document.addEventListener("DOMContentLoaded", () => {
  const consoleBox = document.getElementById("console");
  if (consoleBox) {
    consoleBox.scrollTop = consoleBox.scrollHeight;
  }
});