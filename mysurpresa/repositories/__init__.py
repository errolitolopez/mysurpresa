"""All SQL lives here: one class per table, always with ? parameters."""

from mysurpresa.repositories.items import ItemRepository
from mysurpresa.repositories.parcels import ParcelRepository
from mysurpresa.repositories.photos import PhotoRepository
from mysurpresa.repositories.settings import SettingsRepository

__all__ = ["ItemRepository", "ParcelRepository", "PhotoRepository", "SettingsRepository"]
