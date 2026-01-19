"""Geocoding Service.

Converts addresses to coordinates using various providers.
"""

from typing import Optional, Tuple
from geopy.geocoders import Nominatim, GoogleV3

from config.settings import get_settings
from utils.logger import get_logger


class GeocodingService:
    """Service for address geocoding and reverse geocoding."""
    
    def __init__(self, provider: str = None) -> None:
        settings = get_settings()
        self.provider_name = provider or settings.geocoding_provider
        self.logger = get_logger("service.geocoding")
        
        if self.provider_name == "google":
            self.geocoder = GoogleV3(api_key=settings.google_maps_api_key)
        else:
            # Default to Nominatim (OpenStreetMap)
            self.geocoder = Nominatim(user_agent=settings.geocoding_user_agent)
            
        self.logger.info(f"Initialized geocoding with provider: {self.provider_name}")

    async def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """Convert address string to (latitude, longitude)."""
        try:
            # Note: geopy is synchronous, wrap in executor in production if needed
            location = self.geocoder.geocode(address)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            self.logger.error(f"Geocoding failed for '{address}': {str(e)}")
            
        return None

    async def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """Convert coordinates to a readable address."""
        try:
            location = self.geocoder.reverse((lat, lon))
            if location:
                return location.address
        except Exception as e:
            self.logger.error(f"Reverse geocoding failed for {lat}, {lon}: {str(e)}")
            
        return None
