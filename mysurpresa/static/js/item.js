// Item page: full screen photos, and the Share and Copy link buttons. (Facebook and Messenger are plain links.)

const shareButton = document.getElementById("share-button");
const copyButton = document.getElementById("copy-button");

// showDone(copyButton, "Copied!") -> the button says "Copied!" for 2 seconds
const showDone = (button, text) => {
  const original = button.textContent;
  button.textContent = text;
  setTimeout(() => { button.textContent = original; }, 2000);
};

// copyLink("https://...") -> true when the link is on the clipboard
const copyLink = async (url) => {
  try {
    await navigator.clipboard.writeText(url);
    return true;
  } catch {
    // Old browser or not https: let the person copy it by hand.
    window.prompt("Copy this link:", url);
    return false;
  }
};

// On phones, navigator.share opens the share sheet: Messenger, Facebook, Viber, SMS...
// Computers without it copy the link instead.
shareButton.addEventListener("click", async () => {
  const { url, title } = shareButton.dataset;
  if (navigator.share) {
    try {
      await navigator.share({ title, url });
    } catch {
      // The person closed the share sheet: nothing to do.
    }
    return;
  }
  if (await copyLink(url)) showDone(shareButton, "Link copied!");
});

copyButton.addEventListener("click", async () => {
  if (await copyLink(copyButton.dataset.url)) showDone(copyButton, "Copied!");
});

// --- Full screen photos (like mytee's full screen button) ---
// Where the browser can make a part of the page full screen (Android, computers), the photos get the
// real full screen: no browser bar, no phone status bar. iPhone Safari can't, so there the photos
// cover the page instead (.is-fullscreen in glass.css). Swipe or the arrows still change the photo.

const gallery = document.getElementById("gallery");
const fullscreenButton = document.getElementById("fullscreen-toggle");

// isFullscreen() -> true while the photos fill the screen, either way
const isFullscreen = () => Boolean(document.fullscreenElement) || gallery.classList.contains("is-fullscreen");

// showFullscreenButton(true) -> the button shows "exit"; its name is for tooltips and screen readers
const showFullscreenButton = (on) => {
  fullscreenButton.querySelector("i").className = on ? "bi bi-fullscreen-exit" : "bi bi-arrows-fullscreen";
  const label = on ? "Exit full screen" : "Full screen";
  fullscreenButton.setAttribute("aria-label", label);
  fullscreenButton.title = label;
};

const openFullscreen = () => {
  if (document.fullscreenEnabled) {
    gallery.requestFullscreen().catch(() => {
      // Refused (e.g. inside an app's own browser): cover the page instead.
      gallery.classList.add("is-fullscreen");
      showFullscreenButton(true);
    });
    return;
  }
  gallery.classList.add("is-fullscreen");
  showFullscreenButton(true);
};

const closeFullscreen = () => {
  if (document.fullscreenElement) {
    document.exitFullscreen();
    return;
  }
  gallery.classList.remove("is-fullscreen");
  showFullscreenButton(false);
};

if (gallery) {
  fullscreenButton.addEventListener("click", () => (isFullscreen() ? closeFullscreen() : openFullscreen()));
  // Tapping the photo itself opens or closes it too. A swipe to the next photo is not a tap (no click).
  gallery.querySelectorAll(".carousel-item img").forEach((image) => {
    image.addEventListener("click", () => (isFullscreen() ? closeFullscreen() : openFullscreen()));
  });
  // The browser's own full screen ends with Esc or the phone's back gesture too: keep the button right.
  document.addEventListener("fullscreenchange", () => showFullscreenButton(Boolean(document.fullscreenElement)));
  // Esc closes the cover-the-page full screen (the real one closes by itself), and the arrow keys change photo.
  document.addEventListener("keydown", (event) => {
    if (!isFullscreen()) return;
    if (event.key === "Escape") closeFullscreen();
    // Bootstrap already changes photo with the arrows while the carousel has focus: don't do it twice.
    if (gallery.contains(document.activeElement)) return;
    const carousel = bootstrap.Carousel.getOrCreateInstance(gallery);
    if (event.key === "ArrowLeft") carousel.prev();
    if (event.key === "ArrowRight") carousel.next();
  });
}
