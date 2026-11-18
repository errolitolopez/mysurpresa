// Admin item page: the photos (add, make cover, delete) and the details (name, price, status...).

const itemId = document.getElementById("item-page").dataset.itemId;
const MAX_PHOTOS = 10;

const photosGrid = document.getElementById("photos-grid");
const photoInput = document.getElementById("photo-input");
const photoPick = document.getElementById("photo-pick");
const photoProgress = document.getElementById("photo-progress");
const detailsForm = document.getElementById("details-form");
const saveButton = document.getElementById("save-button");
const deleteButton = document.getElementById("delete-button");

// --- photos ---

// photoTile(photo, isCover) -> a square photo with "Cover" / "Make cover" and a delete button
const photoTile = (photo, isCover) => {
  const column = makeElement("div", "col");
  const card = makeElement("div", "card overflow-hidden h-100");
  const image = makeElement("img", "item-photo");
  image.src = photo.thumb_url;
  image.alt = isCover ? "Cover photo" : "Photo";
  card.append(image);

  const buttons = makeElement("div", "d-flex");
  if (isCover) {
    buttons.append(makeElement("span", "badge text-bg-primary rounded-0 flex-fill py-2", "Cover"));
  } else {
    const coverButton = makeElement("button", "btn btn-sm btn-link flex-fill text-decoration-none", "Make cover");
    coverButton.type = "button";
    coverButton.addEventListener("click", () => photoAction(`/api/photos/${photo.id}/cover`, "POST", coverButton));
    buttons.append(coverButton);
  }
  const removeButton = makeElement("button", "btn btn-sm btn-link text-danger bi bi-trash");
  removeButton.type = "button";
  removeButton.setAttribute("aria-label", "Delete photo");
  removeButton.addEventListener("click", () => {
    if (window.confirm("Delete this photo?")) {
      photoAction(`/api/photos/${photo.id}`, "DELETE", removeButton);
    }
  });
  buttons.append(removeButton);
  card.append(buttons);
  column.append(card);
  return column;
};

// showPhotos(photos) -> draws the grid and the "3 / 10" count
let photoCount = 0;
const showPhotos = (photos) => {
  photoCount = photos.length;
  photosGrid.replaceChildren(...photos.map((photo, index) => photoTile(photo, index === 0)));
  document.getElementById("photos-empty").classList.toggle("d-none", photos.length > 0);
  document.getElementById("photo-count").textContent = `${photos.length} / ${MAX_PHOTOS}`;
  photoPick.classList.toggle("disabled", photos.length >= MAX_PHOTOS);
};

const loadPhotos = async () => {
  try {
    const response = await apiFetch(`/api/items/${itemId}/photos`);
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    showPhotos((await response.json()).photos);
  } catch (error) {
    showError("photos-error", error.message || "Could not load the photos.");
  }
};

// photoAction("/api/photos/4/cover", "POST", button) -> does it, then reloads the photos
const photoAction = async (url, method, button) => {
  hideError("photos-error");
  setBusy(button, true);
  try {
    const response = await apiFetch(url, { method });
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    await loadPhotos();
  } catch (error) {
    showError("photos-error", error.message || "Something went wrong. Try again.");
    setBusy(button, false);
  }
};

// Photos go up one at a time: a phone on slow data can show progress, and one bad photo
// doesn't stop the others.
photoInput.addEventListener("change", async () => {
  hideError("photos-error");
  const files = [...photoInput.files].slice(0, MAX_PHOTOS - photoCount);
  photoInput.value = "";
  if (!files.length) return;

  const failed = [];
  photoPick.classList.add("disabled");
  photoProgress.classList.remove("d-none");
  for (const [index, file] of files.entries()) {
    photoProgress.textContent = `Uploading photo ${index + 1} of ${files.length}...`;
    const body = new FormData();
    body.append("photo", file);
    try {
      const response = await apiFetch(`/api/items/${itemId}/photos`, { method: "POST", body });
      if (!response) return;
      if (!response.ok) failed.push(`${file.name}: ${await errorText(response)}`);
    } catch {
      failed.push(`${file.name}: could not reach the server.`);
    }
  }
  photoProgress.classList.add("d-none");
  if (failed.length) showError("photos-error", failed.join(" "));
  await loadPhotos();
});

// --- details ---

const loadDetails = async () => {
  try {
    const [itemResponse, parcelsResponse] = await Promise.all([
      apiFetch(`/api/items/${itemId}`),
      apiFetch("/api/parcels"),
    ]);
    if (!itemResponse || !parcelsResponse) return;
    if (!itemResponse.ok) throw new Error(await errorText(itemResponse));
    if (!parcelsResponse.ok) throw new Error(await errorText(parcelsResponse));
    const { item } = await itemResponse.json();
    const { parcels } = await parcelsResponse.json();

    document.getElementById("name").value = item.name;
    document.getElementById("price").value = toPesoInput(item.price);
    document.getElementById("status").value = item.status;
    document.getElementById("description").value = item.description;
    fillParcelSelects(parcels, item.parcel_id);
  } catch (error) {
    showError("details-error", error.message || "Could not load the item.");
  }
};

detailsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError("details-error");
  const price = toCentavos(document.getElementById("price").value);
  if (price === null || Number.isNaN(price)) {
    showError("details-error", "Enter a price, e.g. 250.");
    return;
  }
  const status = document.getElementById("status").value;
  if (status !== "draft" && photoCount === 0
      && !window.confirm("This item has no photos yet. Show it in the shop anyway?")) {
    return;
  }
  const parcelValue = document.getElementById("parcel").value;
  setBusy(saveButton, true);
  try {
    const response = await sendJson(`/api/items/${itemId}`, "PUT", {
      name: document.getElementById("name").value,
      price,
      status,
      parcel_id: parcelValue ? Number(parcelValue) : null,
      description: document.getElementById("description").value,
    });
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    flash("details-saved");
  } catch (error) {
    showError("details-error", error.message || "Could not save the item.");
  } finally {
    setBusy(saveButton, false);
  }
});

deleteButton.addEventListener("click", async () => {
  if (!window.confirm("Delete this item and all its photos? This can't be undone.")) return;
  hideError("details-error");
  setBusy(deleteButton, true);
  try {
    const response = await apiFetch(`/api/items/${itemId}`, { method: "DELETE" });
    if (!response) return;
    if (!response.ok) throw new Error(await errorText(response));
    window.location.href = "/admin";
  } catch (error) {
    showError("details-error", error.message || "Could not delete the item.");
    setBusy(deleteButton, false);
  }
});

loadPhotos();
loadDetails();
