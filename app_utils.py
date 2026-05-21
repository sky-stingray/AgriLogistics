INDIAN_CITIES = {
    "Delhi": (28.7041, 77.1025),
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Nagpur": (21.1458, 79.0882),
    "Indore": (22.7196, 75.8577),
    "Bhopal": (23.2599, 77.4126),
    "Patna": (25.5941, 85.1376),
    "Chandigarh": (30.7333, 76.7794)
}

DEFAULT_DESTINATIONS = ["Mumbai", "Pune", "Ahmedabad"]


def get_available_destinations(depot_city):
    """Return the list of possible destination cities excluding the selected depot."""
    return [city for city in INDIAN_CITIES.keys() if city != depot_city]


def get_default_destinations(depot_city, defaults=None):
    """Return valid default selections for the current depot city."""
    if defaults is None:
        defaults = DEFAULT_DESTINATIONS
    available = get_available_destinations(depot_city)
    return [city for city in defaults if city in available]
