// Item page: the Share and Copy link buttons. (Facebook and Messenger are plain links.)

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
