// Admin settings page: the shop's name, tagline, Messenger username, Facebook page, and the password.

const shopForm = document.getElementById("shop-form");
const shopSave = document.getElementById("shop-save");
const passwordForm = document.getElementById("password-form");
const passwordSave = document.getElementById("password-save");

const FIELDS = {
  shop_name: "shop-name",
  tagline: "tagline",
  messenger_username: "messenger",
  facebook_url: "facebook",
};

// fillShopForm({shop_name: "MySurpresa", ...}) -> puts each setting in its input
const fillShopForm = (settings) => {
  Object.entries(FIELDS).forEach(([key, id]) => {
    document.getElementById(id).value = settings[key];
  });
};

const loadSettings = async () => {
  hideError("shop-error");
  try {
    const response = await apiFetch("/api/settings");
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    fillShopForm((await response.json()).settings);
  } catch (error) {
    showError("shop-error", error.message || "Could not load the settings.");
  }
};

shopForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError("shop-error");
  const data = {};
  Object.entries(FIELDS).forEach(([key, id]) => {
    data[key] = document.getElementById(id).value;
  });
  setBusy(shopSave, true);
  try {
    const response = await sendJson("/api/settings", "PUT", data);
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    // Show the cleaned values, e.g. a pasted m.me link becomes just the username.
    fillShopForm((await response.json()).settings);
    flash("shop-saved");
  } catch (error) {
    showError("shop-error", error.message || "Could not save the settings.");
  } finally {
    setBusy(shopSave, false);
  }
});

passwordForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError("password-error");
  setBusy(passwordSave, true);
  try {
    const response = await sendJson("/api/password", "POST", {
      current_password: document.getElementById("current-password").value,
      new_password: document.getElementById("new-password").value,
      confirm_password: document.getElementById("confirm-password").value,
    });
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    passwordForm.reset();
    flash("password-saved");
  } catch (error) {
    showError("password-error", error.message || "Could not change the password.");
  } finally {
    setBusy(passwordSave, false);
  }
});

loadSettings();
