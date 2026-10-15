"""Keyword-rule baseline: guess an expense category from the description.

No machine learning. If a keyword shows up in the description, we pick that category.
This is the "score to beat" for the machine learning model we build later.
"""

import re

# What we return when no keyword matches
UNKNOWN = "unknown"

# Each category has a list of keywords (all lowercase)
KEYWORDS = {
    "equipment": [
        "camera", "lens", "tripod", "flash", "speedlight", "battery", "memory card",
        "light panel", "light stand", "softbox", "gimbal", "filter", "drone",
    ],
    "software": [
        "adobe", "lightroom", "pixieset", "dropbox", "google workspace", "quickbooks",
        "squarespace", "canva", "zoom", "capture one", "godaddy", "domain", "backblaze",
        "subscription", "license",
    ],
    "marketing": [
        "ads", "vistaprint", "business cards", "flyers", "banner", "postcards",
        "stickers", "booth", "expo", "thumbtack", "giveaway", "sponsor", "tote",
        "referral", "directory",
    ],
    "travel": [
        "uber", "lyft", "gas", "parking", "hotel", "flight", "toll", "rental car",
        "southwest", "airline",
    ],
    "office supplies": [
        "paper", "ink", "pens", "notebooks", "envelopes", "folders", "binders",
        "sticky", "tape", "organizer", "packaging", "stapler",
    ],
}


def _clean(text):
    """Lowercase the text and keep only letters and numbers, with spaces around each word.
    Example: "Buc-ee's" becomes " buc ee s ", so keywords only match whole words."""
    return " " + re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip() + " "


def predict_category(description):
    """Return the category whose keywords match the description most often.
    If nothing matches, return "unknown"."""
    text = _clean(description)
    best_category = UNKNOWN
    best_score = 0
    for category, keywords in KEYWORDS.items():
        # Count how many of this category's keywords appear as whole words
        score = sum(1 for keyword in keywords if f" {keyword} " in text)
        if score > best_score:
            best_category = category
            best_score = score
    return best_category