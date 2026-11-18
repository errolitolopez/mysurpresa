// Helpers shared by the admin pages (and the login page).

const pesoFormat = new Intl.NumberFormat("en-PH", { style: "currency", currency: "PHP" });

// Prices from the server are in centavos (125000 = ₱1,250.00).
// formatPeso(125000) -> "₱1,250.00"
const formatPeso = (centavos) => pesoFormat.format(centavos / 100);

// toCentavos("1250.5") -> 125050; toCentavos("") -> null
const toCentavos = (text) => {
  if (String(text).trim() === "") return null;
  const value = Number(text);
  return Number.isFinite(value) ? Math.round(value * 100) : NaN;
};

// toPesoInput(125050) -> "1250.50" (the value for a number input); toPesoInput(null) -> ""
const toPesoInput = (centavos) => (centavos === null ? "" : (centavos / 100).toFixed(2));

// showError("items-error", "Could not load items.") -> fills that error box and shows it
const showError = (elementId, message) => {
  const box = document.getElementById(elementId);
  box.textContent = message;
  box.classList.remove("d-none");
};

// hideError("items-error") -> hides that box
const hideError = (elementId) => {
  document.getElementById(elementId).classList.add("d-none");
};

// flash("details-saved") -> shows the box for 2 seconds
const flash = (elementId) => {
  const box = document.getElementById(elementId);
  box.classList.remove("d-none");
  setTimeout(() => box.classList.add("d-none"), 2000);
};

// fetch() for the admin API. Sends X-Requested-With (the server refuses changes without it,
// see web/security.py) and goes back to the login page when the session has ended.
// Returns null in that case, so callers can simply stop: if (!response) return;
// apiFetch("/api/items") -> the response, or null
const apiFetch = async (url, options = {}) => {
  const headers = { "X-Requested-With": "fetch", ...(options.headers || {}) };
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    window.location.href = "/login";
    return null;
  }
  return response;
};

// sendJson("/api/items", "POST", { name: "Bag" }) -> the response, or null (see apiFetch)
const sendJson = (url, method, data) => apiFetch(url, {
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});

// errorText(response) -> the server's "error" message, or a general one
const errorText = async (response) => {
  try {
    const data = await response.json();
    return data.error || "Something went wrong. Try again.";
  } catch {
    return "Something went wrong. Try again.";
  }
};

// makeElement("span", "fw-semibold", "Hi") -> <span class="fw-semibold">Hi</span>
// textContent is used (not innerHTML) so names can't inject HTML.
const makeElement = (tag, className, text) => {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
};

// messageItem("No items yet.") -> a grey list row, for an empty list or a message
const messageItem = (text) => makeElement("div", "list-group-item text-body-secondary", text);

// setBusy(saveButton, true) -> the button is disabled and shows a spinner; setBusy(saveButton, false) restores it
const setBusy = (button, busy) => {
  button.disabled = busy;
  button.querySelector(".spinner-border")?.remove();
  if (busy) {
    const spinner = makeElement("span", "spinner-border spinner-border-sm me-2");
    spinner.setAttribute("aria-hidden", "true");
    button.prepend(spinner);
  }
};

const STATUS_BADGES = {
  available: ["text-bg-success", "Available"],
  reserved: ["text-bg-warning", "Reserved"],
  sold: ["text-bg-secondary", "Sold"],
  draft: ["text-bg-light border", "Draft"],
};

// statusBadge("sold") -> <span class="badge text-bg-secondary">Sold</span>
const statusBadge = (status) => {
  const [className, label] = STATUS_BADGES[status];
  return makeElement("span", `badge ${className}`, label);
};

// fillParcelSelects(parcels, 3) -> every <select data-parcel-select> lists the parcels, 3 selected
const fillParcelSelects = (parcels, selectedId) => {
  document.querySelectorAll("[data-parcel-select]").forEach((select) => {
    const options = [new Option("No parcel", "")];
    parcels.forEach((parcel) => options.push(new Option(parcel.name, parcel.id)));
    select.replaceChildren(...options);
    select.value = selectedId ?? "";
  });
};

// The logout button is in the admin navbar, which the login page doesn't have.
document.getElementById("logout-button")?.addEventListener("click", async () => {
  await apiFetch("/api/logout", { method: "POST" });
  window.location.href = "/";
});
