document.addEventListener("DOMContentLoaded", function () {
  const themeToggle = document.getElementById("themeToggle");
  const savedTheme = localStorage.getItem("siteTheme");

  function setTheme(theme) {
    const isDark = theme === "dark";

    document.body.classList.toggle("dark-mode", isDark);

    if (themeToggle) {
      themeToggle.innerHTML = isDark ? '<i class="bx bx-sun"></i>' : '<i class="bx bx-moon"></i>';
      themeToggle.setAttribute("aria-label", isDark ? "Activer le mode jour" : "Activer le mode nuit");
    }
  }

  setTheme(savedTheme === "dark" ? "dark" : "light");

  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      const nextTheme = document.body.classList.contains("dark-mode") ? "light" : "dark";

      localStorage.setItem("siteTheme", nextTheme);
      setTheme(nextTheme);
    });
  }
});
