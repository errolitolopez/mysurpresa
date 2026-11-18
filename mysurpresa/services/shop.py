"""The shop's settings (name, tagline, Messenger username, Facebook page)."""

from mysurpresa.domain.shop import DEFAULTS, clean_shop_settings
from mysurpresa.services.base import Service


class ShopService(Service):
    def get(self):
        """Every shop setting; a setting never saved has its default value."""
        return {key: self.settings.get(key) or default for key, default in DEFAULTS.items()}

    def save(self, data):
        """Check and save every shop setting. Returns the saved values."""
        values = clean_shop_settings(data)
        for key, value in values.items():
            self.settings.set(key, value)
        self.commit()
        return self.get()
