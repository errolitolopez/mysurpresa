// Colour theme (copied from myguro). Loaded in <head> so the theme is set before the page is drawn (no flash).
// "auto" follows the device; a person's choice is kept in this browser only.
// Only Bootstrap's light and dark mode (data-bs-theme); myguro's named themes are left out.

(function () {
  const KEY = "mysurpresa-theme";
  const CHOICES = ["auto", "light", "dark"];
  const dark = window.matchMedia("(prefers-color-scheme: dark)");

  function saved() {
    try {
      const value = localStorage.getItem(KEY);
      return CHOICES.includes(value) ? value : "auto";
    } catch {
      return "auto";
    }
  }

  function apply(choice) {
    const theme = choice === "auto" ? (dark.matches ? "dark" : "light") : choice;
    document.documentElement.setAttribute("data-bs-theme", theme);
  }

  // No colour animation while the first theme is applied (removed once the page has loaded).
  document.documentElement.classList.add("preload");
  window.addEventListener("load", () => {
    requestAnimationFrame(() => document.documentElement.classList.remove("preload"));
  });

  apply(saved());
  dark.addEventListener("change", () => apply(saved()));

  // Saves a choice, draws it, and brings every picker on the page (the navbar menu)
  // in line with it.
  function choose(choice) {
    choice = CHOICES.includes(choice) ? choice : "auto";
    try {
      localStorage.setItem(KEY, choice);
    } catch {
      // Private window or blocked storage: the choice only lasts for this page.
    }
    apply(choice);
    showChoice(choice);
  }

  function showChoice(choice) {
    document.querySelectorAll("[data-theme-select]").forEach((select) => (select.value = choice));
    document.querySelectorAll("[data-theme-choice]").forEach((button) => {
      const current = button.dataset.themeChoice === choice;
      button.classList.toggle("active", current);
      button.setAttribute("aria-current", current ? "true" : "false");
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    showChoice(saved());
    document.querySelectorAll("[data-theme-select]").forEach((select) => {
      select.addEventListener("change", () => choose(select.value));
    });
    // The quick menu in the navbar: one button per theme.
    document.querySelectorAll("[data-theme-choice]").forEach((button) => {
      button.addEventListener("click", () => choose(button.dataset.themeChoice));
    });
  });
})();
