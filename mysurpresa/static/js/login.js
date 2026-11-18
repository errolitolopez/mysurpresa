// Sends the password to /api/login and opens the admin page when it is right.

const form = document.getElementById("login-form");
const passwordInput = document.getElementById("password");
const button = document.getElementById("login-button");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError("login-error");

  const password = passwordInput.value;
  if (!password) {
    showError("login-error", "Enter the password.");
    return;
  }

  setBusy(button, true);
  try {
    const response = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });

    if (response.ok) {
      const data = await response.json();
      // A temporary password (first login) is changed on the Settings page first.
      window.location.href = data.must_change_password ? "/admin/settings" : "/admin";
      return;
    }
    showError("login-error", await errorText(response));
  } catch {
    showError("login-error", "Cannot reach the server. Check your connection.");
  } finally {
    setBusy(button, false);
    passwordInput.value = "";
    passwordInput.focus();
  }
});
