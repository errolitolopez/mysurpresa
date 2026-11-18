#!/usr/bin/env bash
# Draws the Facebook Page profile photos (1080 x 1080 PNG) from profile-photo.html with Chrome.
#   profile-photo.png            the icon only (best: Facebook shows the Page name next to it)
#   profile-photo-with-name.png  the icon with "MySurpresa" under it
set -e
cd "$(dirname "$0")"
profile=$(mktemp -d)
for variant in "" "name"; do
  out="profile-photo${variant:+-with-name}.png"
  google-chrome --headless=new --disable-gpu --no-sandbox --hide-scrollbars --user-data-dir="$profile" \
    --virtual-time-budget=5000 --window-size=1080,1080 --screenshot="$PWD/$out" \
    "file://$PWD/profile-photo.html${variant:+#$variant}" 2>/dev/null
  echo "Saved $out"
done
rm -rf "$profile"
