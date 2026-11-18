// Admin items page: counts, the item list with filters, adding an item, and the parcels.

const itemsList = document.getElementById("items-list");
const parcelsList = document.getElementById("parcels-list");
const statusFilter = document.getElementById("status-filter");
const parcelFilter = document.getElementById("parcel-filter");

const itemForm = document.getElementById("item-form");
const itemModal = new bootstrap.Modal("#item-modal");
const itemSave = document.getElementById("item-save");

const parcelForm = document.getElementById("parcel-form");
const parcelModalElement = document.getElementById("parcel-modal");
const parcelModal = new bootstrap.Modal(parcelModalElement);
const parcelSave = document.getElementById("parcel-save");
const parcelDelete = document.getElementById("parcel-delete");

let parcels = [];
let editingParcelId = null; // null when adding a new parcel

// itemRow(item) -> a list row: photo, name, price, parcel, status; tap to edit
const itemRow = (item) => {
  const row = makeElement("a", "list-group-item list-group-item-action d-flex align-items-center gap-3");
  row.href = `/admin/items/${item.id}`;

  if (item.thumb_url) {
    const image = makeElement("img", "thumb-sm");
    image.src = item.thumb_url;
    image.alt = "";
    image.loading = "lazy";
    row.append(image);
  } else {
    row.append(makeElement("span", "thumb-sm item-photo-empty bi bi-camera fs-5"));
  }

  const text = makeElement("div", "flex-grow-1 min-w-0");
  text.append(makeElement("div", "fw-semibold text-truncate", item.name));
  const details = [formatPeso(item.price)];
  if (item.parcel_name) details.push(item.parcel_name);
  if (item.photo_count === 0) details.push("no photos");
  text.append(makeElement("div", "small text-body-secondary text-truncate", details.join(" · ")));
  row.append(text, statusBadge(item.status));
  return row;
};

// loadItems() -> fills the counts and the list, following the two filters
const loadItems = async () => {
  hideError("items-error");
  const query = new URLSearchParams();
  if (statusFilter.value) query.set("status", statusFilter.value);
  if (parcelFilter.value) query.set("parcel_id", parcelFilter.value);
  try {
    const response = await apiFetch(`/api/items?${query}`);
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    const data = await response.json();

    Object.entries(data.counts).forEach(([status, count]) => {
      document.querySelector(`[data-count="${status}"]`).textContent = count;
    });
    const rows = data.items.map(itemRow);
    itemsList.replaceChildren(...(rows.length ? rows : [messageItem("No items here yet.")]));
  } catch (error) {
    showError("items-error", error.message || "Could not load the items.");
  }
};

// parcelRow(parcel) -> a list row: name, date, items sold, money in vs cost; tap to edit
const parcelRow = (parcel) => {
  const row = makeElement("button", "list-group-item list-group-item-action text-start");
  row.type = "button";

  const top = makeElement("div", "d-flex justify-content-between gap-2");
  top.append(makeElement("span", "fw-semibold text-truncate", parcel.name));
  top.append(makeElement("span", "small text-body-secondary text-nowrap", parcel.bought_on || ""));
  row.append(top);

  const parts = [`${parcel.sold_count} of ${parcel.item_count} sold`, `${formatPeso(parcel.sold_total)} in`];
  if (parcel.cost !== null) {
    parts.push(`cost ${formatPeso(parcel.cost)}`);
    const profit = parcel.sold_total - parcel.cost;
    parts.push(profit >= 0 ? `profit ${formatPeso(profit)}` : `${formatPeso(-profit)} to go`);
  }
  row.append(makeElement("div", "small text-body-secondary", parts.join(" · ")));
  row.addEventListener("click", () => openParcel(parcel));
  return row;
};

