"""Fixed values used throughout the application."""

ADMIN_PASSWORD = "admin123"  # Demo-only password for the project administrator.

ECO_ACTIONS = {
    "Recycled campus waste": 10,
    "Walked or cycled to class": 15,
    "Used a reusable bottle": 5,
    "Turned off unused devices": 8,
    "Joined a campus clean-up": 25,
    "Used public transport to campus": 12,
}

ACTION_ICONS = {
    "Recycled campus waste": "♻",
    "Walked or cycled to class": "🚲",
    "Used a reusable bottle": "💧",
    "Turned off unused devices": "💡",
    "Joined a campus clean-up": "🧹",
    "Used public transport to campus": "🚌",
}

IMAGE_FILE_TYPES = [
    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
    ("All files", "*.*"),
]

VALID_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