// loadParcels() -> fills the parcel list, the parcel filter and the parcel select in the add form
const loadParcels = async () => {
  hideError("parcels-error");
  try {
    const response = await apiFetch("/api/parcels");
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    parcels = (await response.json()).parcels;

    const rows = parcels.map(parcelRow);
    parcelsList.replaceChildren(...(rows.length ? rows : [messageItem("No parcels yet. Add one to keep track of what each parcel earned.")]));

    const selected = parcelFilter.value;
    parcelFilter.replaceChildren(new Option("All parcels", ""),
      ...parcels.map((parcel) => new Option(parcel.name, parcel.id)));
    parcelFilter.value = parcels.some((parcel) => String(parcel.id) === selected) ? selected : "";
    fillParcelSelects(parcels, parcels[0]?.id);
  } catch (error) {
    showError("parcels-error", error.message || "Could not load the parcels.");
  }
};

// --- add an item, then go to its page to add photos ---

itemForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError("item-error");
  const price = toCentavos(document.getElementById("item-price").value);
  if (price === null || Number.isNaN(price)) {
    showError("item-error", "Enter a price, e.g. 250.");
    return;
  }
  const parcelValue = document.getElementById("item-parcel").value;
  setBusy(itemSave, true);
  try {
    const response = await sendJson("/api/items", "POST", {
      name: document.getElementById("item-name").value,
      price,
      parcel_id: parcelValue ? Number(parcelValue) : null,
      status: "draft",
    });
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    const { item } = await response.json();
    window.location.href = `/admin/items/${item.id}`;
  } catch (error) {
    showError("item-error", error.message || "Could not add the item.");
    setBusy(itemSave, false);
  }
});

document.getElementById("item-modal").addEventListener("shown.bs.modal", () => {
  document.getElementById("item-name").focus();
});

// --- parcels: add, edit, delete ---

// openParcel(parcel) -> the parcel form filled in; openParcel(null) -> an empty form to add one
const openParcel = (parcel) => {
  editingParcelId = parcel ? parcel.id : null;
  hideError("parcel-error");
  document.getElementById("parcel-modal-title").textContent = parcel ? "Edit parcel" : "Add parcel";
  document.getElementById("parcel-name").value = parcel?.name ?? "";
  document.getElementById("parcel-cost").value = toPesoInput(parcel?.cost ?? null);
  document.getElementById("parcel-date").value = parcel?.bought_on ?? "";
  document.getElementById("parcel-note").value = parcel?.note ?? "";
  parcelDelete.classList.toggle("d-none", !parcel);
  parcelModal.show();
};

document.getElementById("add-parcel-button").addEventListener("click", () => openParcel(null));

parcelModalElement.addEventListener("shown.bs.modal", () => {
  document.getElementById("parcel-name").focus();
});

parcelForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError("parcel-error");
  const cost = toCentavos(document.getElementById("parcel-cost").value);
  if (Number.isNaN(cost)) {
    showError("parcel-error", "Cost must be a number, e.g. 1500.");
    return;
  }
  setBusy(parcelSave, true);
  try {
    const data = {
      name: document.getElementById("parcel-name").value,
      cost,
      bought_on: document.getElementById("parcel-date").value,
      note: document.getElementById("parcel-note").value,
    };
    const response = editingParcelId
      ? await sendJson(`/api/parcels/${editingParcelId}`, "PUT", data)
      : await sendJson("/api/parcels", "POST", data);
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    parcelModal.hide();
    await loadParcels();
    await loadItems();
  } catch (error) {
    showError("parcel-error", error.message || "Could not save the parcel.");
  } finally {
    setBusy(parcelSave, false);
  }
});

parcelDelete.addEventListener("click", async () => {
  if (!window.confirm("Delete this parcel? Its items are kept, without a parcel.")) return;
  setBusy(parcelDelete, true);
  try {
    const response = await apiFetch(`/api/parcels/${editingParcelId}`, { method: "DELETE" });
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    parcelModal.hide();
    await loadParcels();
    await loadItems();
  } catch (error) {
    showError("parcel-error", error.message || "Could not delete the parcel.");
  } finally {
    setBusy(parcelDelete, false);
  }
});

statusFilter.addEventListener("change", loadItems);
parcelFilter.addEventListener("change", loadItems);

loadParcels().then(loadItems);
